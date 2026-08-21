<template>
  <div class="chat-page">
    <!-- 顶部工具栏 -->
    <div class="chat-header">
      <div class="chat-header-left">
        <el-icon :size="22" color="#5A67F5"><ChatDotRound /></el-icon>
        <span class="chat-title">AI 智能助手</span>
        <el-tag v-if="currentProvider" size="small" type="primary" class="provider-tag">
          {{ currentProvider.name }}
        </el-tag>
      </div>
      <div class="chat-header-right">
        <el-select
          v-model="selectedProviderId"
          placeholder="选择模型"
          style="width: 180px"
          @change="onProviderChange"
        >
          <el-option
            v-for="p in providers"
            :key="p.id"
            :label="p.name"
            :value="p.id"
          />
        </el-select>
        <el-tooltip content="清空对话" placement="bottom">
          <el-button circle @click="clearChat">
            <el-icon><Delete /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 消息区域 -->
    <div ref="messagesRef" class="chat-messages" @scroll="handleScroll">
      <!-- 欢迎提示 -->
      <div v-if="messages.length === 0" class="chat-welcome">
        <el-icon :size="48" color="#5A67F5"><ChatDotRound /></el-icon>
        <h3>欢迎使用 ApeAdmin AI 助手</h3>
        <p>我可以帮您查询系统数据、管理用户、分析信息</p>
        <div class="welcome-suggestions">
          <div
            v-for="s in suggestions"
            :key="s"
            class="suggestion-item"
            @click="sendQuickMessage(s)"
          >
            <el-icon><Pointer /></el-icon>
            <span>{{ s }}</span>
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
          <el-icon v-if="msg.role === 'user'" :size="20" color="#fff"><User /></el-icon>
          <el-icon v-else :size="20" color="#fff"><ChatDotRound /></el-icon>
        </div>
        <div class="message-body">
          <div class="message-role">{{ msg.role === 'user' ? '我' : 'AI 助手' }}</div>
          <!-- 工具调用状态 -->
          <div v-if="msg.toolEvents && msg.toolEvents.length" class="tool-events">
            <div v-for="(te, j) in msg.toolEvents" :key="j" class="tool-event">
              <el-icon :size="14" :color="te.type === 'tool_result' ? '#67c23a' : '#5A67F5'">
                <Loading v-if="te.type === 'tool_call'" class="is-loading" />
                <CircleCheck v-else />
              </el-icon>
              <span class="tool-name">{{ te.name }}</span>
              <span class="tool-args">{{ formatToolArgs(te.arguments) }}</span>
            </div>
          </div>
          <!-- 消息内容 -->
          <div v-if="msg.content" class="message-content markdown-body" v-html="renderMarkdown(msg.content)"></div>
          <!-- 错误信息 -->
          <div v-if="msg.error" class="message-error">
            <el-icon><WarningFilled /></el-icon>
            {{ msg.error }}
          </div>
          <!-- 正在输入指示 -->
          <div v-if="msg.streaming && !msg.content" class="typing-indicator">
            <span></span><span></span><span></span>
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
          placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
          resize="none"
          @keydown.enter.exact.prevent="sendMessage"
        />
        <div class="input-actions">
          <el-tooltip content="启用工具调用" placement="top">
            <el-switch v-model="enableTools" size="small" />
          </el-tooltip>
          <el-button
            v-if="!streaming"
            type="primary"
            :disabled="!inputText.trim()"
            @click="sendMessage"
          >
            <el-icon><Promotion /></el-icon>发送
          </el-button>
          <el-button v-else type="danger" @click="stopStreaming">
            <el-icon><VideoPause /></el-icon>停止
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getAllProviders, chatStream } from '@/api'
import { marked } from 'marked'

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

const messagesRef = ref<HTMLElement>()
const inputText = ref('')
const streaming = ref(false)
const enableTools = ref(true)
const providers = ref<any[]>([])
const selectedProviderId = ref<number | null>(null)
const messages = ref<Message[]>([])
let abortController: AbortController | null = null

const currentProvider = computed(() =>
  providers.value.find((p) => p.id === selectedProviderId.value)
)

const suggestions = [
  '查询系统所有用户',
  '系统有哪些角色？',
  '获取系统统计信息',
  '查看菜单树结构',
]

// Markdown 渲染
marked.setOptions({
  breaks: true,
  gfm: true,
})

function renderMarkdown(text: string): string {
  try {
    return marked.parse(text) as string
  } catch {
    return text
  }
}

