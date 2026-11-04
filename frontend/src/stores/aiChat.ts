/**
 * AI 对话运行状态仓库（pinia，全局生命周期）。
 *
 * 核心设计（qm 式 run 架构的前端侧）：
 * - 每条消息 = 一个后台 run；store 持有 SSE 订阅与流式内容，
 *   **不随页面组件卸载而销毁**——切页面/切路由后生成继续，
 *   回到页面时直接呈现 store 里的最新内容（或从服务端恢复）。
 * - 同会话连发消息自动排队（后端 FIFO）：sessionQueue 记录排队 run，
 *   活跃 run 终态后自动接管下一个。
 * - 网络中断自动重连（指数退避），恢复时以服务端快照为基线续流。
 */
import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import {
  createChatRun,
  getActiveChatRun,
  getChatSessions,
  deleteChatSession,
  stopChatRun,
  subscribeRunEvents,
} from '@/api'

export interface ToolEvent {
  type: 'tool_call' | 'tool_result'
  name: string
  arguments?: any
  result?: any
}

export interface SessionItem {
  id: number
  title: string
  message_count: number
  updated_at: string | null
}

export interface LiveRun {
  runId: number
  sessionId: number
  status: 'pending' | 'running' | 'done' | 'failed' | 'stopped'
  question: string
  answer: string
  toolEvents: ToolEvent[]
  error: string | null
  detach: (() => void) | null
}

const RECONNECT_MAX = 3

