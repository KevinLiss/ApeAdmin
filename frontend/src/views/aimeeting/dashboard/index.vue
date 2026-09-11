<template>
  <div class="dash-page" v-loading="loading">
    <div class="page-header">
      <div>
        <h2>数据面板</h2>
        <p class="text-muted">AI 会议整体运行情况：会议规模、实时录制、转写健康度与趋势</p>
      </div>
      <div class="header-ops">
        <el-switch v-model="auto" active-text="自动刷新(30s)" />
        <el-button :loading="loading" @click="fetchStats">
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
      </div>
    </div>

    <!-- ── 总览卡片 ── -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-label">会议总数</div>
        <div class="stat-value">{{ o.total_meetings ?? '—' }}</div>
        <div class="stat-sub">已结束 {{ o.ended ?? 0 }} · 待开始 {{ o.scheduled ?? 0 }}</div>
      </div>
      <div class="stat-card accent">
        <div class="stat-label">
          进行中会议
          <span v-if="o.live_streaming" class="live-badge"><span class="live-dot"></span>{{ o.live_streaming }} 路实时推流</span>
        </div>
        <div class="stat-value">{{ o.in_progress ?? '—' }}</div>
        <div class="stat-sub">同一时刻仅一路录音（单录制方）</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">今日新增</div>
        <div class="stat-value">{{ o.today_created ?? '—' }}</div>
        <div class="stat-sub">按服务器 UTC 日界</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">累计录音时长</div>
        <div class="stat-value">{{ fmtDuration(o.total_record_sec) }}</div>
        <div class="stat-sub">纪要已生成 {{ o.minutes_done ?? 0 }} 场</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">转写片段</div>
        <div class="stat-value">
          {{ o.records_success ?? 0 }}<span class="stat-unit">/ {{ o.records_total ?? 0 }}</span>
        </div>
        <div class="stat-sub">
          转写中 {{ o.records_processing ?? 0 }} ·
          <span :class="{ danger: (o.records_failed ?? 0) > 0 }">失败 {{ o.records_failed ?? 0 }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-label">重点 / 标记</div>
        <div class="stat-value">{{ o.highlights_total ?? 0 }}<span class="stat-unit"> / {{ o.marks_total ?? 0 }}</span></div>
        <div class="stat-sub">会中随手记录的使用量</div>
      </div>
    </div>

    <!-- ── 图表行 ── -->
    <div class="chart-row">
      <div class="panel">
        <div class="panel-title">近 14 天新建会议</div>
        <v-chart class="chart" :option="trendOption" autoresize />
      </div>
      <div class="panel half">
        <div class="panel-title">会议状态分布</div>
        <v-chart class="chart" :option="statusOption" autoresize />
      </div>
    </div>

    <!-- ── 进行中会议 ── -->
    <div class="panel">
      <div class="panel-title">
        进行中的会议
        <span class="title-tip">{{ data.in_progress_meetings?.length ? '共 ' + data.in_progress_meetings.length + ' 场（最多显示 20）' : '暂无' }}</span>
      </div>
      <el-table :data="data.in_progress_meetings || []" size="small" empty-text="当前没有进行中的会议">
        <el-table-column label="会议" min-width="200">
          <template #default="{ row }">
            <el-link type="primary" @click="goDetail(row.id)">{{ row.title }}</el-link>
            <span class="code-tag">{{ row.meeting_code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实时推流" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.live" type="danger" size="small" effect="dark">录制中</el-tag>
            <el-tag v-else type="warning" size="small" effect="plain">无人录制</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="实际开始" width="170">
          <template #default="{ row }">{{ fmtDateTime(row.actual_start) }}</template>
        </el-table-column>
        <el-table-column label="已录时长" width="100" align="center">
          <template #default="{ row }">{{ fmtDuration(row.audio_duration) }}</template>
        </el-table-column>
        <el-table-column label="转写" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.transcript_status === 'success' ? 'success' : row.transcript_status === 'failed' ? 'danger' : 'info'" size="small">
              {{ transcriptText(row.transcript_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分离" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.diarization_status === 'success' ? 'success' : 'info'" size="small" effect="plain">
              {{ diarText(row.diarization_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="goDetail(row.id)">详情</el-button>
            <el-button link type="success" size="small" @click="openShare(row)">分享</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ── 底部两栏：Top5 + 失败片段 ── -->
    <div class="chart-row">
      <div class="panel half">
        <div class="panel-title">录音时长 Top 5</div>
        <el-table :data="data.top_meetings || []" size="small" empty-text="暂无录音数据">
          <el-table-column label="#" type="index" width="40" />
          <el-table-column label="会议" min-width="180">
            <template #default="{ row }">
              <el-link type="primary" @click="goDetail(row.id)">{{ row.title }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="说话人" width="80" align="center">
            <template #default="{ row }">{{ row.speaker_count || '—' }}</template>
          </el-table-column>
          <el-table-column label="时长" width="100" align="center">
            <template #default="{ row }">{{ fmtDuration(row.audio_duration) }}</template>
          </el-table-column>
        </el-table>
      </div>
      <div class="panel half">
        <div class="panel-title">
          最近失败片段
          <span v-if="(data.recent_failed || []).length" class="title-tip danger">{{ data.recent_failed.length }} 条待处理</span>
        </div>
        <el-table :data="data.recent_failed || []" size="small" empty-text="没有失败的转写片段 🎉">
          <el-table-column label="会议" min-width="140">
            <template #default="{ row }">
              <el-link type="primary" @click="goDetail(row.meeting_id)">{{ row.meeting_title || ('#' + row.meeting_id) }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="原因" min-width="180">
            <template #default="{ row }">
              <span class="err-text" :title="row.error">{{ row.error || '未知错误' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="时间" width="160">
            <template #default="{ row }">{{ fmtDateTime(row.at) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 分享二维码弹窗（与会议管理页一致） -->
    <el-dialog v-model="shareVisible" title="分享会议" width="360px" align-center>
      <div class="share-body">
        <img v-if="shareQrUrl" :src="shareQrUrl" class="share-qr" alt="会议二维码" />
        <p class="share-tip">扫码或复制链接进入会议<br />其他设备进入后只读观看，可接管录音</p>
        <div class="share-link-row">
          <el-input :model-value="shareUrl" readonly size="small" />
          <el-button type="primary" size="small" @click="copyLink">复制</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getDashboardStats } from '@/api/aimeeting'

use([CanvasRenderer, BarChart, PieChart, TooltipComponent, LegendComponent, GridComponent])

const router = useRouter()
const loading = ref(false)
const data = ref<any>({})
const o = computed(() => data.value.overview || {})

const auto = ref(true)
let timer: number | null = null

async function fetchStats() {
  loading.value = true
  try {
    data.value = await getDashboardStats() as any
  } catch {
    // request 拦截器已弹错
  } finally {
    loading.value = false
  }
}

function setupTimer() {
  if (timer) clearInterval(timer)
  timer = window.setInterval(() => { if (auto.value) fetchStats() }, 30000)
}

// ── 图表配置 ──
const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 16, top: 24, bottom: 28 },
  xAxis: { type: 'category', data: (data.value.trend_14d || []).map((t: any) => t.date), axisTick: { show: false } },
  yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { type: 'dashed' } } },
  series: [{
    type: 'bar',
    data: (data.value.trend_14d || []).map((t: any) => t.count),
    barMaxWidth: 18,
    itemStyle: { color: '#4f46e5', borderRadius: [4, 4, 0, 0] },
  }],
}))

const STATUS_LABEL: Record<string, string> = {
  scheduled: '待开始', in_progress: '进行中', ended: '已结束', cancelled: '已取消',
}
const STATUS_COLOR: Record<string, string> = {
  scheduled: '#909399', in_progress: '#e6a23c', ended: '#67c23a', cancelled: '#c0c4cc',
}
const statusOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, itemWidth: 10, itemHeight: 10 },
  series: [{
    type: 'pie',
    radius: ['42%', '65%'],
    center: ['50%', '44%'],
    avoidLabelOverlap: true,
    label: { show: false },
    data: (data.value.status_distribution || []).map((s: any) => ({
      name: STATUS_LABEL[s.status] || s.status,
      value: s.count,
      itemStyle: { color: STATUS_COLOR[s.status] || '#4f46e5' },
    })),
  }],
}))

// ── 格式化 ──
function fmtDuration(sec?: number) {
  if (!sec) return '0'
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  if (h > 0) return `${h}h${String(m).padStart(2, '0')}m`
  if (m > 0) return `${m}m${String(s).padStart(2, '0')}s`
  return `${s}s`
}
function fmtDateTime(v?: string | null) {
  if (!v) return '—'
  const d = new Date(v)
  if (isNaN(d.getTime())) return v
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}
function transcriptText(s?: string) {
  return s === 'success' ? '已完成' : s === 'failed' ? '失败' : s === 'processing' ? '转写中' : '未转写'
}
function diarText(s?: string) {
  return s === 'success' ? '已分离' : s === 'pending' ? '分离中' : s === 'failed' ? '失败' : '未分离'
}

function goDetail(id: number) {
  router.push(`/aimeeting/detail/${id}`)
}

// ── 分享弹窗 ──
const shareVisible = ref(false)
const shareUrl = ref('')
const shareQrUrl = ref('')
const H5_BASE = `${location.protocol}//${location.hostname}:5177`
async function openShare(row: any) {
  shareUrl.value = `${H5_BASE}/meeting/${row.id}`
  shareQrUrl.value = ''
  shareVisible.value = true
  try {
    const QRCode = (await import('qrcode')).default
    shareQrUrl.value = await QRCode.toDataURL(shareUrl.value, { width: 440, margin: 1 })
  } catch {
    ElMessage.warning('二维码生成失败，可直接复制链接')
  }
}
async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    ElMessage.success('链接已复制')
  } catch {
    ElMessage.warning('复制失败，请手动选择复制')
  }
}

