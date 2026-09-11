<template>
  <div class="aimeeting-detail-page" v-loading="pageLoading">
    <!-- 顶部：返回 + 标题 -->
    <div class="page-header">
      <el-button link @click="goBack">
        <el-icon><ArrowLeft /></el-icon> 返回列表
      </el-button>
      <div class="header-row">
        <h2>{{ meeting?.title || '会议详情' }}</h2>
        <div class="header-ops">
          <el-button v-if="canGenerate" size="small" :loading="generating" @click="generateMinutes" v-permission="'aimeeting:minutes:generate'">
            <el-icon><MagicStick /></el-icon> {{ minutes?.status === 'success' ? '重新生成纪要' : '生成纪要' }}
          </el-button>
          <el-button size="small" :disabled="!minutesContent" @click="doExport('md')">
            <el-icon><Download /></el-icon> 导出 MD
          </el-button>
          <el-button size="small" :disabled="!minutesContent" @click="doExport('docx')">
            <el-icon><Document /></el-icon> 导出 Word
          </el-button>
          <el-button size="small" @click="fetchAll">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </div>
      <div v-if="meeting" class="meta">
        <el-tag size="small" effect="plain">{{ meeting.meeting_code }}</el-tag>
        <el-tag :type="statusType(meeting.status)" size="small">{{ statusText(meeting.status) }}</el-tag>
        <span class="text-muted">创建人：{{ meeting.creator_name || '—' }}</span>
        <span class="text-muted">录音 {{ fmtDuration(meeting.audio_duration) }}</span>
        <span class="text-muted" v-if="meeting.speakers?.length">说话人 {{ meeting.speakers.length }} 人</span>
      </div>
    </div>

    <!-- 会议信息 -->
    <el-card v-if="meeting" class="info-card" shadow="never">
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="会议编号">{{ meeting.meeting_code || '—' }}</el-descriptions-item>
        <el-descriptions-item label="预约时间">{{ fmtDateTime(meeting.start_time) }}</el-descriptions-item>
        <el-descriptions-item label="参会人">{{ meeting.participants || '—' }}</el-descriptions-item>
        <el-descriptions-item label="实际开始">{{ fmtDateTime(meeting.actual_start) }}</el-descriptions-item>
        <el-descriptions-item label="实际结束">{{ fmtDateTime(meeting.actual_end) }}</el-descriptions-item>
        <el-descriptions-item label="录音时长">{{ fmtDuration(meeting.audio_duration) }}</el-descriptions-item>
        <el-descriptions-item label="转写状态">
          <el-tag :type="transcriptType(meeting.transcript_status)" size="small">{{ transcriptText(meeting.transcript_status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="说话人分离">
          <el-tag :type="meeting.diarization_status === 'success' ? 'success' : 'info'" size="small" effect="plain">{{ diarText(meeting.diarization_status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="纪要状态">
          <el-tag :type="minutesStatusType" size="small" effect="plain">{{ minutesStatusText }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- ── 主体：三 Tab ── -->
    <el-card class="section-card" shadow="never" body-class="tab-body">
      <el-tabs v-model="activeTab">
        <!-- Tab 1：会议记录（转写对话流 + 分段记录） -->
        <el-tab-pane name="records">
          <template #label>会议记录<span class="tab-count" v-if="meeting?.record_count">（{{ meeting.record_count }}）</span></template>

          <el-radio-group v-model="recordsView" size="small" class="records-switch">
            <el-radio-button value="dialogue">对话流</el-radio-button>
            <el-radio-button value="segments">分段记录（{{ records.length }}）</el-radio-button>
          </el-radio-group>

          <!-- 对话流：句级时间戳 + 说话人 -->
          <div v-if="recordsView === 'dialogue'">
            <el-empty v-if="!dialogueSegments.length" description="暂无结构化转写（可能是旧数据，请查看分段记录）" />
            <div v-else class="dialogue-list">
              <div v-for="(seg, i) in dialogueSegments" :key="i" class="dialogue-item">
                <span class="dlg-time">{{ fmtOffset(seg.start) }}</span>
                <span class="dlg-speaker" :style="{ color: speakerColor(seg.speaker) }">
                  {{ speakerName(seg.speaker) }}
                </span>
                <p class="dlg-text">{{ seg.text }}</p>
              </div>
            </div>
          </div>

          <!-- 分段记录：每次上传/每个流式段 -->
          <div v-else>
            <el-empty v-if="recordsLoading && !records.length" description="加载中…" :image-size="60" />
            <el-timeline v-else-if="records.length" style="margin-top: 12px; padding-left: 4px">
              <el-timeline-item
                v-for="rec in records"
                :key="rec.id"
                :timestamp="`[${fmtOffset(rec.offset_sec)} 起 · ${fmtDuration(rec.audio_duration)}] ${fmtDateTime(rec.created_at)}`"
                placement="top"
              >
                <div class="record-item">
                  <div class="record-meta">
                    <el-tag :type="transcriptType(rec.transcript_status)" size="small">{{ transcriptText(rec.transcript_status) }}</el-tag>
                    <el-tag size="small" effect="plain">{{ rec.device_id ? '设备录制' : '后台上传' }}</el-tag>
                  </div>
                  <p class="record-content pre-wrap">{{ rec.transcript || '（本段无转写文本）' }}</p>
                  <p v-if="rec.transcript_status === 'failed' && rec.error" class="record-error">{{ rec.error }}</p>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无录音转写记录" />
          </div>
        </el-tab-pane>

        <!-- Tab 2：会议总结 -->
        <el-tab-pane name="summary">
          <template #label>会议总结</template>
          <el-alert
            v-if="!minutes || minutes.status !== 'success'"
            type="info" :closable="false" show-icon
            title="暂无会议总结：请先在「会议记录」确认转写完成，再点击右上角「生成纪要」"
          />
          <template v-else>
            <div class="summary-card">
              <p class="summary-text pre-wrap">{{ minutes.summary || '（本次纪要未包含一句话总结）' }}</p>
            </div>
            <div v-if="meeting?.transcript_text" class="summary-src">
              <div class="src-title">依据素材（完整转写，共 {{ (meeting.transcript_text || '').length }} 字）</div>
              <div class="pre-wrap transcript-text">{{ meeting.transcript_text }}</div>
            </div>
          </template>
        </el-tab-pane>

        <!-- Tab 3：会议纪要（Markdown 查看 + 编辑） -->
        <el-tab-pane name="minutes">
          <template #label>会议纪要</template>
          <div class="minutes-toolbar" v-if="minutes && minutes.status === 'success'">
            <span class="text-muted" v-if="minutes.provider_name">由 {{ minutes.provider_name }} 生成 · 更新于 {{ fmtDateTime(minutes.updated_at) }}</span>
            <div>
              <el-button size="small" @click="copyMinutes">
                <el-icon><CopyDocument /></el-icon> 复制 Markdown
              </el-button>
              <el-button size="small" type="primary" plain @click="openEdit" v-permission="'aimeeting:minutes:generate'">
                <el-icon><EditPen /></el-icon> 编辑纪要
              </el-button>
            </div>
          </div>
          <el-alert
            v-else-if="minutes && minutes.status === 'pending'"
            type="warning" :closable="false" show-icon title="纪要生成中，请稍候点击刷新…"
          />
          <el-alert
            v-else-if="minutes && minutes.status === 'failed'"
            type="error" :closable="false" show-icon :title="'纪要生成失败：' + (minutes.error || '未知原因')"
          />
          <el-empty v-else description="暂无会议纪要，转写完成后点击「生成纪要」由 AI 自动生成" />

          <!-- Markdown 渲染视图 -->
          <div v-if="minutes && minutes.status === 'success'" class="markdown-body" v-html="minutesHtml"></div>
        </el-tab-pane>

        <!-- Tab 4：说话人 -->
        <el-tab-pane name="speakers" v-if="meeting?.speakers?.length">
          <template #label>说话人（{{ meeting.speakers.length }}）</template>
          <el-table :data="meeting.speakers" size="small" style="max-width: 560px">
            <el-table-column label="说话人" min-width="160">
              <template #default="{ row }">
                <span class="dlg-speaker" :style="{ color: speakerColor(row.speaker_no) }">{{ speakerName(row.speaker_no) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="累计发言" width="120" align="center">
              <template #default="{ row }">{{ fmtDuration(row.total_speak_sec) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 纪要编辑弹窗 -->
    <el-dialog v-model="editVisible" title="编辑会议纪要（Markdown）" width="720px" :close-on-click-modal="false" top="6vh">
      <div class="edit-summary-row">
        <span>一句话总结</span>
        <el-input v-model="editSummary" size="small" maxlength="300" show-word-limit placeholder="会议总结" />
      </div>
      <el-input
        v-model="editContent"
        type="textarea"
        :rows="18"
        placeholder="结构化会议纪要（Markdown：## 标题 / - 列表）"
        class="edit-textarea"
      />
      <div class="edit-preview">
        <div class="src-title">预览</div>
        <div class="markdown-body" v-html="editPreviewHtml"></div>
      </div>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveMinutes">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh, Download, Document, EditPen, CopyDocument, MagicStick } from '@element-plus/icons-vue'
import { marked } from 'marked'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()
const meetingId = Number(route.params.id)

const pageLoading = ref(false)
const meeting = ref<any>(null)
const records = ref<any[]>([])
const recordsLoading = ref(false)
const minutes = ref<any>(null)

const activeTab = ref<'records' | 'summary' | 'minutes' | 'speakers'>('records')
const recordsView = ref<'dialogue' | 'segments'>('dialogue')
const generating = ref(false)

// ── 计算属性 ──
const canGenerate = computed(() => !!meeting.value && meeting.value.status === 'ended')
const minutesContent = computed(() => minutes.value?.status === 'success' ? (minutes.value.minutes || '') : '')
const minutesStatusType = computed(() => {
  const s = meeting.value?.minutes_status || minutes.value?.status
  return s === 'success' ? 'success' : s === 'failed' ? 'danger' : s === 'pending' ? 'warning' : 'info'
})
const minutesStatusText = computed(() => {
  const s = meeting.value?.minutes_status || minutes.value?.status
  return s === 'success' ? '已生成' : s === 'failed' ? '生成失败' : s === 'pending' ? '生成中' : '未生成'
})

// 对话流片段（transcript_json 句级结构：start/end/text/speaker）
const dialogueSegments = computed(() => {
  try {
    const arr = JSON.parse(meeting.value?.transcript_json || '[]')
    return Array.isArray(arr) ? arr.filter((s: any) => s && typeof s === 'object' && !('__merged_record_ids' in s)) : []
  } catch { return [] }
})

// Markdown 渲染（marked + 轻量清洗；纪要由 AI/编辑者产生，非不可信公网输入）
function mdToHtml(md: string) {
  if (!md) return ''
  return marked.parse(md, { async: false }) as string
}
const minutesHtml = computed(() => mdToHtml(minutesContent.value))

// ── 格式化 ──
const speakerColors = ['#4f46e5', '#7c3aed', '#0891b2', '#d97706', '#dc2626', '#059669', '#db2777', '#2563eb']
function speakerColor(no: number) {
  if (!no) return '#909399'
  return speakerColors[(no - 1) % speakerColors.length]
}
function speakerLabel(no: number) {
  if (!no) return '未知'
  return `发言者${String.fromCharCode(64 + ((no - 1) % 26))}${String(no).padStart(3, '0')}`
}
// speaker_no → 显示名映射（声纹分离后用户可能改过真实姓名）
const speakerNameMap = computed(() => {
  const map: Record<number, string> = {}
  for (const s of meeting.value?.speakers || []) {
    if (s.display_name) map[s.speaker_no] = s.display_name
  }
  return map
})
function speakerName(no: number) {
  return speakerNameMap.value[no] || speakerLabel(no)
}
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
function diarText(s?: string) {
  return s === 'success' ? '已分离' : s === 'pending' ? '分离中' : s === 'failed' ? '失败' : '未分离'
}
function fmtDateTime(v?: string | null) {
  if (!v) return '—'
  const raw = String(v)
  let s = raw.replace('T', ' ').slice(0, 19)
  const hasTz = /[zZ]$|[+-]\d{2}:?\d{2}$/.test(raw)
  if (!hasTz) s += 'Z'
  const d = new Date(s.replace(' ', 'T'))
  if (Number.isNaN(d.getTime())) return raw.slice(0, 16)
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
function fmtOffset(start?: number) {
  const s = Math.floor(start || 0)
  const m = Math.floor(s / 60)
  return `${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
}

// ── 数据加载 ──
async function fetchDetail() {
  const res: any = await request.get(`/aimeeting/meetings/${meetingId}`)
  meeting.value = res
}
async function fetchRecords() {
  recordsLoading.value = true
  try {
    const res: any = await request.get(`/aimeeting/meetings/${meetingId}/records`)
    records.value = res || []
  } finally {
    recordsLoading.value = false
  }
}
async function fetchMinutes() {
  const res: any = await request.get(`/aimeeting/meetings/${meetingId}/minutes`)
  minutes.value = res || null
}
async function fetchAll() {
  pageLoading.value = true
  try {
    await Promise.all([fetchDetail(), fetchRecords(), fetchMinutes()])
  } finally {
    pageLoading.value = false
  }
}

async function generateMinutes() {
  generating.value = true
  try {
    const res: any = await request.post(`/aimeeting/meetings/${meetingId}/minutes/generate`)
    minutes.value = res
    if (res?.status === 'success') {
      ElMessage.success('纪要生成成功')
      activeTab.value = 'minutes'
    } else if (res?.status === 'failed') {
      ElMessage.error('纪要生成失败：' + (res?.error || ''))
    } else {
      ElMessage.info('纪要已提交生成，请稍候刷新')
    }
    await fetchDetail()
  } catch {
    // interceptor handled
  } finally {
    generating.value = false
  }
}

// ── 纪要编辑 ──
const editVisible = ref(false)
const editContent = ref('')
const editSummary = ref('')
const saving = ref(false)
const editPreviewHtml = computed(() => mdToHtml(editContent.value))

function openEdit() {
  editContent.value = minutes.value?.minutes || ''
  editSummary.value = minutes.value?.summary || ''
  editVisible.value = true
}
async function saveMinutes() {
  if (!editContent.value.trim()) {
    ElMessage.warning('纪要内容不能为空')
    return
  }
  saving.value = true
  try {
    const res: any = await request.put(`/aimeeting/meetings/${meetingId}/minutes`, {
      minutes: editContent.value,
      summary: editSummary.value,
    })
    minutes.value = res
    editVisible.value = false
    ElMessage.success('纪要已保存')
  } catch {
    // interceptor handled
  } finally {
    saving.value = false
  }
}
async function copyMinutes() {
  try {
    await navigator.clipboard.writeText(minutesContent.value)
    ElMessage.success('Markdown 已复制到剪贴板')
  } catch {
    ElMessage.warning('复制失败，请手动选择复制')
  }
}

// ── 导出（走后端接口下载附件）──
async function doExport(fmt: 'md' | 'docx') {
  try {
    const blob: any = await request.get(`/aimeeting/meetings/${meetingId}/minutes/export`, {
      params: { fmt },
      responseType: 'blob',
      timeout: 60000,
    })
    const title = (meeting.value?.title || `meeting_${meetingId}`).replace(/[\/\\:*?"<>|]/g, '_')
    const ext = fmt === 'docx' ? 'docx' : 'md'
    const url = URL.createObjectURL(blob instanceof Blob ? blob : new Blob([blob]))
    const a = document.createElement('a')
    a.href = url
    a.download = `${title} 纪要.${ext}`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(fmt === 'docx' ? 'Word 文档已开始下载' : 'Markdown 文件已开始下载')
  } catch {
    ElMessage.error('导出失败')
  }
}

function goBack() {
  router.push('/aimeeting/list')
}

onMounted(fetchAll)
</script>

<style scoped>
.aimeeting-detail-page {
  padding: 20px;
}
.page-header { margin-bottom: 16px; }
.header-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; flex-wrap: wrap; margin: 8px 0 4px;
}
.header-row h2 { margin: 0; font-size: 20px; }
.header-ops { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.page-header .meta {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.text-muted { color: #909399; font-size: 13px; }
.info-card, .section-card { margin-bottom: 16px; }
.pre-wrap { white-space: pre-wrap; word-break: break-word; }
.tab-count { color: #909399; font-weight: 400; }
.records-switch { margin-bottom: 12px; }

/* 对话流 */
.dialogue-list { max-height: 620px; overflow: auto; padding: 4px 2px; }
.dialogue-item {
  display: grid; grid-template-columns: 52px 100px 1fr;
  gap: 10px; align-items: baseline;
  padding: 8px 6px; border-bottom: 1px dashed #f0f0f0;
}
.dialogue-item:hover { background: #fafbff; }
.dlg-time { font-size: 12px; color: #909399; font-variant-numeric: tabular-nums; }
.dlg-speaker { font-size: 13px; font-weight: 600; }
.dlg-text { margin: 0; font-size: 14px; color: #303133; line-height: 1.65; word-break: break-word; }

/* 分段记录 */
.record-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.record-content { color: #333; margin: 4px 0; }
.record-error { color: var(--el-color-danger); font-size: 12px; margin: 4px 0 0; }

/* 总结 tab */
.summary-card {
  background: linear-gradient(135deg, #f5f7ff, #eef4ff);
  border: 1px solid #dbe4ff; border-radius: 10px;
  padding: 18px 20px; margin-bottom: 16px;
}
.summary-text { font-size: 15px; line-height: 1.8; color: #1f2937; margin: 0; }
.summary-src { margin-top: 8px; }
.src-title { font-size: 12px; color: #909399; margin-bottom: 6px; }
.transcript-text {
  max-height: 320px; overflow: auto;
  background: var(--el-fill-color-light); border-radius: 6px;
  padding: 12px; font-size: 13px; line-height: 1.7; color: #333;
}

/* 纪要 tab */
.minutes-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px; flex-wrap: wrap; gap: 8px;
}

/* Markdown 渲染 */
.markdown-body { line-height: 1.75; color: #303133; font-size: 14px; }
.markdown-body :deep(h1) { font-size: 20px; margin: 18px 0 10px; }
.markdown-body :deep(h2) { font-size: 17px; margin: 16px 0 8px; padding-left: 8px; border-left: 3px solid var(--el-color-primary); }
.markdown-body :deep(h3) { font-size: 15px; margin: 12px 0 6px; }
.markdown-body :deep(p) { margin: 6px 0; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 22px; margin: 6px 0; }
.markdown-body :deep(li) { margin: 3px 0; }
.markdown-body :deep(strong) { color: #1f2937; }
.markdown-body :deep(table) { border-collapse: collapse; margin: 8px 0; }
.markdown-body :deep(th), .markdown-body :deep(td) { border: 1px solid #e4e7ed; padding: 5px 10px; font-size: 13px; }

/* 编辑弹窗 */
.edit-summary-row {
  display: flex; align-items: center; gap: 10px; margin-bottom: 10px;
  font-size: 13px; color: #606266; white-space: nowrap;
}
.edit-textarea :deep(textarea) { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; line-height: 1.6; }
.edit-preview { margin-top: 12px; border-top: 1px dashed #e4e7ed; padding-top: 10px; max-height: 300px; overflow: auto; }
</style>
