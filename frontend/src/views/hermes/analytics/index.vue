<template>
  <div class="hermes-analytics-page">
    <!-- 顶部：标题 + 时间范围 + 刷新 -->
    <div class="page-header">
      <div class="header-left">
        <h3 class="page-title">用量分析</h3>
        <span class="page-subtitle">统计 hermes 引擎的模型调用与 Token 消耗</span>
      </div>
      <div class="header-actions">
        <el-select v-model="days" class="days-select" @change="loadAll">
          <el-option label="近 7 天" :value="7" />
          <el-option label="近 14 天" :value="14" />
          <el-option label="近 30 天" :value="30" />
        </el-select>
        <el-button :icon="Refresh" :loading="loading" @click="loadAll">刷新</el-button>
      </div>
    </div>

    <!-- 概览统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <el-statistic title="总 Prompt 数" :value="totals.prompts ?? 0">
            <template #suffix>
              <span class="stat-suffix">次</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <el-statistic title="总 Token 数" :value="totals.tokens ?? 0" />
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <el-statistic title="平均延迟" :value="Number(totals.avg_latency) || 0">
            <template #default>
              <span class="stat-value">{{ formatLatency(totals.avg_latency) }}</span>
              <span class="stat-suffix">ms</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="never" class="stat-card">
          <el-statistic title="平均 TPS" :value="Number(totals.avg_tps) || 0">
            <template #default>
              <span class="stat-value">{{ formatTps(totals.avg_tps) }}</span>
              <span class="stat-suffix">tok/s</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 模型用量分析 -->
    <el-card shadow="never" class="model-card">
      <template #header>
        <div class="card-header">
          <span>模型用量分析</span>
          <span class="card-sub">按调用次数与 Token 统计各模型使用情况</span>
        </div>
      </template>
      <el-table :data="models" v-loading="loading" stripe class="model-table">
        <el-table-column label="模型名" min-width="220">
          <template #default="{ row }">
            <span class="model-name">{{ row.model || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="调用次数" prop="calls" min-width="100" align="right" />
        <el-table-column label="总 Token" prop="tokens" min-width="120" align="right" />
        <el-table-column label="平均延迟" min-width="120" align="right">
          <template #default="{ row }">
            {{ formatLatency(row.avg_latency) }} ms
          </template>
        </el-table-column>
        <el-table-column label="占比" min-width="180">
          <template #default="{ row }">
            <div class="share-cell">
              <el-progress
                :percentage="sharePercent(row)"
                :stroke-width="8"
                :show-text="false"
                class="share-bar"
              />
              <span class="share-text">{{ sharePercent(row) }}%</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !models.length" description="暂无模型用量数据" :image-size="80" />
    </el-card>

    <!-- 每日用量趋势 -->
    <el-card shadow="never" class="trend-card">
      <template #header>
        <div class="card-header">
          <span>每日用量趋势</span>
          <span class="card-sub">近 {{ days }} 天调用量与 Token 消耗（{{ trendRange }}）</span>
        </div>
      </template>
      <div v-if="daily.length" class="trend-wrap">
        <!-- Prompt 柱状图 -->
        <div class="trend-group">
          <div class="trend-title">Prompt 数</div>
          <div class="bars">
            <div
              v-for="d in daily"
              :key="'p-' + d.date"
              class="bar-item"
              :title="`${d.date}: ${d.prompts ?? 0} 次`"
            >
              <div class="bar-track">
                <div
                  class="bar-fill bar-fill-primary"
                  :style="{ height: barHeight(d.prompts, maxPrompts) }"
                ></div>
              </div>
              <div class="bar-label">{{ shortDate(d.date) }}</div>
            </div>
          </div>
        </div>
        <!-- Token 柱状图 -->
        <div class="trend-group">
          <div class="trend-title">Token 数</div>
          <div class="bars">
            <div
              v-for="d in daily"
              :key="'t-' + d.date"
              class="bar-item"
              :title="`${d.date}: ${formatTokens(d.tokens)}`"
            >
              <div class="bar-track">
                <div
                  class="bar-fill bar-fill-accent"
                  :style="{ height: barHeight(d.tokens, maxTokens) }"
                ></div>
              </div>
              <div class="bar-label">{{ shortDate(d.date) }}</div>
            </div>
          </div>
        </div>
        <div class="trend-legend">
          <span class="legend-item"><i class="legend-dot legend-dot-primary"></i>Prompt 数</span>
          <span class="legend-item"><i class="legend-dot legend-dot-accent"></i>Token 数</span>
        </div>
      </div>
      <el-empty v-else-if="!loading" description="暂无趋势数据" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElSelect, ElOption, ElCard, ElStatistic, ElTable, ElTableColumn, ElButton, ElProgress } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

// ── 状态 ──────────────────────────────────────────
const loading = ref(false)
const days = ref(7)

interface DailyItem {
  date: string
  prompts?: number
  tokens?: number
  [key: string]: any
}

interface ModelStat {
  model: string
  calls: number
  tokens?: number
  avg_latency?: number
  [key: string]: any
}

const daily = ref<DailyItem[]>([])
const totals = ref<Record<string, any>>({})
const models = ref<ModelStat[]>([])

const trendRange = computed(() => {
  if (!daily.value.length) return ''
  const first = daily.value[0]?.date
  const last = daily.value[daily.value.length - 1]?.date
  return first && last ? `${first} ~ ${last}` : ''
})

const maxPrompts = computed(() =>
  Math.max(1, ...daily.value.map((d) => Number(d.prompts) || 0))
)
const maxTokens = computed(() =>
  Math.max(1, ...daily.value.map((d) => Number(d.tokens) || 0))
)

const totalCalls = computed(() =>
  models.value.reduce((sum, m) => sum + (Number(m.calls) || 0), 0)
)

// ── 格式化 ────────────────────────────────────────
function formatLatency(v?: number): string {
  const n = Number(v)
  if (!Number.isFinite(n) || n <= 0) return '--'
  return n >= 1000 ? (n / 1000).toFixed(2) : Math.round(n).toString()
}

function formatTps(v?: number): string {
  const n = Number(v)
  if (!Number.isFinite(n) || n <= 0) return '--'
  return n >= 100 ? Math.round(n).toString() : n.toFixed(1)
}

function formatTokens(v?: number): string {
  const n = Number(v) || 0
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K'
  return n.toString()
}

function shortDate(date: string): string {
  if (!date) return ''
  return date.length > 5 ? date.slice(5) : date
}

function sharePercent(row: any): number {
  const calls = Number(row.calls) || 0
  if (!totalCalls.value) return 0
  return Number(((calls / totalCalls.value) * 100).toFixed(1))
}

function barHeight(v?: number, max?: number): string {
  const n = Number(v) || 0
  const m = Number(max) || 1
  if (!n) return '2%'
  const pct = Math.max(2, Math.round((n / m) * 100))
  return `${pct}%`
}

// ── 数据加载 ──────────────────────────────────────
async function loadAll() {
  loading.value = true
  try {
    const [analyticsRes, modelsRes]: any[] = await Promise.all([
      hermes.getAnalytics(days.value),
      hermes.getModelsAnalytics(days.value),
    ])
    const aData = analyticsRes?.data ?? analyticsRes ?? {}
    const mData = modelsRes?.data ?? modelsRes ?? {}
    daily.value = Array.isArray(aData.daily) ? aData.daily : []
    totals.value = aData.totals ?? {}
    models.value = Array.isArray(mData.models) ? mData.models : []
  } catch (e: any) {
    console.error('[analytics] 加载用量数据失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.hermes-analytics-page {
  padding: 4px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1f2937);
}

.page-subtitle {
  font-size: 13px;
  color: var(--el-text-color-secondary, #909399);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.days-select {
  width: 130px;
}

.stat-row {
  margin-bottom: 16px;
}

.stat-row .el-col {
  margin-bottom: 16px;
}

.stat-card {
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
  transition: box-shadow 0.2s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.08);
}

.stat-suffix {
  font-size: 13px;
  font-weight: 400;
  color: var(--el-text-color-secondary, #909399);
  margin-left: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1f2937);
}

.model-card,
.trend-card {
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.card-sub {
  font-size: 12px;
  color: var(--el-text-color-secondary, #909399);
}

.model-name {
  font-weight: 500;
  color: var(--el-text-color-primary, #303133);
}

.share-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.share-bar {
  flex: 1;
  max-width: 110px;
}

.share-text {
  font-size: 12px;
  color: var(--el-text-color-secondary, #909399);
  white-space: nowrap;
}

/* ── 每日趋势柱状图（CSS 模拟） ── */
.trend-wrap {
  padding-top: 8px;
}

.trend-group + .trend-group {
  margin-top: 24px;
}

.trend-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-regular, #606266);
  margin-bottom: 10px;
}

.bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  min-height: 160px;
}

.bar-item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.bar-track {
  width: 100%;
  max-width: 36px;
  height: 120px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: var(--el-fill-color-light, #f5f7fa);
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  border-radius: 6px 6px 0 0;
  transition: height 0.45s ease;
}

.bar-fill-primary {
  background: linear-gradient(180deg, #7c3aed, #4f46e5);
}

.bar-fill-accent {
  background: linear-gradient(180deg, #38bdf8, #0ea5e9);
}

.bar-label {
  font-size: 11px;
  color: var(--el-text-color-secondary, #909399);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.trend-legend {
  display: flex;
  gap: 18px;
  margin-top: 14px;
  justify-content: center;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary, #909399);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  display: inline-block;
}

.legend-dot-primary {
  background: linear-gradient(180deg, #7c3aed, #4f46e5);
}

.legend-dot-accent {
  background: linear-gradient(180deg, #38bdf8, #0ea5e9);
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .bar-track {
    background: var(--el-fill-color-dark, #2a2a2e);
  }
  .stat-card:hover {
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.15);
  }
}
</style>