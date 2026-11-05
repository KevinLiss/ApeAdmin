<template>
  <div class="hermes-sessions-page">
    <!-- 顶部统计卡片（字段与官方 /api/sessions/stats 对齐：total/active_store/archived/messages） -->
    <div class="stats-row">
      <div class="stat-card">
        <el-statistic :value="stats.total ?? 0" title="总会话数">
          <template #suffix>
            <el-icon class="stat-icon"><Clock /></el-icon>
          </template>
        </el-statistic>
      </div>
      <div class="stat-card">
        <el-statistic :value="stats.activeStore ?? 0" title="活跃会话">
          <template #suffix>
            <el-icon class="stat-icon"><Clock /></el-icon>
          </template>
        </el-statistic>
      </div>
      <div class="stat-card">
        <el-statistic :value="stats.archived ?? 0" title="已归档">
          <template #suffix>
            <el-icon class="stat-icon"><Folder /></el-icon>
          </template>
        </el-statistic>
      </div>
      <div class="stat-card">
        <el-statistic :value="stats.messages ?? 0" title="消息总数">
          <template #suffix>
            <el-icon class="stat-icon"><ChatDotRound /></el-icon>
          </template>
        </el-statistic>
      </div>
      <div class="stat-card">
        <el-statistic :value="stats.emptySessions ?? 0" title="空会话数">
          <template #suffix>
            <el-icon class="stat-icon"><Delete /></el-icon>
          </template>
        </el-statistic>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="query"
          placeholder="搜索会话关键词"
          clearable
          :prefix-icon="Search"
          class="search-input"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <!-- 来源过滤下拉（与官方 by_source 统计对齐） -->
        <el-dropdown trigger="click" @command="handleSourceCommand">
          <el-button :icon="Filter">
            {{ sourceLabel }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="">全部来源</el-dropdown-item>
              <el-dropdown-item
                v-for="[src, count] in sourceOptions"
                :key="src"
                :command="src"
              >
                {{ src }}（{{ count }}）
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button :icon="Refresh" @click="loadAll">刷新</el-button>
        <el-button
          type="warning"
          plain
          :icon="Delete"
          :disabled="stats.emptySessions === 0"
          @click="handleClearEmpty"
        >
          清理空会话{{ stats.emptySessions ? `（${stats.emptySessions}）` : '' }}
        </el-button>
        <el-button type="danger" plain :icon="Delete" @click="handlePrune">清理旧会话</el-button>
        <el-button :icon="Upload" @click="triggerImport">导入会话</el-button>
        <input
          ref="importInput"
          type="file"
          accept=".json,.jsonl"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
      <div class="toolbar-right">
        <el-button
          v-if="selection.length"
          type="danger"
          :icon="Delete"
          @click="handleBulkDelete"
        >
          批量删除（{{ selection.length }}）
        </el-button>
      </div>
    </div>

    <!-- 会话表格 -->
    <el-table
      v-loading="loading"
      :data="items"
      stripe
      border
      class="session-table"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="48" />
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="session-title">{{ row.title || '未命名会话' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="preview" label="预览" min-width="260" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="session-preview">{{ row.preview || '…' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="message_count" label="消息数" width="90" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="Number(row.message_count) > 0 ? 'primary' : 'info'" effect="plain">
            {{ row.message_count ?? 0 }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          <span class="time-text">{{ formatTime(row.started_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="source" label="来源" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.source" size="small" effect="plain">{{ row.source }}</el-tag>
          <span v-else class="muted">—</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button size="small" :icon="Download" @click="handleExport(row)">导出</el-button>
          <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && !items.length" description="暂无会话" />

    <!-- 分页 -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="limit"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="loadSessions"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Refresh, Search, Download, Clock, Folder, ChatDotRound, Filter, ArrowDown, Upload } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

// ── 状态 ──────────────────────────────────────────
const loading = ref(false)
const items = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const limit = ref(20)
const query = ref('')
const selection = ref<any[]>([])
const stats = reactive<{
  total: number
  activeStore: number
  archived: number
  messages: number
  emptySessions: number
  bySource?: Record<string, number>
}>({
  total: 0,
  activeStore: 0,
  archived: 0,
  messages: 0,
  emptySessions: 0,
  bySource: undefined,
})

// 来源过滤 + 导入 + 清理
const sourceFilter = ref('') // '' = 全部
const importInput = ref<HTMLInputElement | null>(null)
const sourceOptions = computed(() =>
  Object.entries(stats.bySource ?? {}).sort((a, b) => b[1] - a[1]),
)
const sourceLabel = computed(() =>
  sourceFilter.value ? `${sourceFilter.value}（过滤中）` : '全部来源',
)

function handleSourceCommand(src: string) {
  sourceFilter.value = src
  page.value = 1
  loadSessions()
}

function triggerImport() {
  importInput.value?.click()
}

async function handleImportFile(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  try {
    const text = await file.text()
    // 兼容单对象/数组/JSONL
    let data: any[] = []
    const trimmed = text.trim()
    if (trimmed.startsWith('[')) {
      data = JSON.parse(trimmed)
    } else if (trimmed.startsWith('{')) {
      data = [JSON.parse(trimmed)]
    } else {
      data = trimmed
        .split(/\r?\n/)
        .filter(Boolean)
        .map((line) => JSON.parse(line))
    }
    const res: any = await hermes.importSessions(data)
    ElMessage.success(
      `导入完成：新增 ${res?.imported ?? 0}，跳过 ${res?.skipped ?? 0}`,
    )
    await loadAll()
  } catch (err: any) {
    ElMessage.error(`导入失败：${err?.message || '文件格式错误'}`)
  }
}

async function handlePrune() {
  try {
    const { value } = await ElMessageBox.prompt(
      '删除多少天前已结束的非活跃会话？（活跃会话不会被清理）',
      '清理旧会话',
      {
        confirmButtonText: '清理',
        cancelButtonText: '取消',
        inputValue: '90',
        inputPattern: /^\d+$/,
        inputErrorMessage: '请输入天数',
      },
    )
    const res: any = await hermes.pruneSessions(parseInt(value, 10), sourceFilter.value || undefined)
    ElMessage.success(`已清理 ${res?.deleted ?? 0} 个旧会话`)
    await loadAll()
  } catch (e: any) {
    if (e === 'cancel' || e?.message === 'cancel') return
    ElMessage.error(e?.message || '清理旧会话失败')
  }
}

// ── 工具函数 ──────────────────────────────────────
function formatTime(epochSeconds?: number | null): string {
  if (epochSeconds == null || epochSeconds === 0) return '—'
  // started_at 为 epoch 秒，转成毫秒再格式化
  return new Date(Number(epochSeconds) * 1000).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

// ── 数据加载 ──────────────────────────────────────
async function loadSessions() {
  loading.value = true
  try {
    const params: any = {
      limit: limit.value,
      offset: (page.value - 1) * limit.value,
      q: query.value || undefined,
    }
    if (sourceFilter.value) {
      params.sources = sourceFilter.value
    }
    const res: any = await hermes.getSessions(params)
    items.value = res?.sessions ?? res?.items ?? []
    total.value = res?.total ?? items.value.length
    // 若当前页已被删空，回退一页
    if (!items.value.length && page.value > 1) {
      page.value -= 1
      await loadSessions()
      return
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '加载会话列表失败')
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const [res, empty]: any[] = await Promise.all([
      hermes.getSessionStats(),
      hermes.getEmptySessionsCount(),
    ])
    stats.total = res?.total ?? 0
    stats.activeStore = res?.active_store ?? 0
    stats.archived = res?.archived ?? 0
    stats.messages = res?.messages ?? 0
    stats.emptySessions = empty?.count ?? 0
    stats.bySource = res?.by_source
  } catch {
    // 统计失败不影响主流程
  }
}

async function loadAll() {
  await Promise.all([loadSessions(), loadStats()])
}

// ── 搜索 / 分页 ──────────────────────────────────
function handleSearch() {
  page.value = 1
  loadSessions()
}

function handleSizeChange() {
  page.value = 1
  loadSessions()
}

// ── 多选 ─────────────────────────────────────────
function handleSelectionChange(rows: any[]) {
  selection.value = rows
}

// ── 删除 ─────────────────────────────────────────
async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除会话「${row.title || '未命名会话'}」吗？删除后不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return // 用户取消
  }
  try {
    await hermes.deleteSession(row.id)
    ElMessage.success('会话已删除')
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

async function handleBulkDelete() {
  if (!selection.value.length) return
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selection.value.length} 个会话吗？删除后不可恢复。`,
      '批量删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    await hermes.bulkDeleteSessions(selection.value.map((s) => s.id))
    ElMessage.success(`已删除 ${selection.value.length} 个会话`)
    selection.value = []
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.message || '批量删除失败')
  }
}

// ── 清理空会话 ───────────────────────────────────
async function handleClearEmpty() {
  const emptyCount = stats.emptySessions
  if (!emptyCount) return
  try {
    await ElMessageBox.confirm(
      `确定清理全部 ${emptyCount} 个空会话吗？`,
      '清理空会话',
      { type: 'warning', confirmButtonText: '清理', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    const res: any = await hermes.deleteEmptySessions()
    ElMessage.success(`已清理 ${res?.deleted ?? emptyCount} 个空会话`)
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.message || '清理空会话失败')
  }
}

// ── 导出 ─────────────────────────────────────────
function handleExport(row: any) {
  // exportSessionUrl 同步返回导出链接（经 ApeAdmin 代理）
  const url = hermes.exportSessionUrl(row.id)
  if (!url) {
    ElMessage.warning('该会话暂无可导出的内容')
    return
  }
  window.open(url, '_blank')
  ElMessage.success('已生成导出链接')
}

// ── 生命周期 ─────────────────────────────────────
onMounted(loadAll)
</script>

<style scoped>
.hermes-sessions-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

/* 统计卡片 */
.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.stat-card {
  flex: 1;
  max-width: 280px;
  background: #fff;
  border-radius: 8px;
  padding: 20px 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  margin-left: 8px;
  color: #4f46e5;
  font-size: 18px;
  vertical-align: -2px;
}

/* 操作栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.search-input {
  width: 260px;
}

/* 表格 */
.session-table {
  border-radius: 8px;
  overflow: hidden;
}

.session-title {
  font-weight: 500;
  color: #303133;
}

.session-preview {
  color: #909399;
  font-size: 13px;
}

.time-text {
  color: #606266;
  font-size: 13px;
}

.muted {
  color: #c0c4cc;
}

/* 分页 */
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  background: #fff;
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .hermes-sessions-page {
    background: #141414;
  }
  .stat-card,
  .pagination-wrap {
    background: #1f1f1f;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.4);
  }
  .session-title {
    color: #e5eaf3;
  }
  .time-text {
    color: #a3a6ad;
  }
}
</style>