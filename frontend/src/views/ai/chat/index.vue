<template>
  <div class="chat-page">
    <!-- 会话侧栏（桌面端常驻，移动端抽屉） -->
    <transition name="session-slide">
      <div v-show="!isMobile || sessionDrawerOpen" class="session-panel">
        <div class="session-panel-header">
          <span class="session-panel-title">会话</span>
          <el-tooltip content="新建会话" placement="bottom">
            <button class="icon-btn" @click="newSession">
              <el-icon :size="16"><Plus /></el-icon>
            </button>
          </el-tooltip>
        </div>
        <div class="session-list">
          <div
            v-for="s in sessions"
            :key="s.id"
            class="session-item"
            :class="{ active: s.id === activeSessionId }"
            @click="switchSession(s.id)"
          >
            <div class="session-item-main">
              <div class="session-item-top">
                <span class="session-item-title" :title="s.title">{{ s.title }}</span>
                <span v-if="isSessionWorking(s.id)" class="session-status-dot" title="生成中"></span>
              </div>
              <div class="session-item-sub">
                <span>{{ formatSessionTime(s.updated_at) }}</span>
                <span>·</span>
                <span>{{ s.message_count }} 条</span>
              </div>
            </div>
            <el-icon
              class="session-item-del"
              :size="14"
              @click.stop="confirmDeleteSession(s)"
            ><Delete /></el-icon>
          </div>
          <div v-if="sessions.length === 0" class="session-empty">暂无历史会话</div>
        </div>
      </div>
    </transition>
    <!-- 移动端抽屉遮罩 -->
    <div
      v-if="isMobile && sessionDrawerOpen"
      class="session-overlay"
      @click="sessionDrawerOpen = false"
    ></div>

    <!-- 主聊天区 -->
    <div class="chat-main">
      <!-- 顶部状态条（仅会话状态，工具收纳进输入框） -->
      <div v-if="workingSessionCount > 0 || isMobile" class="chat-statusbar">
        <button v-if="isMobile" class="icon-btn" @click="sessionDrawerOpen = true">
          <el-icon :size="18"><Menu /></el-icon>
        </button>
        <span v-if="workingSessionCount > 0" class="running-badge">
          <span class="running-dot"></span>{{ workingSessionCount }} 个生成中
        </span>
      </div>

      <!-- 消息区域 -->
      <div ref="messagesRef" class="chat-messages" @scroll="handleScroll">
        <!-- 欢迎提示 -->
        <div v-if="displayMessages.length === 0" class="chat-welcome">
          <div class="welcome-logo">
            <el-icon :size="30" color="#fff"><ChatDotRound /></el-icon>
          </div>
          <h3>有什么可以帮您？</h3>
          <p class="welcome-sub">用自然语言查询与操作系统，支持多会话并行、切页面不中断</p>
          <div class="welcome-suggestions">
            <div
              v-for="s in suggestions"
              :key="s.text"
              class="suggestion-item"
              @click="sendQuickMessage(s.text)"
            >
              <el-icon class="suggestion-icon"><component :is="s.icon" /></el-icon>
              <div class="suggestion-text">
                <div class="suggestion-title">{{ s.title }}</div>
                <div class="suggestion-desc">{{ s.text }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, i) in displayMessages"
          :key="msg.key"
          class="message-row"
          :class="[msg.role, { 'is-pending': msg.pending }]"
        >
          <div class="msg-main">
            <div class="message-meta">
              <span class="speaker-label">{{ msg.role === 'user' ? '我' : 'AI 助手' }}</span>
              <span v-if="msg.time" class="message-time">{{ msg.time }}</span>
              <span v-if="msg.pending" class="queue-tag"><el-icon :size="12"><Clock /></el-icon>生成中</span>
              <span v-else-if="msg.queued" class="queue-tag queued"><el-icon :size="12"><Clock /></el-icon>排队中</span>
            </div>
            <!-- 工具调用状态 -->
            <div v-if="msg.toolEvents && msg.toolEvents.length" class="tool-events">
              <div v-for="(te, j) in msg.toolEvents" :key="j" class="tool-event">
                <el-icon :size="13" :color="te.type === 'tool_result' ? 'var(--el-color-success)' : 'var(--el-color-primary)'">
                  <Loading v-if="te.type === 'tool_call'" class="is-loading" />
                  <CircleCheck v-else />
                </el-icon>
                <span class="tool-name">{{ te.name }}</span>
                <span class="tool-args">{{ formatToolArgs(te.arguments) }}</span>
              </div>
            </div>
            <!-- 消息内容 -->
            <div
              v-if="msg.content"
              class="message-content markdown-body"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <!-- 排队消息操作 -->
            <div v-if="msg.queued && msg.runId" class="message-actions" :class="{ user: true }">
              <button class="msg-action-btn withdraw-btn" @click="withdrawQueued(msg.runId)">
                <el-icon :size="13"><Close /></el-icon>撤回
              </button>
            </div>
            <!-- 错误信息 -->
            <div v-if="msg.error" class="message-error">
              <el-icon><WarningFilled /></el-icon>
              {{ msg.error }}
            </div>
            <!-- 正在输入指示 -->
            <div v-if="msg.streaming && !msg.content && !msg.error" class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
            <!-- 消息操作（复制） -->
            <div v-if="msg.content && !msg.streaming" class="message-actions" :class="{ user: msg.role === 'user' }">
              <el-tooltip content="复制" placement="top">
                <button class="msg-action-btn" @click="copyMessage(msg)">
                  <el-icon :size="13"><CopyDocument /></el-icon>
                </button>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域（qm 式大圆角卡片） -->
      <div class="composer-area">
        <div v-if="queuedRuns.length > 0" class="queue-note">
          <el-icon :size="13"><Clock /></el-icon>
          已排队 {{ queuedRuns.length }} 条消息，将按顺序执行
        </div>
        <div class="composer-wrap">
          <div v-if="isBusy" class="generating-tip">
            <el-icon class="is-loading" :size="13"><Loading /></el-icon>
            <span>正在生成回复，可随时切换其他会话继续提问</span>
            <button class="stop-inline" @click="stopActive">
              <el-icon :size="12"><VideoPause /></el-icon>停止
            </button>
          </div>
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 6 }"
            placeholder="输入消息，Enter 发送，Shift+Enter 换行"
            resize="none"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="composer-toolbar">
            <div class="composer-left">
              <el-tooltip content="启用工具调用（允许 AI 查询/操作系统数据）" placement="top">
                <div class="tools-toggle">
                  <el-icon :size="14"><SetUp /></el-icon>
                  <span>工具</span>
                  <el-switch v-model="enableTools" size="small" />
                </div>
              </el-tooltip>
              <span class="char-count" v-if="inputText.length">{{ inputText.length }}</span>
              <!-- 会话操作（收纳进输入框） -->
              <template v-if="activeSessionId != null">
                <span class="toolbar-sep"></span>
                <el-tooltip content="重命名会话" placement="top">
                  <button class="toolbar-icon-btn" @click="renameActiveSession">
                    <el-icon :size="14"><EditPen /></el-icon>
                  </button>
                </el-tooltip>
                <el-tooltip content="清空当前对话（历史仍保留在会话中）" placement="top">
                  <button class="toolbar-icon-btn" @click="clearChat">
                    <el-icon :size="14"><Delete /></el-icon>
                  </button>
                </el-tooltip>
              </template>
            </div>
            <div class="composer-right">
              <!-- 模型选择（收纳进输入框，qm 式） -->
              <el-select
                v-model="selectedProviderId"
                placeholder="供应商"
                class="provider-select"
                size="small"
                @change="onProviderChange"
              >
                <el-option
                  v-for="p in providers"
                  :key="p.id"
                  :label="p.name"
                  :value="p.id"
                />
              </el-select>
              <el-select
                v-model="selectedModel"
                placeholder="模型"
                class="model-select"
                size="small"
                :disabled="modelOptions.length === 0"
                @change="saveModelChoice"
              >
                <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
              </el-select>
              <el-tooltip v-if="isBusy" content="停止生成" placement="top">
                <button class="stop-square" @click="stopActive">
                  <el-icon :size="15"><VideoPause /></el-icon>
                </button>
              </el-tooltip>
              <el-tooltip content="发送（Enter）" placement="top">
                <button class="send-square" :disabled="!inputText.trim()" @click="sendMessage">
                  <el-icon :size="16"><Promotion /></el-icon>
                </button>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAllProviders,
  getChatSessionMessages,
} from '@/api'
import { useAiChatStore } from '@/stores/aiChat'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import Prism from 'prismjs'
// 按需注册常用语言
import 'prismjs/components/prism-markup.min.js'
import 'prismjs/components/prism-javascript.min.js'
import 'prismjs/components/prism-typescript.min.js'
import 'prismjs/components/prism-json.min.js'
import 'prismjs/components/prism-python.min.js'
import 'prismjs/components/prism-sql.min.js'
import 'prismjs/components/prism-bash.min.js'
import 'prismjs/components/prism-css.min.js'
import 'prismjs/components/prism-yaml.min.js'
import 'prismjs/components/prism-go.min.js'
import 'prismjs/components/prism-java.min.js'
import 'prismjs/components/prism-php.min.js'
import 'prismjs/components/prism-markdown.min.js'
import 'prismjs/components/prism-ini.min.js'

