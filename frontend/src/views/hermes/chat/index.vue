<template>
  <div class="hermes-chat-page">
    <!-- 引擎状态栏 -->
    <div class="engine-bar">
      <el-tag :type="engineRunning ? 'success' : 'danger'" size="small" effect="dark">
        <span class="dot" :class="{ online: engineRunning }"></span>
        {{ engineRunning ? '引擎在线' : '引擎离线' }}
      </el-tag>
      <span v-if="enginePid" class="engine-meta">PID {{ enginePid }} · 端口 {{ enginePort }}</span>
      <el-button v-if="!engineRunning" size="small" type="primary" @click="refreshStatus">重试连接</el-button>
    </div>

    <div class="chat-layout" v-loading="wsConnecting">
      <!-- 会话列表 -->
      <aside class="session-panel">
        <div class="session-header">
          <span>会话</span>
          <el-button size="small" type="primary" :icon="Plus" circle @click="newSession" title="新建会话" />
        </div>
        <div class="session-list" v-if="sessions.length">
          <div
            v-for="s in sessions"
            :key="s.id"
            class="session-item"
            :class="{ active: currentSessionId === s.id }"
            @click="switchSession(s)"
          >
            <div class="session-title">{{ s.title || '未命名会话' }}</div>
            <div class="session-preview">{{ s.preview || '…' }}</div>
          </div>
        </div>
        <el-empty v-else description="暂无会话" :image-size="60" />
      </aside>

      <!-- 聊天主区 -->
      <section class="chat-main">
        <div ref="messageListRef" class="message-list">
          <template v-for="(m, idx) in messages" :key="idx">
            <!-- 用户消息 -->
            <div v-if="m.role === 'user'" class="msg-row user">
              <div class="bubble user-bubble">{{ m.text }}</div>
            </div>
            <!-- 助手消息 -->
            <div v-else class="msg-row assistant">
              <div class="avatar">H</div>
              <div class="bubble assistant-bubble">
                <div v-if="m.thinking && m.thinking.length" class="thinking-block">
                  <div v-for="(t, ti) in m.thinking" :key="ti" class="thinking-row">
                    <el-icon class="thinking-icon is-loading"><Loading /></el-icon>{{ t }}
                  </div>
                </div>
                <div v-if="m.streaming && m.text" class="streaming-text" v-html="renderMarkdown(m.text)"></div>
                <div v-else-if="!m.streaming && m.text" class="final-text" v-html="renderMarkdown(m.text)"></div>
                <div v-else-if="m.error" class="error-text">
                  <el-icon><WarningFilled /></el-icon>{{ m.error }}
                </div>
                <div v-else-if="m.status" class="status-line">{{ m.status }}</div>
              </div>
            </div>
          </template>
          <div v-if="isStreaming" class="cursor-blink"></div>
        </div>

        <!-- 输入区 -->
        <div class="input-panel">
          <el-input
            v-model="draft"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="输入消息，Enter 发送，Shift+Enter 换行"
            :disabled="!engineRunning || isStreaming"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="input-actions">
            <span v-if="isStreaming" class="streaming-hint">
              <el-icon class="is-loading"><Loading /></el-icon> AI 思考中…
            </span>
            <span v-else-if="!engineRunning" class="streaming-hint error">引擎离线，无法发送</span>
            <el-button type="primary" :disabled="!draft.trim() || isStreaming || !engineRunning" @click="sendMessage">
              发送
            </el-button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Loading, WarningFilled } from '@element-plus/icons-vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { getHermesStatus } from '@/api/hermes'

// ── 渲染配置 ──────────────────────────────────────
marked.setOptions({ breaks: true, gfm: true })

function renderMarkdown(text: string): string {
  if (!text) return ''
  const raw = marked.parse(text) as string
  return DOMPurify.sanitize(raw)
}

// ── 引擎状态 ──────────────────────────────────────
const engineRunning = ref(false)
const enginePid = ref<number | null>(null)
const enginePort = ref<number | null>(null)
const wsConnecting = ref(false)

