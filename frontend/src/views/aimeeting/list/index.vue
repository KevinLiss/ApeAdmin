<template>
  <div class="aimeeting-page">
    <div class="page-header">
      <h2>AI 会议</h2>
      <p class="text-muted">管理历史会议：查看用户端录制的语音转写文本与 AI 生成的会议纪要</p>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" :loading="creating" @click="quickCreate" v-permission="'aimeeting:meeting:create'">
        <el-icon><Plus /></el-icon> 新建会议
      </el-button>
      <el-button @click="fetchList" :loading="loading">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
      <el-select v-model="filters.status" placeholder="状态" clearable style="width: 130px" @change="fetchList">
        <el-option label="待开始" value="scheduled" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已结束" value="ended" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-input
        v-model="filters.keyword"
        placeholder="搜索标题 / 会议编号"
        clearable
        style="width: 220px"
        @keyup.enter="fetchList"
        @clear="fetchList"
      >
        <template #append>
          <el-button :icon="Search" @click="fetchList" />
        </template>
      </el-input>
      <el-button
        type="danger"
        plain
        :disabled="selectedRows.length === 0"
        :loading="batchDeleting"
        @click="handleBatchDelete"
        v-permission="'aimeeting:meeting:delete'"
      >
        <el-icon><Delete /></el-icon> 批量删除<span v-if="selectedRows.length">（{{ selectedRows.length }}）</span>
      </el-button>
    </div>

    <!-- 列表 -->
    <el-table
      :data="tableData"
      v-loading="loading"
      stripe
      style="width: 100%; margin-top: 16px"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="45" align="center" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="会议标题" min-width="160" show-overflow-tooltip />
      <el-table-column label="会议编号" width="120">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ row.meeting_code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="开始时间" min-width="150">
        <template #default="{ row }">
          <span>{{ fmtDateTime(row.start_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="录音时长" width="90" align="center">
        <template #default="{ row }">
          <span>{{ fmtDuration(row.audio_duration) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'scheduled' || row.status === 'in_progress'"
            link
            type="success"
            size="small"
            @click="openShare(row)"
          >分享会议</el-button>
          <el-button link type="primary" size="small" @click="goDetail(row)">详情</el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)" v-permission="'aimeeting:meeting:delete'">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchList"
        @current-change="fetchList"
      />
    </div>

    <!-- 分享会议弹窗（二维码 + 会议链接，支持多设备扫码进入共享录制） -->
    <el-dialog v-model="shareVisible" title="分享会议" width="360px" align-center>
      <div v-if="shareMeeting" class="share-body">
        <p class="share-title">{{ shareMeeting.title }}</p>
        <p class="share-code">会议编号：{{ shareMeeting.meeting_code }}</p>
        <div class="share-qr">
          <img v-if="shareQrDataUrl" :src="shareQrDataUrl" alt="会议二维码" width="220" height="220" />
          <p v-else class="text-muted">二维码生成中…</p>
        </div>
        <p class="share-tip">手机扫码或在其他设备打开链接即可进入会议<br />多台设备可同时录音，转写内容实时共享</p>
        <div class="share-link-row">
          <el-input :model-value="shareUrl" readonly size="small" />
          <el-button type="primary" size="small" @click="copyShareLink">复制</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="shareVisible = false">关闭</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search, Delete } from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const creating = ref(false)
const selectedRows = ref<any[]>([])
const batchDeleting = ref(false)

const filters = reactive({
  status: '',
  keyword: '',
})

function statusType(s: string) {
  return s === 'in_progress' ? 'warning' : s === 'ended' ? 'success' : s === 'cancelled' ? 'info' : 'primary'
}
function statusText(s: string) {
  return s === 'scheduled' ? '待开始' : s === 'in_progress' ? '进行中' : s === 'ended' ? '已结束' : s === 'cancelled' ? '已取消' : s
}
function fmtDateTime(v?: string | null) {
  if (!v) return '—'
  // 后端混存两类时间：SQLite CURRENT_TIMESTAMP 为 naive UTC（无时区后缀），
  // datetime.now(utc) 序列化带 +00:00/Z。naive 串按 UTC 解析后转本地时区显示，
  // 修复管理端「差 8 小时」问题。
  const raw = String(v)
  let s = raw.replace('T', ' ').slice(0, 19)
  const hasTz = /[zZ]$|[+-]\d{2}:?\d{2}$/.test(raw)
  if (!hasTz) s += 'Z'
  const d = new Date(s.replace(' ', 'T'))
  if (Number.isNaN(d.getTime())) return raw.replace('T', ' ').slice(0, 16)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}
function fmtDuration(sec?: number) {
  if (!sec) return '—'
  const s = Math.floor(sec)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const r = s % 60
  if (h > 0) return `${h}时${m}分`
  if (m > 0) return `${m}分${r}秒`
  return `${r}秒`
}

async function fetchList() {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filters.status) params.status = filters.status
    if (filters.keyword) params.keyword = filters.keyword
    const res: any = await request.get('/aimeeting/meetings', { params })
    tableData.value = res.items || []
    total.value = res.total || 0
    selectedRows.value = []
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function onSelectionChange(rows: any[]) {
  selectedRows.value = rows
}

/** 新建会议：不弹表单，直接创建（标题留空后端自动命名）并跳转 H5 会议页 */
async function quickCreate() {
  creating.value = true
  try {
    const res: any = await request.post('/aimeeting/meetings', {})
    if (res?.id) {
      await fetchList()
      window.location.href = meetingH5Url(res.id)
    }
  } catch {
    // handled by interceptor
  } finally {
    creating.value = false
  }
}

/** H5 用户端地址：优先读 VITE_H5_BASE。
 * 开发环境默认同主机 5177（vite dev server）；生产环境把 H5 dist 与管理端放同域
 * （不同 base 路径或子域名），不设 VITE_H5_BASE 时自动回退为当前 origin。 */
const H5_BASE =
  (import.meta.env?.VITE_H5_BASE as string) ||
  (import.meta.env?.DEV
    ? `${window.location.protocol}//${window.location.hostname}:5177`
    : window.location.origin)

function meetingH5Url(meetingId: number) {
  return `${H5_BASE}/meeting/${meetingId}`
}

// ── 分享会议（二维码 + 链接，多设备扫码共享录制） ──
const shareVisible = ref(false)
const shareMeeting = ref<any | null>(null)
const shareUrl = ref('')
const shareQrDataUrl = ref('')

async function openShare(row: any) {
  shareMeeting.value = row
  shareUrl.value = meetingH5Url(row.id)
  shareQrDataUrl.value = ''
  shareVisible.value = true
  try {
    const QRCode = (await import('qrcode')).default
    shareQrDataUrl.value = await QRCode.toDataURL(shareUrl.value, {
      width: 440,
      margin: 2,
      color: { dark: '#1a1a1a', light: '#ffffff' },
    })
  } catch {
    ElMessage.error('二维码生成失败，可直接复制链接分享')
  }
}

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    ElMessage.success('会议链接已复制')
  } catch {
    // 剪贴板不可用（非安全上下文）时退化为选中文本
    ElMessage.warning('复制失败，请手动选中文本复制')
  }
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除会议「${row.title}」吗？删除后其录音转写记录与纪要一并删除。`, '提示', { type: 'warning' })
  await request.delete(`/aimeeting/meetings/${row.id}`)
  ElMessage.success('删除成功')
  await fetchList()
}

async function handleBatchDelete() {
  if (selectedRows.value.length === 0) return
  const ids = selectedRows.value.map((r) => r.id)
  const titles = selectedRows.value.slice(0, 5).map((r) => r.title).join('、')
  const more = ids.length > 5 ? ` 等 ${ids.length} 个会议` : ''
  try {
    await ElMessageBox.confirm(
      `确定删除「${titles}${more}」吗？删除后其录音转写记录与纪要一并删除，且不可恢复。`,
      '批量删除',
      { type: 'warning', confirmButtonText: `删除 ${ids.length} 个会议`, cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  batchDeleting.value = true
  try {
    const res: any = await request.post('/aimeeting/meetings/batch-delete', { ids })
    ElMessage.success(`已删除 ${res?.deleted ?? ids.length} 个会议`)
    selectedRows.value = []
    await fetchList()
  } catch {
    // handled by interceptor
  } finally {
    batchDeleting.value = false
  }
}

function goDetail(row: any) {
  router.push(`/aimeeting/detail/${row.id}`)
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.aimeeting-page {
  padding: 20px;
}
.page-header {
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0 0 4px;
  font-size: 20px;
}
.page-header .text-muted {
  color: #999;
  font-size: 13px;
  margin: 0;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.pre-wrap {
  white-space: pre-wrap;
  word-break: break-word;
}
/* 分享会议弹窗 */
.share-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.share-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}
.share-code {
  margin: 0;
  font-size: 12px;
  color: #999;
}
.share-qr {
  padding: 8px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.share-tip {
  margin: 0;
  font-size: 12px;
  color: #999;
  text-align: center;
  line-height: 1.6;
}
.share-link-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
</style>