interface ToolEvent {
  type: 'tool_call' | 'tool_result'
  name: string
  arguments?: any
  result?: any
}

interface DisplayMessage {
  key: string
  role: 'user' | 'assistant'
  content: string
  time?: string
  toolEvents?: ToolEvent[]
  error?: string | null
  streaming?: boolean
  pending?: boolean
  queued?: boolean
  runId?: number
}

interface ChatSessionItem {
  id: number
  title: string
  message_count: number
  updated_at: string | null
}

const store = useAiChatStore()

// 会话列表来自全局 store（切页面后状态仍在）
const sessions = computed(() => store.sessions)

const messagesRef = ref<HTMLElement>()
const inputText = ref('')
const enableTools = ref(true)
const providers = ref<any[]>([])
const selectedProviderId = ref<number | null>(null)
const selectedModel = ref<string>('')
const activeSessionId = ref<number | null>(null)
const historyMessages = ref<DisplayMessage[]>([])
const sessionDrawerOpen = ref(false)
const isMobile = ref(window.innerWidth <= 991)

const STORAGE_KEY = 'apeadmin_ai_chat_pref'
const LAST_SESSION_KEY = 'apeadmin_ai_chat_last_session'

const currentProvider = computed(() =>
  providers.value.find((p) => p.id === selectedProviderId.value)
)