export const useAiChatStore = defineStore('aiChat', () => {
  // 全部运行中的 run（key: runId）——页面卸载不影响
  const runs = reactive(new Map<number, LiveRun>())
  // 会话 -> 当前展示中的 run（活跃或刚结束待合入）
  const currentRunBySession = reactive(new Map<number, number>())
  // 会话 -> 排队中的 runId 队列（FIFO，活跃 run 结束后依次接管）
  const queueBySession = reactive(new Map<number, number[]>())
  // 会话列表
  const sessions = ref<SessionItem[]>([])
  // 每会话的重连尝试计数
  const reconnectCount = reactive(new Map<number, number>())
  // 会话完成版本号：每次有 run 到达终态时 +1，页面据此刷新历史（避免组件卸载期间错过终态）
  const completedVersion = reactive(new Map<number, number>())

  // ---------------- 会话列表 ----------------
  async function loadSessions() {
    try {
      const data: any = await getChatSessions()
      sessions.value = data?.items || []
    } catch {
      /* 忽略 */
    }
  }

  function upsertSession(item: SessionItem) {
    const idx = sessions.value.findIndex((s) => s.id === item.id)
    if (idx >= 0) sessions.value.splice(idx, 1, { ...sessions.value[idx], ...item })
    else sessions.value.unshift(item)
  }

  async function removeSession(sessionId: number) {
    try {
      await deleteChatSession(sessionId)
    } catch {
      return false
    }
    sessions.value = sessions.value.filter((s) => s.id !== sessionId)
    // 清理该会话的本地运行状态（活跃 + 排队全部终止）
    for (const [runId, run] of runs) {
      if (run.sessionId === sessionId) {
        run.detach?.()
        runs.delete(runId)
      }
    }
    currentRunBySession.delete(sessionId)
    queueBySession.delete(sessionId)
    return true
  }

  // ---------------- 发送（排队） ----------------
  async function sendMessage(params: {
    sessionId: number | null
    question: string
    providerId?: number | null
    model?: string | null
    enableTools?: boolean
  }): Promise<{ runId: number; sessionId: number } | { error: string }> {
    try {
      const data: any = await createChatRun({
        session_id: params.sessionId,
        question: params.question,
        provider_id: params.providerId ?? null,
        model: params.model ?? null,
        enable_tools: params.enableTools ?? true,
      })
      const runId: number = data.run_id
      const sessionId: number = data.session_id
      upsertSession({ id: sessionId, title: data.title || '新对话', message_count: 0, updated_at: null })

      const run: LiveRun = reactive({
        runId,
        sessionId,
        status: 'pending',
        question: params.question,
        answer: '',
        toolEvents: [],
        error: null,
        detach: null,
      })
      runs.set(runId, run)

      const cur = currentRunBySession.get(sessionId)
      if (cur != null && runs.get(cur)?.status && !['done', 'failed', 'stopped'].includes(runs.get(cur)!.status)) {
        // 已有活跃 run → 排队，等它结束后接管
        const q = queueBySession.get(sessionId) || []
        q.push(runId)
        queueBySession.set(sessionId, q)
      } else {
        currentRunBySession.set(sessionId, runId)
        attach(run)
      }
      return { runId, sessionId }
    } catch (e: any) {
      return { error: e?.message || '提交失败' }
    }
  }

  // ---------------- SSE 订阅 ----------------
  function attach(run: LiveRun, seenEvents = 0) {
    run.detach?.()
    const detach = subscribeRunEvents(
      run.runId,
      seenEvents,
      (event: any) => {
        reconnectCount.set(run.runId, 0)
        if (event.type === 'snapshot') {
          run.status = event.status
          run.answer = event.answer || ''
          run.toolEvents = event.tool_events || []
          run.error = event.error || null
        } else if (event.type === 'run_start') {
          run.status = 'running'
        } else if (event.type === 'content') {
          run.answer += event.content || ''
        } else if (event.type === 'tool_call') {
          run.toolEvents.push({ type: 'tool_call', name: event.name, arguments: event.arguments })
        } else if (event.type === 'tool_result') {
          run.toolEvents.push({ type: 'tool_result', name: event.name, result: event.result })
        } else if (event.type === 'run_end') {
          run.status = event.status
          run.error = event.error || null
        } else if (event.type === 'error') {
          run.status = 'failed'
          run.error = event.message || '执行失败'
        }
      },
      () => onStreamClosed(run),
      (message: string) => onStreamError(run, message)
    )
    run.detach = detach
  }

  function onStreamClosed(run: LiveRun) {
    if (['done', 'failed', 'stopped'].includes(run.status)) {
      reconnectCount.set(run.runId, 0)
      completedVersion.set(run.sessionId, (completedVersion.get(run.sessionId) || 0) + 1)
      takeNextOrClose(run.sessionId)
    } else if (reconnectCount.get(run.runId, 0) < RECONNECT_MAX) {
      reconnect(run) // 流被服务端提前关闭（重启/超时），重连续传
    }
  }

  function onStreamError(run: LiveRun, message: string) {
    if (reconnectCount.get(run.runId, 0) < RECONNECT_MAX) {
      reconnect(run)
      return
    }
    // 多次重连失败：降级为一次性查询，拿不到就判失败
    import('@/api').then(async ({ getChatRun }) => {
      try {
        const data: any = await getChatRun(run.runId)
        run.status = data.status
        run.answer = data.answer ?? ''
        run.toolEvents = data.tool_events ?? []
        run.error = data.error ?? message
      } catch {
        run.status = 'failed'
        run.error = message
      }
      takeNextOrClose(run.sessionId)
    })
  }

  function reconnect(run: LiveRun) {
    reconnectCount.set(run.runId, (reconnectCount.get(run.runId) || 0) + 1)
    const attempt = reconnectCount.get(run.runId)!
    const delay = Math.min(1000 * 2 ** (attempt - 1), 4000)
    setTimeout(() => {
      if (!['done', 'failed', 'stopped'].includes(run.status)) attach(run, 0) // 快照兜底，无重复
    }, delay)
  }

  /** 活跃 run 结束：接管队首（并清理已结束的 run）；无排队时保留终态供页面合入后调 finishRun */
  function takeNextOrClose(sessionId: number) {
    const q = queueBySession.get(sessionId)
    if (q && q.length > 0) {
      const nextId = q.shift()!
      if (q.length === 0) queueBySession.delete(sessionId)
      else queueBySession.set(sessionId, q)
      // 清理刚结束的 run（流已关、内容已落库）
      const finishedId = currentRunBySession.get(sessionId)
      if (finishedId != null) {
        runs.get(finishedId)?.detach?.()
        runs.delete(finishedId)
        reconnectCount.delete(finishedId)
      }
      const next = runs.get(nextId)
      if (next) {
        currentRunBySession.set(sessionId, nextId)
        attach(next)
      }
    }
    // 没有排队任务：保留 currentRun 引用供页面合入历史（页面合入后调 finishRun 清理）
  }

  /** 页面在把终态 run 合入历史后调用：清理状态 */
  function finishRun(sessionId: number) {
    const cur = currentRunBySession.get(sessionId)
    if (cur != null) {
      const run = runs.get(cur)
      run?.detach?.()
      runs.delete(cur)
      currentRunBySession.delete(sessionId)
      reconnectCount.delete(cur)
    }
  }

  // ---------------- 停止 / 恢复 ----------------
  async function stopRun(sessionId: number): Promise<boolean> {
    const cur = currentRunBySession.get(sessionId)
    const run = cur != null ? runs.get(cur) : null
    if (!run || ['done', 'failed', 'stopped'].includes(run.status)) return false
    try {
      await stopChatRun(run.runId)
      return true
    } catch {
      return false
    }
  }

  /** 撤回排队中的消息 */
  async function withdrawQueued(sessionId: number, runId: number): Promise<boolean> {
    const q = queueBySession.get(sessionId)
    try {
      await stopChatRun(runId)
    } catch {
      return false
    }
    if (q) {
      const idx = q.indexOf(runId)
      if (idx >= 0) q.splice(idx, 1)
      if (q.length === 0) queueBySession.delete(sessionId)
    }
    runs.delete(runId)
    return true
  }

  /** 进入会话时恢复运行中的 run（刷新页面/重开浏览器后也能续上） */
  async function restoreSession(sessionId: number): Promise<boolean> {
    // store 里已有活跃状态：终态的清理掉（历史里已有），活跃的直接续用
    const cur = currentRunBySession.get(sessionId)
    if (cur != null && runs.has(cur)) {
      const st = runs.get(cur)!.status
      if (['done', 'failed', 'stopped'].includes(st)) {
        finishRun(sessionId)
        return false
      }
      return true
    }
    try {
      const data: any = await getActiveChatRun(sessionId)
      if (!data) return false
      const run: LiveRun = reactive({
        runId: data.run_id,
        sessionId,
        status: data.status,
        question: data.question || '',
        answer: data.answer || '',
        toolEvents: data.tool_events || [],
        error: data.error || null,
        detach: null,
      })
      runs.set(run.runId, run)
      currentRunBySession.set(sessionId, run.runId)
      if (data.queued > 0) {
        // 排队 run 的 id 未知（跨页面刷新），由后端执行后自然出现；
        // 终态接管依赖下一次 restore——可接受（排队跨刷新是边缘场景）。
        queueBySession.set(sessionId, [])
      }
      attach(run)
      return true
    } catch {
      return false
    }
  }

  /** 清理所有会话中滞留的终态 run（页面挂载时调用，防止泄漏） */
  function sweepTerminalRuns() {
    for (const [sid, runId] of Array.from(currentRunBySession.entries())) {
      const st = runs.get(runId)?.status
      if (st != null && ['done', 'failed', 'stopped'].includes(st)) {
        finishRun(sid)
      }
    }
  }

  function isSessionBusy(sessionId: number | null): boolean {
    if (sessionId == null) return false
    const cur = currentRunBySession.get(sessionId)
    if (cur == null) return false
    const st = runs.get(cur)?.status
    return st === 'pending' || st === 'running'
  }

  return {
    runs,
    currentRunBySession,
    queueBySession,
    sessions,
    completedVersion,
    loadSessions,
    upsertSession,
    removeSession,
    sendMessage,
    stopRun,
    withdrawQueued,
    restoreSession,
    sweepTerminalRuns,
    finishRun,
    isSessionBusy,
  }
})
