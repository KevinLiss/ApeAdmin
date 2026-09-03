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
            <el-icon class="session-item-icon" :size="15"><ChatDotRound /></el-icon>
            <span class="session-item-title" :title="s.title">{{ s.title }}</span>
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
      <!-- 顶部工具栏 -->
      <div class="chat-header">
        <div class="chat-header-left">
          <button v-if="isMobile" class="icon-btn" @click="sessionDrawerOpen = true">
            <el-icon :size="18"><Menu /></el-icon>
          </button>
          <span class="chat-title">AI 全能助手</span>
        </div>
        <div class="chat-header-right">
          <!-- 供应商 + 模型 二级选择（替代原双标签 bug） -->
          <el-select
            v-model="selectedProviderId"
            placeholder="供应商"
            class="provider-select"
            size="default"
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
            size="default"
            :disabled="modelOptions.length === 0"
            @change="saveModelChoice"
          >
            <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
          </el-select>
          <el-tooltip content="清空当前对话" placement="bottom">
            <button class="icon-btn" @click="clearChat">
              <el-icon :size="16"><Delete /></el-icon>
            </button>
          </el-tooltip>
        </div>
      </div>

      <!-- 消息区域 -->
      <div ref="messagesRef" class="chat-messages" @scroll="handleScroll">
        <!-- 欢迎提示 -->
        <div v-if="messages.length === 0" class="chat-welcome">
          <div class="welcome-logo">
            <el-icon :size="30" color="#fff"><ChatDotRound /></el-icon>
          </div>
          <h3>有什么可以帮您？</h3>
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
          v-for="(msg, i) in messages"
          :key="i"
          class="message-row"
          :class="msg.role"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'" :size="18" color="#fff"><User /></el-icon>
            <el-icon v-else :size="18" color="#fff"><ChatDotRound /></el-icon>
          </div>
          <div class="message-body">
            <div class="message-meta">
              <span class="message-role">{{ msg.role === 'user' ? '我' : 'AI 助手' }}</span>
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
            <!-- 错误信息 -->
            <div v-if="msg.error" class="message-error">
              <el-icon><WarningFilled /></el-icon>
              {{ msg.error }}
            </div>
            <!-- 正在输入指示 -->
            <div v-if="msg.streaming && !msg.content" class="typing-indicator">
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

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="chat-input-wrapper">
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="2"
            :autosize="{ minRows: 2, maxRows: 6 }"
            placeholder="输入消息，Enter 发送，Shift+Enter 换行"
            resize="none"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="input-actions">
            <div class="input-actions-left">
              <el-tooltip content="启用工具调用（允许 AI 查询/操作系统数据）" placement="top">
                <div class="tools-toggle">
                  <el-icon :size="14"><SetUp /></el-icon>
                  <span>工具</span>
                  <el-switch v-model="enableTools" size="small" />
                </div>
              </el-tooltip>
            </div>
            <div class="input-actions-right">
              <span class="char-count" v-if="inputText.length">{{ inputText.length }}</span>
              <el-button
                v-if="!streaming"
                type="primary"
                :disabled="!inputText.trim()"
                @click="sendMessage"
              >
                <el-icon><Promotion /></el-icon><span class="send-label">发送</span>
              </el-button>
              <el-button v-else type="danger" @click="stopStreaming">
                <el-icon><VideoPause /></el-icon>停止
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getAllProviders,
  chatStream,
  getChatSessions,
  createChatSession,
  getChatSessionMessages,
  deleteChatSession,
  appendChatMessage,
} from '@/api'
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

interface Message {
  role: 'user' | 'assistant'
  content: string
  streaming?: boolean
  error?: string
  toolEvents?: ToolEvent[]
}

interface ChatSessionItem {
  id: number
  title: string
  message_count: number
  updated_at: string
}