const modelOptions = computed(() => {
  const p = currentProvider.value
  if (!p) return []
  let models: string[] = []
  try {
    models = typeof p.models === 'string' ? JSON.parse(p.models || '[]') : p.models || []
  } catch {
    models = []
  }
  return models
})

const suggestions = [
  { icon: 'User', title: '查询用户', text: '查询系统所有用户' },
  { icon: 'Avatar', title: '角色管理', text: '系统有哪些角色？' },
  { icon: 'DataAnalysis', title: '数据统计', text: '获取系统统计信息' },
  { icon: 'Menu', title: '菜单结构', text: '查看菜单树结构' },
]

// ---------- 会话运行状态（来自全局 store） ----------
function currentRunOf(sessionId: number | null) {
  if (sessionId == null) return null
  const runId = store.currentRunBySession.get(sessionId)
  return runId != null ? store.runs.get(runId) ?? null : null
}

const activeRun = computed(() => currentRunOf(activeSessionId.value))

const isBusy = computed(
  () => activeRun.value != null && ['pending', 'running'].includes(activeRun.value.status)
)

const queuedRuns = computed(() => {
  const sid = activeSessionId.value
  if (sid == null) return []
  const q = store.queueBySession.get(sid) || []
  return q.map((id) => store.runs.get(id)).filter(Boolean) as any[]
})

/** 展示消息 = 历史消息 + 活跃 run（问题去重）+ 排队 run 的问题 */
const displayMessages = computed<DisplayMessage[]>(() => {
  const msgs: DisplayMessage[] = [...historyMessages.value]
  const run = activeRun.value
  if (run) {
    // 后端在入队时就已把问题落库；仅当历史里还没有时才追加（避免重复）
    const lastHis = msgs[msgs.length - 1]
    const qInHistory = lastHis && lastHis.role === 'user' && lastHis.content === run.question
    if (!qInHistory) {
      msgs.push({ key: `u-${run.runId}`, role: 'user', content: run.question, pending: true })
    }
    msgs.push({
      key: `a-${run.runId}`,
      role: 'assistant',
      content: run.answer,
      toolEvents: run.toolEvents,
      error: run.error,
      streaming: run.status === 'pending' || run.status === 'running',
      pending: run.status === 'running',
    })
  }
  for (const q of queuedRuns.value) {
    if (run && q.runId === run.runId) continue
    const qInHistory = historyMessages.value.some(
      (m) => m.role === 'user' && m.content === q.question
    )
    if (!qInHistory) {
      msgs.push({ key: `u-${q.runId}`, role: 'user', content: q.question, queued: true, runId: q.runId })
    }
  }
  return msgs
})

function isSessionWorking(sessionId: number): boolean {
  const runId = store.currentRunBySession.get(sessionId)
  if (runId == null) return false
  const st = store.runs.get(runId)?.status
  return st === 'pending' || st === 'running'
}

const workingSessionCount = computed(() => {
  let n = 0
  for (const s of store.sessions) if (isSessionWorking(s.id)) n++
  return n
})

// ---------- 偏好持久化（供应商/模型） ----------
function loadPrefs() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const pref = JSON.parse(raw)
      selectedModel.value = pref.model || ''
      return pref.provider_id || null
    }
  } catch {
    /* ignore */
  }
  return null
}

function saveModelChoice() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ provider_id: selectedProviderId.value, model: selectedModel.value })
    )
  } catch {
    /* ignore */
  }
}

// ---------- Markdown + 代码高亮 + XSS 防护 ----------
marked.setOptions({
  breaks: true,
  gfm: true,
})

function renderMarkdown(text: string): string {
  try {
    const html = marked.parse(text) as string
    const clean = DOMPurify.sanitize(html, {
      ADD_ATTR: ['target'],
    })
    return clean
  } catch {
    return DOMPurify.sanitize(text)
  }
}

function highlightCode() {
  nextTick(() => {
    if (!messagesRef.value) return
    messagesRef.value.querySelectorAll('pre code').forEach((el) => {
      if (!el.classList.contains('language-marked')) {
        el.classList.add('language-marked')
        try {
          Prism.highlightElement(el as HTMLElement)
        } catch {
          /* 高亮失败忽略 */
        }
      }
    })
  })
}

watch(() => displayMessages.value.map((m) => m.content).join(''), highlightCode)

function formatToolArgs(args: any): string {
  if (!args || typeof args !== 'object') return ''
  const entries = Object.entries(args)
  if (entries.length === 0) return ''
  return entries.map(([k, v]) => `${k}=${v}`).join(', ')
}