onMounted(() => { fetchStats(); setupTimer() })
onBeforeUnmount(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.dash-page {
  padding: 0 0 24px;
}
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0 0 4px; font-size: 20px; }
.text-muted { color: #909399; font-size: 13px; margin: 0; }
.header-ops { display: flex; align-items: center; gap: 12px; }

/* 总览卡片 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}
.stat-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 16px 18px;
}
.stat-card.accent {
  border-color: #c7d2fe;
  background: linear-gradient(135deg, #f5f7ff 0%, #eef1ff 100%);
}
.stat-label { font-size: 13px; color: #606266; display: flex; align-items: center; gap: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: #1a1a1a; margin: 6px 0 4px; }
.stat-unit { font-size: 14px; font-weight: 400; color: #909399; margin-left: 4px; }
.stat-sub { font-size: 12px; color: #909399; }
.stat-sub .danger, .title-tip.danger { color: #f56c6c; }
.live-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; color: #fff; background: #f56c6c;
  padding: 1px 8px; border-radius: 999px;
}
.live-dot {
  width: 6px; height: 6px; border-radius: 50%; background: #fff;
  animation: blink 1s infinite;
}
@keyframes blink { 50% { opacity: 0.25; } }

/* 面板 */
.panel {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 14px 16px;
  margin-bottom: 16px;
}
.panel-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
.title-tip { font-size: 12px; font-weight: 400; color: #909399; }
.chart-row {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 16px;
}
.chart-row .panel { margin-bottom: 16px; }
.chart { height: 260px; }
@media (max-width: 900px) { .chart-row { grid-template-columns: 1fr; } }

.code-tag { margin-left: 8px; font-size: 12px; color: #909399; }
.err-text {
  display: inline-block; max-width: 100%;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: #f56c6c; font-size: 12px; vertical-align: bottom;
}

/* 分享弹窗 */
.share-body { text-align: center; }
.share-qr { width: 220px; height: 220px; }
.share-tip { font-size: 12px; color: #909399; line-height: 1.7; margin: 8px 0 12px; }
.share-link-row { display: flex; gap: 8px; }
</style>
