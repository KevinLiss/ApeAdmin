<template>
  <div class="hermes-logs-page">
    <!-- 过滤栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select
          v-model="filters.level"
          placeholder="日志级别"
          style="width: 130px"
          @change="loadLogs"
        >
          <el-option v-for="lv in levels" :key="lv" :label="lv" :value="lv" />
        </el-select>

        <el-select
          v-model="filters.component"
          placeholder="组件"
          style="width: 150px"
          @change="loadLogs"
        >
          <el-option v-for="c in components" :key="c" :label="c" :value="c" />
        </el-select>

        <el-select
          v-model="filters.file"
          placeholder="日志文件"
          style="width: 180px"
          clearable
          filterable
          @change="loadLogs"
        >
          <el-option v-for="f in files" :key="f" :label="f" :value="f" />
        </el-select>

        <el-input-number
          v-model="filters.lines"
          :min="10"
          :max="5000"
          :step="50"
          controls-position="right"
          style="width: 110px"
          @change="loadLogs"
        />

        <el-button :icon="Refresh" :loading="loading" @click="loadLogs">刷新</el-button>
        <el-button :icon="Search" text @click="loadLogs">加载</el-button>
      </div>
      <div class="filter-right">
        <span class="autorefresh-hint">自动刷新</span>
        <el-switch v-model="autoRefresh" @change="handleAutoRefresh" />
        <span v-if="autoRefresh" class="countdown-hint">每 {{ interval }}s</span>
      </div>
    </div>

    <!-- 日志内容区 -->
    <div class="log-card">
      <div class="log-meta">
        <span class="log-file">{{ fileInfo || '暂无文件信息' }}</span>
        <span class="log-count">共 {{ displayLines.length }} 行</span>
      </div>
      <div class="log-scroll" ref="logAreaRef">
        <span
          v-for="(line, i) in displayLines"
          :key="i"
          class="log-line"
          :class="lineClass(line)"
        >
          <span class="line-no">{{ lineNo(i) }}</span>{{ line }}
        </span>
        <div v-if="!displayLines.length && !loading" class="log-empty">暂无日志</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

const levels = ['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR']
const components = ['all', 'agent', 'gateway', 'cli', 'sdk', 'mcp']

const filters = reactive({
  level: 'ALL',
  component: 'all',
  file: '',
  lines: 200,
})

const loading = ref(false)
const displayLines = ref<string[]>([])
const fileInfo = ref('')
const files = ref<string[]>([])

// ── 自动刷新 ──────────────────────────────────────
const autoRefresh = ref(false)
const interval = 10
let timer: ReturnType<typeof setInterval> | null = null

function handleAutoRefresh(on: boolean) {
  if (on) {
    timer = setInterval(loadLogs, interval * 1000)
    loadLogs()
  } else if (timer) {
    clearInterval(timer)
    timer = null
  }
}

// ── 日志加载 ─────────────────────────────────────────
async function loadLogs() {
  loading.value = true
  try {
    const params: Record<string, any> = { lines: filters.lines }
    if (filters.level !== 'ALL') params.level = filters.level
    if (filters.component && filters.component !== 'all') params.component = filters.component
    if (filters.file) params.file = filters.file

    const res: any = await hermes.getLogs(params)
    if (Array.isArray(res?.lines)) {
      displayLines.value = res.lines
    } else if (typeof res?.logs === 'string') {
      displayLines.value = res.logs.split('\n').filter((l: string) => l !== '')
    } else if (Array.isArray(res)) {
      displayLines.value = res
    } else {
      displayLines.value = []
    }
    fileInfo.value = res?.file ?? filters.file ?? ''
    if (Array.isArray(res?.files)) {
      files.value = res.files
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '获取日志失败')
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

// ── 行着色与行号 ──────────────────────────────────────
function lineClass(line: string): string {
  if (/\[(ERROR|CRITICAL|FATAL)\]/.test(line) || /\bERROR\b/i.test(line)) return 'error'
  if (/\[(WARNING|WARN)\]/.test(line) || /\bWARNING\b/i.test(line)) return 'warning'
  if (/\[DEBUG\]/.test(line) || /\bDEBUG\b/i.test(line)) return 'debug'
  return ''
}

const lineNoStart = ref(1)

function lineNo(i: number): number {
  return lineNoStart.value + i
}

// ── 滚动到底部 ─────────────────────────────────────────
const logAreaRef = ref<HTMLElement>()

async function scrollToBottom() {
  await nextTick()
  if (logAreaRef.value) {
    logAreaRef.value.scrollTop = logAreaRef.value.scrollHeight
  }
}

onMounted(loadLogs)
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.hermes-logs-page {
  padding: 16px;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  padding: 12px 14px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.autorefresh-hint,
.countdown-hint {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.log-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  overflow: hidden;
}

.log-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
}

.log-file {
  font-family: 'SF Mono', 'Monaco', monospace;
  color: var(--el-text-color-secondary);
}

.log-count {
  color: var(--el-text-color-secondary);
}

.log-scroll {
  height: calc(100vh - 300px);
  min-height: 320px;
  overflow-y: auto;
  padding: 12px 14px;
  background: var(--el-fill-color-light);
}

.log-line {
  display: block;
  font-family: 'SF Mono', 'Monaco', monospace;
  font-size: 12.5px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--el-text-color-regular);
}

.log-line.error {
  color: #f56c6c;
}

.log-line.warning {
  color: #e6a23c;
}

.log-line.debug {
  color: var(--el-text-color-secondary);
}

.line-no {
  display: inline-block;
  min-width: 52px;
  margin-right: 12px;
  text-align: right;
  color: var(--el-text-color-placeholder);
  user-select: none;
}

.log-empty {
  padding: 40px 0;
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>