// ---------- 时间显示 ----------
function formatTime(iso: string | undefined | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return ''
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function formatSessionTime(iso: string | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (isNaN(d.getTime())) return ''
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  const hm = `${pad(d.getHours())}:${pad(d.getMinutes())}`
  if (d.toDateString() === now.toDateString()) return hm
  return `${d.getMonth() + 1}/${d.getDate()} ${hm}`
}

// ---------- 供应商与模型 ----------
async function loadProviders() {
  try {
    const data: any = await getAllProviders()
    providers.value = data || []
    const savedProviderId = loadPrefs()
    if (providers.value.length > 0) {
      const saved = providers.value.find((p) => p.id === savedProviderId)
      selectedProviderId.value = saved ? saved.id : providers.value[0].id
      if (!modelOptions.value.includes(selectedModel.value)) {
        selectedModel.value = modelOptions.value[0] || ''
      }
    }
  } catch {
    providers.value = []
  }
}

function onProviderChange() {
  selectedModel.value = modelOptions.value[0] || ''
  saveModelChoice()
}

// ---------- 会话管理 ----------
async function loadSessions() {
  await store.loadSessions()
}

function newSession() {
  activeSessionId.value = null
  historyMessages.value = []
  sessionDrawerOpen.value = false
  try {
    localStorage.removeItem(LAST_SESSION_KEY)
  } catch {
    /* ignore */
  }
}

async function loadHistory(sessionId: number) {
  try {
    const data: any = await getChatSessionMessages(sessionId)
    const list = data?.messages || []
    historyMessages.value = list.map((m: any, i: number) => ({
      key: `h-${m.id ?? i}`,
      role: m.role,
      content: m.content,
      time: formatTime(m.created_at),
      toolEvents: m.tool_events || [],
    }))
    // 同步会话元数据（标题/计数，后端为准）
    const s = data?.session
    if (s) {
      store.upsertSession({
        id: s.id,
        title: s.title,
        message_count: s.message_count,
        updated_at: s.updated_at,
      })
    }
  } catch {
    ElMessage.error('加载会话失败')
  }
}

async function switchSession(id: number) {
  if (id === activeSessionId.value) {
    sessionDrawerOpen.value = false
    return
  }
  activeSessionId.value = id
  historyMessages.value = []
  sessionDrawerOpen.value = false
  try {
    localStorage.setItem(LAST_SESSION_KEY, String(id))
  } catch {
    /* ignore */
  }
  await Promise.all([loadHistory(id), store.restoreSession(id)])
  scrollToBottom(true)
}

async function confirmDeleteSession(s: ChatSessionItem) {
  try {
    await ElMessageBox.confirm(`删除会话「${s.title}」？删除后不可恢复`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const ok = await store.removeSession(s.id)
    if (!ok) {
      ElMessage.error('删除失败')
      return
    }
    if (activeSessionId.value === s.id) {
      activeSessionId.value = null
      historyMessages.value = []
    }
    ElMessage.success('会话已删除')
  } catch {
    /* 用户取消 */
  }
}

// ---------- 滚动 ----------
function scrollToBottom(force = false) {
  nextTick(() => {
    if (!messagesRef.value) return
    if (force || autoScroll) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

let autoScroll = true
function handleScroll() {
  const el = messagesRef.value
  if (!el) return
  autoScroll = el.scrollHeight - el.scrollTop - el.clientHeight < 80
}

// ---------- 发送 ----------
function sendQuickMessage(text: string) {
  inputText.value = text
  sendMessage()
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return

  if (providers.value.length === 0) {
    ElMessage.warning('请先在「模型密钥管理」中添加模型供应商')
    return
  }

  const res = await store.sendMessage({
    sessionId: activeSessionId.value,
    question: text,
    providerId: selectedProviderId.value,
    model: selectedModel.value || null,
    enableTools: enableTools.value,
  })
  if ('error' in res) {
    ElMessage.error(res.error)
    return
  }
  if (activeSessionId.value == null) {
    activeSessionId.value = res.sessionId
  }
  inputText.value = ''
  autoScroll = true
  scrollToBottom(true)
  try {
    localStorage.setItem(LAST_SESSION_KEY, String(res.sessionId))
  } catch {
    /* ignore */
  }
}

// ---------- 运行终态 → 合入历史 ----------
// 监听 store 的完成版本号（而非 run.status）：页面卸载期间错过的终态也能在回归后被
// sweepTerminalRuns + loadHistory 补齐；同会话连续排队时每次完成都会触发刷新
watch(
  () => {
    const sid = activeSessionId.value
    return sid == null ? 0 : store.completedVersion.get(sid) || 0
  },
  async () => {
    const sid = activeSessionId.value
    if (sid == null) return
    const curId = store.currentRunBySession.get(sid)
    const cur = curId != null ? store.runs.get(curId) : null
    // 先刷新历史（服务端为准），避免闪烁：终态 run 仍在 store 中展示完整内容
    await loadHistory(sid)
    // 仅当当前 run 已终态且无排队时才清理（排队接管时 cur 是新的活跃 run，不能动）
    const qLen = (store.queueBySession.get(sid) || []).length
    if (cur && ['done', 'failed', 'stopped'].includes(cur.status) && qLen === 0) {
      store.finishRun(sid)
    }
    scrollToBottom()
    if (cur && cur.status === 'failed' && !cur.answer) {
      ElMessage.error('生成失败：' + (cur.error || '未知错误'))
    }
  }
)

// 排队 run 被接管为活跃 run（前一个完成后）
watch(
  () => {
    const sid = activeSessionId.value
    if (sid == null) return null
    return store.currentRunBySession.get(sid) ?? null
  },
  (newId, oldId) => {
    if (newId != null && newId !== oldId) scrollToBottom(true)
  }
)

// live 内容变化 → 跟随滚动
watch(
  () => activeRun.value?.answer,
  () => scrollToBottom()
)

// ---------- 停止 / 撤回 ----------
async function stopActive() {
  const sid = activeSessionId.value
  if (sid == null) return
  await store.stopRun(sid)
}

async function withdrawQueued(runId: number) {
  const sid = activeSessionId.value
  if (sid == null) return
  await store.withdrawQueued(sid, runId)
}

function clearChat() {
  if (historyMessages.value.length === 0 && !activeRun.value) return
  ElMessageBox.confirm('清空当前对话显示？（历史消息已保存在会话中，可从左侧切换回来）', '提示', {
    confirmButtonText: '清空',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      historyMessages.value = []
      activeSessionId.value = null
      try {
        localStorage.removeItem(LAST_SESSION_KEY)
      } catch {
        /* ignore */
      }
    })
    .catch(() => {})
}

async function renameActiveSession() {
  const sid = activeSessionId.value
  if (sid == null) return
  const s = store.sessions.find((x) => x.id === sid)
  if (!s) return
  try {
    const { value } = await ElMessageBox.prompt('新的会话名称', '重命名会话', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: s.title,
      inputValidator: (v: string) =>
        (v && v.trim().length > 0 && v.trim().length <= 200) || '名称不能为空且不超过 200 字',
    })
    const title = (value || '').trim()
    if (!title || title === s.title) return
    const { renameChatSession } = await import('@/api')
    await renameChatSession(sid, title)
    s.title = title
    ElMessage.success('已重命名')
  } catch {
    /* 用户取消 */
  }
}

// ---------- 复制 ----------
async function copyMessage(msg: DisplayMessage) {
  try {
    await navigator.clipboard.writeText(msg.content)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

// ---------- 移动端检测 ----------
function onResize() {
  isMobile.value = window.innerWidth <= 991
}

onMounted(async () => {
  window.addEventListener('resize', onResize)
  await Promise.all([loadProviders(), loadSessions()])
  // 清理卸载期间滞留的终态 run（历史里已含其内容）
  store.sweepTerminalRuns()
  // 恢复上次会话视图（含运行中的 run 续流）
  let lastId: number | null = null
  try {
    const raw = localStorage.getItem(LAST_SESSION_KEY)
    if (raw) lastId = parseInt(raw, 10) || null
  } catch {
    /* ignore */
  }
  if (lastId != null && store.sessions.some((s) => s.id === lastId)) {
    await switchSession(lastId)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  // 注意：不终止后台运行！SSE 订阅由全局 store 持有，切页面后继续接收。
})
</script>

<style scoped>
.chat-page {
  display: flex;
  height: 100%;
  background: var(--theme-body-bg, #f5f7fa);
  border-radius: 8px;
  overflow: hidden;
}

/* ========== 会话侧栏 ========== */
.session-panel {
  width: 232px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--theme-card-bg, #fff);
  border-right: 1px solid var(--border-light, #ebeef5);
}
.session-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-light, #ebeef5);
  flex-shrink: 0;
}
.session-panel-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #303133);
}
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.session-list::-webkit-scrollbar {
  width: 4px;
}
.session-list::-webkit-scrollbar-thumb {
  background: #d0d3d8;
  border-radius: 2px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px 6px 11px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-regular, #606266);
  font-size: 13px;
  transition: background 0.12s;
}
.session-item:hover {
  background: rgba(127, 138, 248, 0.07);
}
.session-item.active {
  background: var(--el-color-primary-light-9, #ecf0ff);
  color: var(--el-color-primary, #5a67f5);
}
.session-item-main {
  flex: 1;
  min-width: 0;
}
.session-item-top {
  display: flex;
  align-items: center;
  gap: 6px;
}
.session-item-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-item-sub {
  display: flex;
  gap: 4px;
  font-size: 11px;
  color: var(--text-secondary, #909399);
  margin-top: 2px;
}
.session-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--el-color-success, #67c23a);
  flex-shrink: 0;
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.45; transform: scale(0.8); }
}
.session-item-del {
  flex-shrink: 0;
  color: var(--text-secondary, #909399);
  opacity: 0;
  transition: opacity 0.15s;
}
.session-item:hover .session-item-del {
  opacity: 1;
}
.session-item-del:hover {
  color: var(--el-color-danger, #f56c6c);
}
.session-empty {
  text-align: center;
  color: var(--text-secondary, #909399);
  font-size: 12px;
  padding: 24px 0;
}
.session-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 20;
}

/* ========== 主区 ========== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Statusbar（生成状态胶囊，无工具占用） */
.chat-statusbar {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 8px;
  padding: 6px 16px 0;
  flex-shrink: 0;
}
.running-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--el-color-success-light-9, #f0f9eb);
  color: var(--el-color-success, #67c23a);
  font-size: 12px;
  white-space: nowrap;
}
.running-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--el-color-success, #67c23a);
  animation: pulse 1.2s ease-in-out infinite;
}
/* composer 内的小尺寸下拉 */
.composer-right .provider-select {
  width: 128px;
}
.composer-right .model-select {
  width: 150px;
}
.composer-right :deep(.el-select__wrapper) {
  background: transparent;
  box-shadow: none;
  min-height: 28px;
  padding: 0 4px;
}
.composer-right :deep(.el-select__wrapper):hover {
  background: var(--fill-hover, #f5f7fa);
  border-radius: 7px;
}
.composer-right :deep(.el-select__placeholder),
.composer-right :deep(.el-select__selected-item) {
  font-size: 12.5px;
  color: var(--text-secondary, #909399);
}
/* composer 工具栏里的会话操作小按钮 */
.toolbar-sep {
  width: 1px;
  height: 14px;
  background: var(--border-light, #dcdfe6);
  margin: 0 2px;
}
.toolbar-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: none;
  border-radius: 7px;
  background: transparent;
  color: var(--text-secondary, #909399);
  cursor: pointer;
  transition: all 0.12s ease;
}
.toolbar-icon-btn:hover {
  background: var(--fill-hover, #f5f7fa);
  color: var(--el-color-primary, #5a67f5);
}
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-regular, #606266);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.icon-btn:hover {
  background: var(--fill-hover, #f5f7fa);
  color: var(--el-color-primary, #5a67f5);
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
  scroll-behavior: smooth;
}
.chat-messages::-webkit-scrollbar {
  width: 6px;
}
.chat-messages::-webkit-scrollbar-thumb {
  background: #d0d3d8;
  border-radius: 3px;
}

/* Welcome */
.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
  text-align: center;
  padding: 24px;
}
.welcome-logo {
  width: 52px;
  height: 52px;
  border-radius: 15px;
  background: linear-gradient(135deg, var(--el-color-primary, #5a67f5), #47d8ff);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(90, 103, 245, 0.25);
}
.chat-welcome h3 {
  margin: 16px 0 4px;
  font-size: 24px;
  font-weight: 500;
  letter-spacing: -0.01em;
  color: var(--text-primary, #303133);
}
.welcome-sub {
  font-size: 13px;
  color: var(--text-secondary, #909399);
  margin: 0 0 20px;
}
.welcome-suggestions {
  display: grid;
  grid-template-columns: repeat(2, minmax(200px, 260px));
  gap: 10px;
}
.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  background: var(--theme-card-bg, #fff);
  border: 1px solid var(--border-light, #ebeef5);
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}
.suggestion-item:hover {
  border-color: var(--el-color-primary, #5a67f5);
  color: var(--el-color-primary, #5a67f5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(90, 103, 245, 0.1);
}
.suggestion-icon {
  margin-top: 2px;
  color: var(--el-color-primary, #5a67f5);
}
.suggestion-text {
  min-width: 0;
}
.suggestion-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary, #303133);
}
.suggestion-item:hover .suggestion-title {
  color: var(--el-color-primary, #5a67f5);
}
.suggestion-desc {
  font-size: 12px;
  color: var(--text-secondary, #909399);
  margin-top: 2px;
}

/* Message row（qm 式：无头像、speaker 小标签、assistant 文档流、user 低饱和气泡） */
.message-row {
  display: flex;
  min-width: 0;
  max-width: 760px;
  margin: 0 auto 4px;
  padding-bottom: 12px;
}
.message-row.user {
  flex-direction: column;
  align-items: flex-end;
}
.msg-main {
  min-width: 0;
  max-width: 100%;
}
.message-meta {
  margin: 0 0 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.speaker-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary, #909399);
  user-select: none;
}
.message-row.user .message-meta {
  justify-content: flex-end;
}
.message-time {
  font-size: 11px;
  color: var(--text-secondary, #c0c4cc);
}
.queue-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: var(--el-color-success, #67c23a);
  background: var(--el-color-success-light-9, #f0f9eb);
  padding: 1px 8px;
  border-radius: 999px;
}
.queue-tag.queued {
  color: var(--el-color-warning, #e6a23c);
  background: var(--el-color-warning-light-9, #fdf6ec);
}

/* Message content */
.message-content {
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
  max-width: 100%;
}
.message-row.user .message-content {
  display: inline-block;
  padding: 9px 14px;
  border-radius: 16px;
  background: var(--fill-light, #f0f2f5);
  color: var(--text-primary, #303133);
  max-width: 78%;
}
.message-row.is-pending .message-content {
  opacity: 0.75;
}

/* 消息操作 */
.message-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}
.message-row:hover .message-actions {
  opacity: 1;
}
.message-actions.user {
  justify-content: flex-end;
}
.msg-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  width: auto;
  height: 24px;
  padding: 0 6px;
  border: none;
  border-radius: 5px;
  background: transparent;
  color: var(--text-secondary, #909399);
  cursor: pointer;
  transition: all 0.15s;
  font-size: 12px;
}
.msg-action-btn:hover {
  background: var(--fill-hover, #f5f7fa);
  color: var(--el-color-primary, #5a67f5);
}
.withdraw-btn:hover {
  color: var(--el-color-danger, #f56c6c);
}

/* Markdown styling inside assistant messages */
.message-row.assistant .markdown-body :deep(h1),
.message-row.assistant .markdown-body :deep(h2),
.message-row.assistant .markdown-body :deep(h3) {
  margin: 8px 0 4px;
  font-weight: 600;
}
.message-row.assistant .markdown-body :deep(p) {
  margin: 4px 0;
}
.message-row.assistant .markdown-body :deep(ul),
.message-row.assistant .markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}
.message-row.assistant .markdown-body :deep(code) {
  background: var(--fill-light, #f0f2f5);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'SF Mono', 'Consolas', monospace;
}
.message-row.assistant .markdown-body :deep(pre) {
  background: #1e1e2e;
  color: #d4d4d4;
  padding: 12px 14px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
}
.message-row.assistant .markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
  font-family: 'SF Mono', 'Consolas', monospace;
}
.message-row.assistant .markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
}
.message-row.assistant .markdown-body :deep(th),
.message-row.assistant .markdown-body :deep(td) {
  border: 1px solid var(--border-light, #ebeef5);
  padding: 6px 12px;
  text-align: left;
}
.message-row.assistant .markdown-body :deep(th) {
  background: var(--fill-light, #f5f7fa);
  font-weight: 600;
}
/* Prism token 颜色（自定义克制配色） */
.message-row.assistant .markdown-body :deep(.token.comment),
.message-row.assistant .markdown-body :deep(.token.prolog),
.message-row.assistant .markdown-body :deep(.token.doctype),
.message-row.assistant .markdown-body :deep(.token.cdata) {
  color: #6c7293;
}
.message-row.assistant .markdown-body :deep(.token.punctuation) {
  color: #9aa0b5;
}
.message-row.assistant .markdown-body :deep(.token.keyword),
.message-row.assistant .markdown-body :deep(.token.tag),
.message-row.assistant .markdown-body :deep(.token.selector) {
  color: #c792ea;
}
.message-row.assistant .markdown-body :deep(.token.string),
.message-row.assistant .markdown-body :deep(.token.attr-value),
.message-row.assistant .markdown-body :deep(.token.char) {
  color: #c3e88d;
}
.message-row.assistant .markdown-body :deep(.token.number),
.message-row.assistant .markdown-body :deep(.token.boolean) {
  color: #f78c6c;
}
.message-row.assistant .markdown-body :deep(.token.function),
.message-row.assistant .markdown-body :deep(.token.class-name) {
  color: #82aaff;
}
.message-row.assistant .markdown-body :deep(.token.attr-name),
.message-row.assistant .markdown-body :deep(.token.property) {
  color: #ffcb6b;
}

/* Tool events */
.tool-events {
  margin-bottom: 6px;
}
.tool-event {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--el-color-primary-light-9, rgba(90, 103, 245, 0.06));
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-regular, #606266);
  margin-bottom: 2px;
}
.tool-name {
  font-weight: 600;
  color: var(--el-color-primary, #5a67f5);
}
.tool-args {
  color: var(--text-secondary, #909399);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Error */
.message-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--el-color-danger-light-9, #fef0f0);
  border-radius: 8px;
  color: var(--el-color-danger, #f56c6c);
  font-size: 13px;
}

/* Typing indicator */
.typing-indicator {
  display: inline-flex;
  gap: 4px;
  padding: 12px 16px;
  background: var(--theme-card-bg, #fff);
  border: 1px solid var(--border-light, #ebeef5);
  border-radius: 12px;
}
.typing-indicator span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #c0c4cc;
  animation: typing 1.4s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* Input area（qm 式大圆角卡片 composer） */
.composer-area {
  flex-shrink: 0;
  padding: 4px 16px max(14px, calc(10px + env(safe-area-inset-bottom)));
}
.queue-note {
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 760px;
  margin: 0 auto 8px;
  font-size: 12px;
  color: var(--el-color-warning, #e6a23c);
}
.composer-wrap {
  --composer-radius: 18px;
  max-width: 760px;
  margin: 0 auto;
  padding: 10px 12px 8px;
  background: var(--theme-card-bg, #fff);
  border: 1px solid var(--border-light, #ebeef5);
  border-radius: var(--composer-radius);
  box-shadow:
    0 2px 5px rgba(0, 0, 0, 0.04),
    0 8px 24px rgba(0, 0, 0, 0.05);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.composer-wrap:focus-within {
  border-color: var(--el-color-primary-light-5, #b3bcfc);
  box-shadow:
    0 2px 5px rgba(0, 0, 0, 0.04),
    0 8px 24px rgba(90, 103, 245, 0.12);
}
.composer-wrap :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  background: transparent;
  padding: 6px 6px 4px;
  font-size: 15px;
  line-height: 1.55;
  color: var(--text-primary, #303133);
}
.composer-wrap :deep(.el-textarea__inner)::placeholder {
  color: var(--text-secondary, #a8abb2);
}
.composer-wrap :deep(.el-textarea__inner):focus {
  border: none;
  box-shadow: none;
}
.generating-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-color-success, #67c23a);
  padding: 2px 6px 8px;
}
.stop-inline {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: auto;
  border: none;
  background: transparent;
  color: var(--el-color-danger, #f56c6c);
  font-size: 12px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 5px;
}
.stop-inline:hover {
  background: var(--el-color-danger-light-9, #fef0f0);
}
.composer-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 6px;
}
.composer-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.tools-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary, #909399);
  cursor: default;
}
.char-count {
  font-size: 11px;
  color: var(--text-secondary, #c0c4cc);
}
.composer-right {
  display: flex;
  align-items: center;
  gap: 7px;
}
/* 34×34 方形图标按钮（qm 式 send / stop） */
.send-square,
.stop-square {
  width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.12s ease, opacity 0.12s ease;
}
.send-square {
  background: var(--el-color-primary, #5a67f5);
  color: #fff;
}
.send-square:hover:not(:disabled) {
  background: var(--el-color-primary-light-3, #7f88f7);
}
.send-square:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.stop-square {
  background: transparent;
  border: 1px solid var(--border-light, #dcdfe6);
  color: var(--el-color-danger, #f56c6c);
}
.stop-square:hover {
  background: var(--el-color-danger-light-9, #fef0f0);
}

/* ========== 移动端适配（≤991px） ========== */
@media (max-width: 991px) {
  .chat-page {
    position: relative;
    border-radius: 0;
  }
  .session-panel {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 21;
    box-shadow: 4px 0 16px rgba(0, 0, 0, 0.08);
    transform: translateX(0);
  }
  .composer-right .provider-select {
    width: 96px;
  }
  .composer-right .model-select {
    width: 108px;
  }
  .chat-messages {
    padding: 14px 10px;
  }
  .message-row {
    padding-bottom: 10px;
  }
  .message-row.user .message-content {
    max-width: 88%;
  }
  .welcome-suggestions {
    grid-template-columns: 1fr;
    width: 100%;
    max-width: 340px;
  }
  .composer-area {
    padding: 2px 10px calc(10px + env(safe-area-inset-bottom, 0px));
  }
}

/* 会话抽屉滑入动画 */
.session-slide-enter-active,
.session-slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.session-slide-enter-from,
.session-slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
</style>

<style>
/* ===== 深色模式适配 ===== */
html.dark .session-panel {
  background: #232838;
  border-right-color: #36394a;
}
html.dark .session-panel-header {
  border-bottom-color: #36394a;
}
html.dark .session-panel-title {
  color: #e6e8f0;
}
html.dark .session-item {
  color: #b8bdd0;
}
html.dark .session-item:hover {
  background: rgba(127, 138, 248, 0.08);
}
html.dark .session-item.active {
  background: rgba(127, 138, 248, 0.15);
  color: #7f8af8;
}
html.dark .chat-welcome h3 {
  color: #e6e8f0;
}
html.dark .suggestion-item {
  background: #232838;
  border-color: #36394a;
}
html.dark .suggestion-title {
  color: #e6e8f0;
}
html.dark .suggestion-item:hover {
  border-color: #7f8af8;
  background: rgba(127, 138, 248, 0.06);
}
html.dark .message-row.user .message-content {
  background: #2e3344;
  color: #e6e8f0;
}
html.dark .message-row.assistant .message-content {
  background: transparent;
  color: #e6e8f0;
  border: none;
}
html.dark .composer-wrap {
  background: #232838;
  border-color: #36394a;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2), 0 8px 24px rgba(0, 0, 0, 0.25);
}
html.dark .composer-wrap :deep(.el-textarea__inner) {
  background: transparent;
  color: #e6e8f0;
}
html.dark .composer-wrap :deep(.el-textarea__inner)::placeholder {
  color: #6b7089;
}
html.dark .message-row.assistant .markdown-body code {
  background: #2e3344;
}
html.dark .message-row.assistant .markdown-body th {
  background: #2e3344;
}
html.dark .message-row.assistant .markdown-body th,
html.dark .message-row.assistant .markdown-body td {
  border-color: #36394a;
}
html.dark .tool-event {
  background: rgba(127, 138, 248, 0.1);
  color: #b8bdd0;
}
html.dark .message-error {
  background: rgba(245, 108, 108, 0.1);
  color: #f87171;
}
html.dark .typing-indicator {
  background: #232838;
  border-color: #36394a;
}
html.dark .typing-indicator span {
  background: #6b7089;
}
html.dark .composer-area .el-textarea__inner {
  background: transparent;
  border-color: #3a3f52;
  color: #e6e8f0;
}
html.dark .composer-area .el-textarea__inner::placeholder {
  color: #6b7089;
}
html.dark .msg-action-btn:hover {
  background: rgba(127, 138, 248, 0.1);
  color: #7f8af8;
}
html.dark .generating-tip {
  background: rgba(103, 194, 58, 0.1);
}
html.dark .generating-tip.queued-tip {
  background: rgba(230, 162, 60, 0.1);
}
html.dark .running-badge {
  background: rgba(103, 194, 58, 0.12);
}
html.dark .queue-tag {
  background: rgba(103, 194, 58, 0.12);
}
html.dark .queue-tag.queued {
  background: rgba(230, 162, 60, 0.12);
}
html.dark .toolbar-sep {
  background: #3a3f52;
}
html.dark .toolbar-icon-btn:hover {
  background: rgba(127, 138, 248, 0.1);
  color: #7f8af8;
}
html.dark .composer-right :deep(.el-select__wrapper):hover {
  background: #2e3344;
}
</style>