async function refreshStatus() {
  try {
    const res: any = await getHermesStatus()
    engineRunning.value = !!res?.running
    enginePid.value = res?.pid ?? null
    enginePort.value = res?.port ?? null
    if (engineRunning.value && (!ws || ws.readyState !== WebSocket.OPEN)) {
      connectWs()
    }
  } catch {
    engineRunning.value = false
  }
}

// ── WS 连接 ──────────────────────────────────────
let ws: WebSocket | null = null
let rpcSeq = 0
const pendingRpc = new Map<number, { resolve: (v: any) => void; reject: (e: Error) => void }>()

const messages = ref<any[]>([])
const sessions = ref<any[]>([])
const currentSessionId = ref<string | null>(null)
const isStreaming = ref(false)
const draft = ref('')
const messageListRef = ref<HTMLElement | null>(null)

function connectWs() {
  const token = localStorage.getItem('apeadmin_token')
  if (!token) {
    ElMessage.error('未登录，请重新登录')
    return
  }
  wsConnecting.value = true
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${proto}://${location.host}/api/v1/hermes/ws?jwt=${encodeURIComponent(token)}`)
  ws.onopen = () => {
    wsConnecting.value = false
    ElMessage.success('已连接到 Hermes 引擎')
    fetchSessions()
  }
  ws.onmessage = (ev) => handleWsFrame(ev.data)
  ws.onclose = () => {
    wsConnecting.value = false
    if (isStreaming.value) {
      isStreaming.value = false
      ElMessage.warning('连接已断开')
    }
  }
  ws.onerror = () => {
    wsConnecting.value = false
    ElMessage.error('WS 连接错误')
  }
}

function handleWsFrame(raw: string) {
  let frame: any
  try {
    frame = JSON.parse(raw)
  } catch {
    return
  }
  // 事件帧
  if (frame.method === 'event') {
    handleEvent(frame.params)
    return
  }
  // RPC 响应帧
  if (frame.id != null && pendingRpc.has(frame.id)) {
    const { resolve, reject } = pendingRpc.get(frame.id)!
    pendingRpc.delete(frame.id)
    if (frame.error) reject(new Error(frame.error?.message || frame.error?.code || 'RPC error'))
    else resolve(frame.result ?? {})
  }
}

function handleEvent(p: any) {
  const type = p?.type
  const payload = p?.payload ?? {}
  switch (type) {
    case 'message.start':
      isStreaming.value = true
      messages.value.push({ role: 'assistant', text: '', thinking: [], streaming: true })
      break
    case 'reasoning.delta':
    case 'thinking.delta': {
      const last = messages.value[messages.value.length - 1]
      if (last?.streaming) {
        const text = payload.text || ''
        if (!last.thinking) last.thinking = []
        const lastLine = last.thinking[last.thinking.length - 1] || ''
        if (lastLine && text.startsWith(lastLine)) {
          last.thinking[last.thinking.length - 1] = text
        } else {
          last.thinking.push(text)
        }
        scrollToBottom()
      }
      break
    }
    case 'message.delta': {
      const last = messages.value[messages.value.length - 1]
      if (last?.streaming) {
        last.text = (last.text || '') + (payload.text || '')
        scrollToBottom()
      }
      break
    }
    case 'message.complete': {
      const last = messages.value[messages.value.length - 1]
      if (last?.streaming) {
        last.streaming = false
        if (payload.error) {
          last.error = payload.error
        } else if (payload.text) {
          last.text = payload.text as string
        }
      }
      isStreaming.value = false
      refreshSessionList()
      scrollToBottom()
      break
    }
    case 'message.error':
    case 'error': {
      const last = messages.value[messages.value.length - 1]
      if (last?.streaming) {
        last.streaming = false
        last.error = payload.text || payload.message || '发生错误'
      }
      isStreaming.value = false
      break
    }
    default:
      break
  }
}

// ── RPC 封装（唯一实现）──────────────────────────
function rpc(method: string, params: any): Promise<any> {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      reject(new Error('WS 未连接'))
      return
    }
    const id = ++rpcSeq
    pendingRpc.set(id, { resolve, reject })
    ws.send(JSON.stringify({ jsonrpc: '2.0', id, method, params }))
  })
}

