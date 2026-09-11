<template>
  <div class="aimeeting-detail-page">
    <!-- 顶部：返回 + 标题 -->
    <div class="page-header">
      <el-button link @click="goBack">
        <el-icon><ArrowLeft /></el-icon> 返回列表
      </el-button>
      <h2>{{ meeting?.title || '会议详情' }}</h2>
      <div v-if="meeting" class="meta">
        <el-tag size="small" effect="plain">{{ meeting.meeting_code }}</el-tag>
        <el-tag :type="statusType(meeting.status)" size="small">{{ statusText(meeting.status) }}</el-tag>
        <span class="text-muted">创建人：{{ meeting.creator_name }}</span>
        <span class="text-muted">录音 {{ fmtDuration(meeting.audio_duration) }}</span>
      </div>
    </div>

    <!-- 会议信息 -->
    <el-card v-if="meeting" class="info-card" shadow="never">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="会议编号">{{ meeting.meeting_code || '—' }}</el-descriptions-item>
        <el-descriptions-item label="会议时间">
          {{ fmtDateTime(meeting.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="参会人" :span="2">{{ meeting.participants || '—' }}</el-descriptions-item>
        <el-descriptions-item label="实际开始" v-if="meeting.actual_start">{{ fmtDateTime(meeting.actual_start) }}</el-descriptions-item>
        <el-descriptions-item label="实际结束" v-if="meeting.actual_end">{{ fmtDateTime(meeting.actual_end) }}</el-descriptions-item>
        <el-descriptions-item label="录音时长">{{ fmtDuration(meeting.audio_duration) }}</el-descriptions-item>
        <el-descriptions-item label="转写状态">
          <el-tag :type="transcriptType(meeting.transcript_status)" size="small">
            {{ transcriptText(meeting.transcript_status) }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 转写记录 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>录音转写记录</span>
          <el-button size="small" @click="fetchRecords" :loading="recordsLoading">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>

      <el-empty v-if="!recordsLoading && records.length === 0" description="暂无录音转写记录" />
      <el-timeline v-else style="margin-top: 16px; padding-left: 4px">
        <el-timeline-item
          v-for="rec in records"
          :key="rec.id"
          :timestamp="fmtDateTime(rec.created_at)"
          placement="top"
        >
          <div class="record-item">
            <div class="record-main">
              <div class="record-meta">
                <el-tag :type="transcriptType(rec.transcript_status)" size="small">
                  {{ transcriptText(rec.transcript_status) }}
                </el-tag>
                <span class="text-muted">时长 {{ fmtDuration(rec.audio_duration) }}</span>
              </div>
              <p class="record-content pre-wrap">{{ rec.transcript || '（本段无转写文本）' }}</p>
              <p v-if="rec.transcript_status === 'failed' && rec.error" class="record-error">{{ rec.error }}</p>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 完整转写文本 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>完整转写文本</span>
        </div>
      </template>
      <el-empty v-if="!meeting?.transcript_text" description="暂无完整转写文本" />
      <div v-else class="pre-wrap transcript-text">{{ meeting.transcript_text }}</div>
    </el-card>

    <!-- AI 会议纪要 -->
    <el-card class="section-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>AI 会议纪要</span>
          <div>
            <el-button
              type="primary"
              size="small"
              :loading="generating"
              :disabled="!canGenerate"
              @click="generateMinutes"
              v-permission="'aimeeting:minutes:generate'"
            >
              {{ minutes?.status === 'success' ? '重新生成' : '生成纪要' }}
            </el-button>
          </div>
        </div>
      </template>

      <el-alert
        v-if="minutes?.status === 'failed'"
        type="error"
        :closable="false"
        show-icon
        :title="'纪要生成失败：' + (minutes?.error || '')"
        style="margin-bottom: 12px"
      />
      <el-alert
        v-if="minutes?.status === 'pending'"
        type="warning"
        :closable="false"
        show-icon
        title="纪要生成中，请稍候刷新..."
        style="margin-bottom: 12px"
      />
      <el-alert
        v-else-if="minutes?.status === 'none'"
        type="info"
        :closable="false"
        show-icon
        title="会议结束后，点击「生成纪要」由 AI 自动生成会议总结与纪要"
        style="margin-bottom: 12px"
      />

      <template v-if="minutes?.status === 'success'">
        <el-divider content-position="left">会议总结</el-divider>
        <p class="pre-wrap summary-text">{{ minutes.summary }}</p>

        <el-divider content-position="left">会议纪要</el-divider>
        <div class="minutes-body">
          <template v-for="(part, i) in minutesParts" :key="i">
            <h3 v-if="part.type === 'h'" class="minutes-h">{{ part.text }}</h3>
            <ul v-else-if="part.type === 'list'">
              <li v-for="(item, j) in part.items" :key="j" class="minutes-li">{{ item }}</li>
            </ul>
            <p v-else class="minutes-p">{{ part.text }}</p>
          </template>
        </div>
      </template>
      <el-empty v-else-if="!minutes || minutes.status === 'none'" description="暂无纪要" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh } from '@element-plus/icons-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()
const meetingId = Number(route.params.id)

const meeting = ref<any>(null)
const records = ref<any[]>([])
const recordsLoading = ref(false)
const generating = ref(false)
const minutes = ref<any>(null)

const canGenerate = computed(() => !!meeting.value && meeting.value.status === 'ended')

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

// 把 markdown 纪要解析成轻量结构
const minutesParts = computed(() => {
  const md = minutes.value?.minutes || ''
  const parts: any[] = []
  for (const line of md.split('\n')) {
    const t = line.trim()
    if (!t) continue
    const h2 = t.match(/^##+\s*(.*)$/)
    if (h2) {
      parts.push({ type: 'h', text: h2[1] })
      continue
    }
    const li = t.match(/^\s*[-*+]\s+(.*)$/)
    if (li) {
      parts.push({ type: 'li', text: li[1] })
      continue
    }
    const num = t.match(/^\s*\d+[.、]\s*(.*)$/)
    if (num) {
      parts.push({ type: 'li', text: num[1] })
      continue
    }
    const last = parts[parts.length - 1]
    if (last?.type === 'li') {
      last.items.push(t)
    } else {
      parts.push({ type: 'p', text: t })
    }
  }
  const merged: any[] = []
  let pendingLis: string[] | null = null
  for (const p of parts) {
    if (p.type === 'li') {
      pendingLis = pendingLis || []
      pendingLis.push(p.text)
    } else {
      if (pendingLis) {
        merged.push({ type: 'list', items: pendingLis })
        pendingLis = null
      }
      merged.push(p)
    }
  }
  if (pendingLis) merged.push({ type: 'list', items: pendingLis })
  return merged
})

async function fetchDetail() {
  const res: any = await request.get(`/aimeeting/meetings/${meetingId}`)
  meeting.value = res
}

async function fetchRecords() {
  recordsLoading.value = true
  try {
    const res: any = await request.get(`/aimeeting/meetings/${meetingId}/records`)
    records.value = res || []
  } catch {
    // handled by interceptor
  } finally {
    recordsLoading.value = false
  }
}

async function fetchMinutes() {
  const res: any = await request.get(`/aimeeting/meetings/${meetingId}/minutes`)
  minutes.value = res || null
}

async function generateMinutes() {
  generating.value = true
  try {
    const res: any = await request.post(`/aimeeting/meetings/${meetingId}/minutes/generate`)
    minutes.value = res
    if (res?.status === 'success') {
      ElMessage.success('纪要生成成功')
    } else if (res?.status === 'failed') {
      ElMessage.error('纪要生成失败：' + (res?.error || ''))
    } else {
      ElMessage.info('纪要已提交生成')
    }
    await fetchDetail()
  } catch {
    // handled by interceptor
  } finally {
    generating.value = false
  }
}

function goBack() {
  router.push('/aimeeting/list')
}

onMounted(async () => {
  await fetchDetail()
  await fetchRecords()
  await fetchMinutes()
})
</script>

<style scoped>
.aimeeting-detail-page {
  padding: 20px;
}
.page-header {
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 8px 0 4px;
  font-size: 20px;
}
.page-header .meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.page-header .text-muted {
  color: #999;
  font-size: 13px;
}
.info-card,
.section-card {
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.pre-wrap {
  white-space: pre-wrap;
  word-break: break-word;
}
.record-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.record-content {
  color: #333;
  margin: 4px 0;
}
.record-error {
  color: var(--el-color-danger);
  font-size: 12px;
  margin: 4px 0 0;
}
.transcript-text {
  max-height: 320px;
  overflow: auto;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  padding: 12px;
  font-size: 13px;
  line-height: 1.7;
  color: #333;
}
.summary-text {
  font-size: 14px;
  line-height: 1.7;
  color: #333;
}
.minutes-body {
  line-height: 1.7;
}
.minutes-li {
  margin: 4px 0;
}
.minutes-p {
  margin: 6px 0;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>