const messagesRef = ref<HTMLElement>()
const inputText = ref('')
const streaming = ref(false)
const enableTools = ref(true)
const providers = ref<any[]>([])
const selectedProviderId = ref<number | null>(null)
const selectedModel = ref<string>('')
const messages = ref<Message[]>([])
const sessions = ref<ChatSessionItem[]>([])
const activeSessionId = ref<number | null>(null)
const sessionDrawerOpen = ref(false)
const isMobile = ref(window.innerWidth <= 991)
let abortController: AbortController | null = null

const STORAGE_KEY = 'apeadmin_ai_chat_pref'

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
    // DOMPurify 清洗，防 XSS；保留 code class 供 Prism 高亮
    const clean = DOMPurify.sanitize(html, {
      ADD_ATTR: ['target'],
    })
    return clean
  } catch {
    return DOMPurify.sanitize(text)
  }
}

/** 渲染完成后对消息区做语法高亮 */
function highlightCode() {
  nextTick(() => {
    if (!messagesRef.value) return
    messagesRef.value.querySelectorAll('pre code').forEach((el) => {
      if (!el.classList.contains('language-marked')) {
        el.classList.add('language-marked')
        try {
          Prism.highlightElement(el as HTMLElement)
        } catch {
          /* 高亮失败忽略，保持原文本 */
        }
      }
    })
  })
}

watch(() => messages.value.map((m) => m.content).join(''), highlightCode)

function formatToolArgs(args: any): string {
  if (!args || typeof args !== 'object') return ''
  const entries = Object.entries(args)
  if (entries.length === 0) return ''
  return entries.map(([k, v]) => `${k}=${v}`).join(', ')
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
      // 模型默认选中：已保存的 > 供应商列表第一个
      if (!modelOptions.value.includes(selectedModel.value)) {
        selectedModel.value = modelOptions.value[0] || ''
      }
    }
  } catch {
    providers.value = []
  }
}

function onProviderChange() {
  // 切换供应商后重置模型为该供应商第一个
  selectedModel.value = modelOptions.value[0] || ''
  saveModelChoice()
}

// ---------- 会话管理 ----------
async function loadSessions() {
  try {
    const data: any = await getChatSessions()
    sessions.value = data?.items || []
  } catch {
    sessions.value = []
  }
}

async function newSession() {
  messages.value = []
  activeSessionId.value = null
  sessionDrawerOpen.value = false
}

async function ensureSession(): Promise<number | null> {
  if (activeSessionId.value) return activeSessionId.value
  try {
    const data: any = await createChatSession()
    const s = data
    activeSessionId.value = s.id
    sessions.value.unshift({ id: s.id, title: s.title, message_count: 0, updated_at: s.updated_at })
    return s.id
  } catch {
    return null // 会话保存失败不阻塞对话
  }
}

async function switchSession(id: number) {
  if (streaming.value) {
    ElMessage.warning('AI 正在回复，请稍候')
    return
  }
  activeSessionId.value = id
  sessionDrawerOpen.value = false
  try {
    const data: any = await getChatSessionMessages(id)
    const list = data?.messages || []
    messages.value = list.map((m: any) => ({
      role: m.role,
      content: m.content,
      toolEvents: m.tool_events || [],
    }))
    scrollToBottom()
  } catch {
    ElMessage.error('加载会话失败')
  }
}

