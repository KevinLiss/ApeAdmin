<template>
  <div class="aimeeting-page">
    <div class="page-header">
      <h2>AI 会议</h2>
      <p class="text-muted">管理历史会议：查看用户端录制的语音转写文本与 AI 生成的会议纪要</p>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="openCreate" v-permission="'aimeeting:meeting:create'">
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
          <el-button link type="primary" size="small" @click="viewRecords(row)">记录</el-button>
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

    <!-- 新建会议弹窗 -->
    <el-dialog v-model="dialogVisible" title="新建会议" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="会议标题" required>
          <el-input v-model="form.title" placeholder="请输入会议标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="参会人">
          <el-input v-model="form.participants" placeholder="多个参会人请用逗号分隔" />
        </el-form-item>
        <el-form-item label="会议时间">
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

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

    <!-- 会议记录抽屉 -->
    <el-drawer v-model="recordsVisible" :title="`会议记录 - ${recordsMeeting?.title || ''}`" size="640px">
      <div v-loading="recordsLoading">
        <template v-if="recordsMeeting">
          <el-descriptions :column="2" size="small" border style="margin-bottom: 16px">
            <el-descriptions-item label="会议编号">{{ recordsMeeting.meeting_code }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusType(recordsMeeting.status)" size="small">{{ statusText(recordsMeeting.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ fmtDateTime(recordsMeeting.start_time) }}</el-descriptions-item>
            <el-descriptions-item label="录音时长">{{ fmtDuration(recordsMeeting.audio_duration) }}</el-descriptions-item>
          </el-descriptions>
        </template>

        <el-empty v-if="!recordsLoading && records.length === 0" description="暂无录音转写记录" />
        <el-timeline v-else style="padding-left: 4px">
          <el-timeline-item
            v-for="(rec, idx) in records"
            :key="rec.id"
            :timestamp="`第 ${idx + 1} 段 · ${fmtDateTime(rec.created_at)}`"
            placement="top"
          >
            <div class="record-item">
              <div class="record-meta">
                <el-tag :type="transcriptType(rec.transcript_status)" size="small">
                  {{ transcriptText(rec.transcript_status) }}
                </el-tag>
                <span class="text-muted">时长 {{ fmtDuration(rec.audio_duration) }}</span>
                <span class="text-muted">偏移 {{ fmtDuration(rec.offset_sec) }}</span>
              </div>
              <p class="record-content pre-wrap">{{ rec.transcript || '（本段无转写文本）' }}</p>
              <p v-if="rec.transcript_status === 'failed' && rec.error" class="record-error">{{ rec.error }}</p>
            </div>
          </el-timeline-item>
        </el-timeline>

        <el-card v-if="recordsMeeting?.transcript_text" shadow="never" class="full-transcript">
          <template #header><span>完整转写文本</span></template>
          <div class="pre-wrap transcript-text">{{ recordsMeeting.transcript_text }}</div>
        </el-card>
      </div>
    </el-drawer>
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
const saving = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const selectedRows = ref<any[]>([])
const batchDeleting = ref(false)

// 会议记录抽屉
const recordsVisible = ref(false)
const recordsLoading = ref(false)
const recordsMeeting = ref<any | null>(null)
const records = ref<any[]>([])

const filters = reactive({
  status: '',
  keyword: '',
})

const form = reactive({
  title: '',
  participants: '',
  start_time: null as string | null,
})

function statusType(s: string) {
  return s === 'in_progress' ? 'warning' : s === 'ended' ? 'success' : s === 'cancelled' ? 'info' : 'primary'
}
function statusText(s: string) {
  return s === 'scheduled' ? '待开始' : s === 'in_progress' ? '进行中' : s === 'ended' ? '已结束' : s === 'cancelled' ? '已取消' : s
}
function transcriptType(s?: string) {
  return s === 'success' ? 'success' : s === 'failed' ? 'danger' : s === 'processing' ? 'warning' : 'info'
}
function transcriptText(s?: string) {
  return s === 'success' ? '已完成' : s === 'failed' ? '失败' : s === 'processing' ? '转写中' : '未转写'
}
function fmtDateTime(v?: string | null) {
  if (!v) return '—'
  return String(v).replace('T', ' ').slice(0, 16)
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

function openCreate() {
  Object.assign(form, { title: '', participants: '', start_time: null })
  dialogVisible.value = true
}

/** H5 用户端地址：优先读 VITE_H5_BASE，默认与当前主机同款的 5177 端口 */
const H5_BASE =
  (import.meta.env?.VITE_H5_BASE as string) ||
  `${window.location.protocol}//${window.location.hostname}:5177`

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

async function handleSave() {
  if (!form.title.trim()) {
    ElMessage.warning('请输入会议标题')
    return
  }
  saving.value = true
  try {
    const payload: any = {
      title: form.title.trim(),
      participants: form.participants,
    }
    if (form.start_time) payload.start_time = form.start_time
    const res: any = await request.post('/aimeeting/meetings', payload)
    ElMessage.success('创建成功，分享二维码或链接即可进入会议')
    dialogVisible.value = false
    await fetchList()
    // 创建成功后弹出分享框：扫二维码 / 复制链接，多设备可同时进入共享录制
    if (res?.id) openShare(res)
  } catch {
    // handled by interceptor
  } finally {
    saving.value = false
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

async function viewRecords(row: any) {
  recordsMeeting.value = row
  recordsVisible.value = true
  recordsLoading.value = true
  records.value = []
  try {
    const data: any = await request.get(`/aimeeting/meetings/${row.id}/records`)
    records.value = Array.isArray(data) ? data : []
  } catch {
    // handled by interceptor
  } finally {
    recordsLoading.value = false
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
.record-item .record-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}
.record-item .record-meta .text-muted {
  color: #999;
  font-size: 12px;
}
.record-content {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #333;
}
.record-error {
  margin: 4px 0 0;
  font-size: 12px;
  color: #f56c6c;
}
.full-transcript {
  margin-top: 16px;
}
.transcript-text {
  font-size: 13px;
  line-height: 1.8;
  max-height: 320px;
  overflow: auto;
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