function formatToolArgs(args: any): string {
  if (!args || typeof args !== 'object') return ''
  const entries = Object.entries(args)
  if (entries.length === 0) return ''
  return entries.map(([k, v]) => `${k}=${v}`).join(', ')
}

async function loadProviders() {
  try {
    const data: any = await getAllProviders()
    providers.value = data || []
    if (providers.value.length > 0 && !selectedProviderId.value) {
      selectedProviderId.value = providers.value[0].id
    }
  } catch {
    providers.value = []
  }
}

function onProviderChange() {
  // 切换供应商时不需要额外操作
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function handleScroll() {
  // 预留：检测用户是否手动滚动
}

function sendQuickMessage(text: string) {
  inputText.value = text
  sendMessage()
}

function buildMessagesForApi(): Array<{ role: string; content: string }> {
  // 只发送 user 和 assistant 的 content（不含 tool events）
  return messages.value
    .filter((m) => m.content || m.role === 'user')
    .map((m) => ({
      role: m.role,
      content: m.content || '',
    }))
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || streaming.value) return

  if (providers.value.length === 0) {
    ElMessage.warning('请先在「模型密钥管理」中添加模型供应商')
    return
  }

  // 添加用户消息
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''

  // 添加 assistant 占位
  const assistantMsg: Message = {
    role: 'assistant',
    content: '',
    streaming: true,
    toolEvents: [],
  }
  messages.value.push(assistantMsg)

  streaming.value = true
  scrollToBottom()

  // 构建 API 请求的消息列表（含当前用户消息）
  const apiMessages = buildMessagesForApi()
  // 最后一条是空的 assistant 占位，移除它
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
  // 标记最后一条消息为完成
  const last = messages.value[messages.value.length - 1]
  if (last && last.streaming) {
    last.streaming = false
    if (!last.content) {
      last.content = '（已停止）'
    }
  }
}

function clearChat() {
  messages.value = []
}

onMounted(() => {
  loadProviders()
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}
.chat-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.provider-tag {
  margin-left: 4px;
}
.chat-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
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
  padding: 40px;
}
.chat-welcome h3 {
  margin: 16px 0 8px;
  font-size: 20px;
  color: #303133;
}
.chat-welcome p {
  color: #909399;
  font-size: 14px;
  margin-bottom: 24px;
}
.welcome-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  max-width: 600px;
}
.suggestion-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.2s;
}
.suggestion-item:hover {
  border-color: #5A67F5;
  color: #5A67F5;
  background: rgba(90, 103, 245, 0.05);
}

/* Message row */
.message-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 900px;
}
.message-row.user {
  flex-direction: row-reverse;
}
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.message-row.user .message-avatar {
  background: #5A67F5;
}
.message-row.assistant .message-avatar {
  background: linear-gradient(135deg, #5A67F5, #47D8FF);
}
.message-body {
  flex: 1;
  min-width: 0;
}
.message-role {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}
.message-row.user .message-body {
  text-align: right;
}

/* Message content */
.message-content {
  display: inline-block;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  text-align: left;
  word-break: break-word;
}
.message-row.user .message-content {
  background: #5A67F5;
  color: #fff;
  border-top-right-radius: 4px;
}
.message-row.assistant .message-content {
  background: #fff;
  color: #303133;
  border: 1px solid #ebeef5;
  border-top-left-radius: 4px;
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
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Consolas', monospace;
}
.message-row.assistant .markdown-body :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}
.message-row.assistant .markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
  color: inherit;
}
.message-row.assistant .markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
}
.message-row.assistant .markdown-body :deep(th),
.message-row.assistant .markdown-body :deep(td) {
  border: 1px solid #ebeef5;
  padding: 6px 12px;
  text-align: left;
}
.message-row.assistant .markdown-body :deep(th) {
  background: #f5f7fa;
  font-weight: 600;
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
  background: rgba(90, 103, 245, 0.06);
  border-radius: 6px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 2px;
}
.tool-name {
  font-weight: 600;
  color: #5A67F5;
}
.tool-args {
  color: #909399;
}

/* Error */
.message-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fef0f0;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 13px;
}

/* Typing indicator */
.typing-indicator {
  display: inline-flex;
  gap: 4px;
  padding: 10px 16px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
}
.typing-indicator span {
  width: 8px;
  height: 8px;
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
  padding: 12px 20px 16px;
  background: #fff;
  border-top: 1px solid #ebeef5;
  flex-shrink: 0;
}
.chat-input-wrapper {
  max-width: 900px;
  margin: 0 auto;
}
.input-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
</style>