async function confirmDeleteSession(s: ChatSessionItem) {
  try {
    await ElMessageBox.confirm(`删除会话「${s.title}」？删除后不可恢复`, '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteChatSession(s.id)
    sessions.value = sessions.value.filter((x) => x.id !== s.id)
    if (activeSessionId.value === s.id) {
      activeSessionId.value = null
      messages.value = []
    }
    ElMessage.success('会话已删除')
  } catch {
    /* 用户取消 */
  }
}

async function persistMessage(role: 'user' | 'assistant', content: string, toolEvents?: ToolEvent[]) {
  const sid = await ensureSession()
  if (!sid) return
  try {
    await appendChatMessage(sid, { role, content, tool_events: toolEvents || null })
    // 更新侧栏标题/计数
    const s = sessions.value.find((x) => x.id === sid)
    if (s) {
      s.message_count += 1
      if (role === 'user' && s.title === '新对话') s.title = content.slice(0, 50)
    }
  } catch {
    /* 保存失败不阻塞对话 */
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
  // 距底部 80px 内视为跟随滚动
  autoScroll = el.scrollHeight - el.scrollTop - el.clientHeight < 80
}

// ---------- 发送 ----------
function sendQuickMessage(text: string) {
  inputText.value = text
  sendMessage()
}

function buildMessagesForApi(): Array<{ role: string; content: string }> {
  return messages.value
    .filter((m) => m.content || m.role === 'user')
    .map((m) => ({ role: m.role, content: m.content || '' }))
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || streaming.value) return

  if (providers.value.length === 0) {
    ElMessage.warning('请先在「模型密钥管理」中添加模型供应商')
    return
  }

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''

  const assistantMsg: Message = {
    role: 'assistant',
    content: '',
    streaming: true,
    toolEvents: [],
  }
  messages.value.push(assistantMsg)

  streaming.value = true
  autoScroll = true
  scrollToBottom(true)

  // 异步持久化用户消息
  persistMessage('user', text)

  const apiMessages = buildMessagesForApi()
  if (apiMessages.length > 0 && apiMessages[apiMessages.length - 1].role === 'assistant' && !apiMessages[apiMessages.length - 1].content) {
    apiMessages.pop()
  }

  const reqBody: any = {
    messages: apiMessages,
    enable_tools: enableTools.value,
  }
  if (selectedProviderId.value) {
    reqBody.provider_id = selectedProviderId.value
  }
  if (selectedModel.value) {
    reqBody.model = selectedModel.value
  }

  abortController = chatStream(reqBody, (event: any) => {
    if (event.type === 'content') {
      assistantMsg.content += event.content
      scrollToBottom()
    } else if (event.type === 'tool_call') {
      assistantMsg.toolEvents!.push({
        type: 'tool_call',
        name: event.name,
        arguments: event.arguments,
      })
      scrollToBottom()
    } else if (event.type === 'tool_result') {
      assistantMsg.toolEvents!.push({
        type: 'tool_result',
        name: event.name,
        result: event.result,
      })
      scrollToBottom()
    } else if (event.type === 'done') {
      assistantMsg.streaming = false
      streaming.value = false
      scrollToBottom()
      persistMessage('assistant', assistantMsg.content, assistantMsg.toolEvents)
    } else if (event.type === 'error') {
      assistantMsg.streaming = false
      assistantMsg.error = event.message || '请求失败'
      streaming.value = false
    }
  })
}

function stopStreaming() {
  if (abortController) {
    abortController.abort()
    abortController = null
  }
  streaming.value = false
  const last = messages.value[messages.value.length - 1]
  if (last && last.streaming) {
    last.streaming = false
    if (!last.content) {
      last.content = '（已停止）'
    } else {
      persistMessage('assistant', last.content, last.toolEvents)
    }
  }
}

function clearChat() {
  if (messages.value.length === 0) return
  ElMessageBox.confirm('清空当前对话显示？（历史消息已保存在会话中，可从左侧切换回来）', '提示', {
    confirmButtonText: '清空',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      messages.value = []
      activeSessionId.value = null
    })
    .catch(() => {})
}

// ---------- 复制 ----------
async function copyMessage(msg: Message) {
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

onMounted(() => {
  window.addEventListener('resize', onResize)
  loadProviders()
  loadSessions()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  if (abortController) abortController.abort()
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
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-regular, #606266);
  font-size: 13px;
  transition: background 0.15s;
}
.session-item:hover {
  background: var(--fill-hover, #f5f7fa);
}
.session-item.active {
  background: var(--el-color-primary-light-9, #ecf0ff);
  color: var(--el-color-primary, #5a67f5);
}
.session-item-icon {
  flex-shrink: 0;
}
.session-item-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--theme-card-bg, #fff);
  border-bottom: 1px solid var(--border-light, #ebeef5);
  flex-shrink: 0;
  gap: 8px;
}
.chat-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.chat-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  white-space: nowrap;
}
.chat-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.provider-select {
  width: 150px;
}
.model-select {
  width: 180px;
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
  padding: 20px;
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
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 24px;
}
.welcome-logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--el-color-primary, #5a67f5), #47d8ff);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(90, 103, 245, 0.25);
}
.chat-welcome h3 {
  margin: 16px 0 20px;
  font-size: 19px;
  color: var(--text-primary, #303133);
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

/* Message row */
.message-row {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  max-width: 860px;
  margin-left: auto;
  margin-right: auto;
}
.message-row.user {
  flex-direction: row-reverse;
}
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.message-row.user .message-avatar {
  background: var(--el-color-primary, #5a67f5);
}
.message-row.assistant .message-avatar {
  background: linear-gradient(135deg, var(--el-color-primary, #5a67f5), #47d8ff);
}
.message-body {
  flex: 1;
  min-width: 0;
}
.message-meta {
  margin-bottom: 4px;
}
.message-role {
  font-size: 12px;
  color: var(--text-secondary, #909399);
}
.message-row.user .message-meta {
  text-align: right;
}

/* Message content */
.message-content {
  display: inline-block;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.65;
  text-align: left;
  word-break: break-word;
  max-width: 100%;
}
.message-row.user .message-content {
  background: var(--el-color-primary, #5a67f5);
  color: #fff;
  border-top-right-radius: 4px;
}
.message-row.assistant .message-content {
  background: var(--theme-card-bg, #fff);
  color: var(--text-primary, #303133);
  border: 1px solid var(--border-light, #ebeef5);
  border-top-left-radius: 4px;
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
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 5px;
  background: transparent;
  color: var(--text-secondary, #909399);
  cursor: pointer;
  transition: all 0.15s;
}
.msg-action-btn:hover {
  background: var(--fill-hover, #f5f7fa);
  color: var(--el-color-primary, #5a67f5);
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

/* Input area */
.chat-input-area {
  padding: 12px 16px 16px;
  background: var(--theme-card-bg, #fff);
  border-top: 1px solid var(--border-light, #ebeef5);
  flex-shrink: 0;
}
.chat-input-wrapper {
  max-width: 860px;
  margin: 0 auto;
}
.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  gap: 8px;
}
.input-actions-left {
  display: flex;
  align-items: center;
}
.tools-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary, #909399);
  cursor: default;
}
.input-actions-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.char-count {
  font-size: 12px;
  color: var(--text-secondary, #909399);
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
  .provider-select {
    width: 118px;
  }
  .model-select {
    width: 128px;
  }
  .chat-messages {
    padding: 14px;
  }
  .message-row {
    gap: 8px;
    margin-bottom: 14px;
  }
  .message-avatar {
    width: 28px;
    height: 28px;
  }
  .message-content {
    font-size: 13.5px;
    padding: 9px 12px;
  }
  .welcome-suggestions {
    grid-template-columns: 1fr;
    width: 100%;
    max-width: 340px;
  }
  .chat-input-area {
    padding: 10px 12px calc(12px + env(safe-area-inset-bottom, 0px));
  }
  .send-label {
    display: none;
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
html.dark .chat-header {
  background: #232838;
  border-bottom-color: #36394a;
}
html.dark .chat-title {
  color: #e6e8f0;
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
html.dark .message-row.assistant .message-content {
  background: #232838;
  color: #e6e8f0;
  border-color: #36394a;
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
html.dark .chat-input-area {
  background: #232838;
  border-top-color: #36394a;
}
html.dark .chat-input-area .el-textarea__inner {
  background: #2e3344;
  border-color: #3a3f52;
  color: #e6e8f0;
}
html.dark .chat-input-area .el-textarea__inner::placeholder {
  color: #6b7089;
}
html.dark .msg-action-btn:hover {
  background: rgba(127, 138, 248, 0.1);
  color: #7f8af8;
}
</style>