// ── 会话管理 ──────────────────────────────────────
async function newSession() {
  try {
    const res: any = await rpc('session.create', {})
    currentSessionId.value = res?.session_id ?? null
    messages.value = []
    draft.value = ''
    ElMessage.success('已创建新会话')
  } catch (e: any) {
    ElMessage.error(`创建会话失败: ${e.message}`)
  }
}

async function fetchSessions() {
  try {
    const res: any = await rpc('session.list', { limit: 20 })
    const list = res?.sessions ?? res?.items ?? []
    sessions.value = list
  } catch {
    // 静默失败
  }
}

function refreshSessionList() {
  fetchSessions()
}

async function switchSession(s: any) {
  if (isStreaming.value) {
    ElMessage.warning('AI 正在回复中，请稍候')
    return
  }
  if (s.id === currentSessionId.value) return
  try {
    const res: any = await rpc('session.resume', { session_id: s.id })
    currentSessionId.value = res?.session_id ?? s.id
    const history: any[] = res?.messages ?? []
    messages.value = history
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({
        role: m.role,
        text: m.text || '',
        streaming: false,
      }))
    scrollToBottom()
  } catch (e: any) {
    ElMessage.error(`恢复会话失败: ${e.message}`)
  }
}

// ── 发送消息 ──────────────────────────────────────
async function sendMessage() {
  const text = draft.value.trim()
  if (!text || isStreaming.value || !engineRunning.value) return
  if (!currentSessionId.value) {
    await newSession()
    if (!currentSessionId.value) return
  }
  messages.value.push({ role: 'user', text })
  draft.value = ''
  try {
    await rpc('prompt.submit', { text, session_id: currentSessionId.value })
  } catch (e: any) {
    ElMessage.error(`发送失败: ${e.message}`)
    isStreaming.value = false
  }
}

// ── 滚动 ──────────────────────────────────────────
function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// ── 生命周期 ──────────────────────────────────────
onMounted(() => {
  refreshStatus()
})

onBeforeUnmount(() => {
  if (ws) {
    ws.close()
    ws = null
  }
})
</script>

<style scoped>
.hermes-chat-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  min-height: 480px;
}
.engine-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f56c6c;
  margin-right: 4px;
}
.dot.online {
  background: #67c23a;
}
.engine-meta {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.chat-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.session-panel {
  width: 240px;
  border-right: 1px solid var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
}
.session-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  font-weight: 600;
}
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}
.session-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: background 0.2s;
}
.session-item:hover {
  background: var(--el-fill-color-light);
}
.session-item.active {
  background: var(--el-color-primary-light-9);
}
.session-title {
  font-size: 13px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-preview {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 2px;
}
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.msg-row {
  display: flex;
  margin-bottom: 16px;
  gap: 10px;
}
.msg-row.user {
  justify-content: flex-end;
}
.bubble {
  max-width: 72%;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}
.user-bubble {
  background: var(--el-color-primary);
  color: #fff;
  border-top-right-radius: 2px;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 15px;
  flex-shrink: 0;
}
.assistant-bubble {
  background: var(--el-fill-color-light);
  border-top-left-radius: 2px;
}
.thinking-block {
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--el-border-color-lighter);
}
.thinking-row {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: flex-start;
  gap: 4px;
}
.thinking-icon {
  margin-top: 2px;
}
.error-text {
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-line {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.cursor-blink {
  width: 8px;
  height: 16px;
  background: var(--el-color-primary);
  animation: blink 1s infinite;
  display: inline-block;
  margin-top: 16px;
}
@keyframes blink {
  0%, 50% { opacity: 1; }
  50.01%, 100% { opacity: 0; }
}
.input-panel {
  border-top: 1px solid var(--el-border-color-lighter);
  padding: 12px 16px;
}
.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}
.streaming-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}
.streaming-hint.error {
  color: #f56c6c;
}
</style>