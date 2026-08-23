<template>
  <div class="dashboard-default">
    <PageHeader title="默认看板" :breadcrumb="['APEUI库', '数据看板', '默认看板']" />

    <div class="dash-container">
      <!-- Row 1: Profile Greeting (10/24) + 年度概览 (8/24) + Activity Review (6/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- Profile Greeting -->
        <el-col :xs="24" :sm="12" :lg="10">
          <div class="ape-card profile-greeting">
            <div class="greeting-body">
              <div class="greeting-text">
                <h1>欢迎回来，{{ greetingName }}</h1>
                <p>系统共 {{ stats.user_total }} 个用户、{{ stats.role_total }} 个角色，今日 MCP 调用 {{ stats.auditToday }} 次</p>
                <a class="greeting-btn" href="javascript:void(0)">
                  继续
                  <el-icon><ArrowRight /></el-icon>
                </a>
              </div>
              <div class="greeting-img">
                <img src="/assets/images/dashboard/profile-greeting/bg.png" alt="" />
              </div>
            </div>
          </div>
        </el-col>

        <!-- 年度概览 -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="ape-card yearly-view">
            <div class="card-header">
              <h3>MCP 调用趋势 <span class="ape-badge-soft">{{ stats.audit_total }}</span></h3>
              <h5 class="weekday-label">近 14 天</h5>
            </div>
            <div class="card-body p-0">
              <v-chart class="yearly-chart" :option="yearlyChartOption" autoresize />
            </div>
          </div>
        </el-col>

        <!-- Activity Review -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="ape-card activity-review">
            <div class="card-header">
              <h3>最近调用</h3>
            </div>
            <div class="card-body">
              <div class="activity-list">
                <div class="activity-item" v-for="act in activities" :key="act.id">
                  <div class="activity-avatar activity-avatar-type" :class="act.statusClass">{{ act.typeLabel }}</div>
                  <div class="activity-info">
                    <h5>{{ act.title }}</h5>
                    <p>{{ act.subtitle }}</p>
                  </div>
                  <div class="time-badge">
                    <p>{{ act.time }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 2: Transaction (10/24) + Value Chart sub-cards (6/24) + 超越边界 (8/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- Transaction History -->
        <el-col :xs="24" :lg="10">
          <div class="ape-card transaction-history">
            <div class="card-header">
              <h3>系统资源 <span class="ape-badge-soft">{{ stats.plugin_total }} 插件</span></h3>
            </div>
            <div class="transaction-body">
              <table class="transaction-table">
                <thead>
                  <tr>
                    <th>插件名称</th>
                    <th>创建日期</th>
                    <th>版本</th>
                    <th>启用率</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tx in transactions" :key="tx.id">
                    <td>
                      <div class="tx-item">
                        <div class="tx-icon tx-icon-text">{{ tx.icon }}</div>
                        <div>
                          <h5>{{ tx.name }}</h5>
                          <p>{{ tx.delivery }}</p>
                        </div>
                      </div>
                    </td>
                    <td>
                      <h5>{{ tx.date }}</h5>
                      <p>{{ tx.author }}</p>
                    </td>
                    <td>
                      <h5>v{{ tx.days }}</h5>
                    </td>
                    <td>
                      <div class="progress-showcase">
                        <p>{{ tx.progress }}%</p>
                        <div class="progress-track" :class="tx.progressClass">
                          <div class="progress-fill" :style="{ width: tx.progress + '%' }"></div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <h5>{{ tx.payment }}</h5>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-col>

        <!-- Value Chart: 2 sub-cards stacked -->
        <el-col :xs="24" :lg="6">
          <div class="value-chart-sub1 ape-card">
            <div class="value-chart-body">
              <div class="round-progress-section">
                <v-chart class="knob-chart" :option="knobChartOption" autoresize />
              </div>
              <div class="valuechart-detail">
                <p>插件启用率</p>
                <h2>{{ pluginRate }}%</h2>
              </div>
            </div>
            <span class="value-badge">启用</span>
          </div>
          <div class="value-chart-sub2 ape-card">
            <div class="value-chart-body">
              <div class="stock-chart-section">
                <v-chart class="stock-chart" :option="stockChartOption" autoresize />
              </div>
              <div class="valuechart-detail">
                <p>今日调用</p>
                <h2>{{ stats.auditToday }}</h2>
              </div>
            </div>
            <span class="value-badge">实时</span>
          </div>
        </el-col>

        <!-- 超越边界 -->
        <el-col :xs="24" :lg="8">
          <div class="beyo-line">
            <div class="beyo-header">
              <v-chart class="beyo-chart" :option="beyoChartOption" autoresize />
            </div>
            <div class="beyo-detail">
              <h3>系统统计 <span class="ape-badge-soft">实时</span></h3>
              <p>共 {{ stats.menu_total }} 个菜单、{{ stats.dept_total }} 个部门，{{ stats.plugin_enabled }}/{{ stats.plugin_total }} 插件已启用。</p>
              <div class="date-history">
                <ul class="beyo-avatars">
                  <li><h2>{{ stats.audit_total }}</h2></li>
                </ul>
                <div class="date-label">
                  <h3>{{ todayDate }}</h3>
                  <p>{{ todayMonth }}</p>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 3: Investment Chart 3-col (10/24) + 热门社交媒体 (6/24) + Upgrade History (8/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- Investment Chart -->
        <el-col :xs="24" :lg="10">
          <div class="ape-card investment-chart">
            <div class="card-body">
              <el-row :gutter="20">
                <el-col :sm="8">
                  <div class="investment-group">
                    <span class="invest-label">{{ stats.user_total }}</span>
                    <v-chart class="invest-chart-sm" :option="investChartOption" autoresize />
                    <div class="chart-detail">
                      <h5>用户</h5>
                      <h2>{{ stats.user_total }}</h2>
                    </div>
                  </div>
                </el-col>
                <el-col :sm="8">
                  <div class="investment-group">
                    <span class="invest-label">{{ stats.role_total }}</span>
                    <v-chart class="invest-chart-sm" :option="gainChartOption" autoresize />
                    <div class="chart-detail">
                      <h5>角色</h5>
                      <h2>{{ stats.role_total }}</h2>
                    </div>
                  </div>
                </el-col>
                <el-col :sm="8">
                  <div class="investment-group">
                    <span class="invest-label">{{ stats.menu_total }}</span>
                    <v-chart class="invest-chart-sm" :option="profitChartOption" autoresize />
                    <div class="chart-detail">
                      <h5>菜单</h5>
                      <h2>{{ stats.menu_total }}</h2>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-col>

        <!-- 系统资源统计 -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="ape-card social-shared">
            <div class="card-header">
              <h3>系统资源</h3>
            </div>
            <div class="card-body">
              <div class="social-list">
                <div class="social-item" v-for="sys in sysStats" :key="sys.name">
                  <div class="social-icon">
                    <h5 class="social-icon-text">{{ sys.name[0] }}</h5>
                  </div>
                  <div class="social-info">
                    <h5>{{ sys.name }}</h5>
                    <p>系统资源</p>
                  </div>
                  <div class="social-trend">
                    <el-icon class="trend-up-icon"><CaretTop /></el-icon>
                    <h5>+{{ sys.trend }}</h5>
                  </div>
                  <div class="social-value">
                    <h5>{{ sys.value }}</h5>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- Upgrade History -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="ape-card upgrade-history">
            <div class="upgrade-body">
              <div class="upgrade-text">
                <h3>立即购买更多空间！</h3>
                <p>邀请 2 位好友，即可获得 5 GB 额外空间。</p>
                <a class="upgrade-btn" href="javascript:void(0)">立即升级</a>
              </div>
            </div>
            <div class="upgrade-img">
              <img src="/assets/images/dashboard/upgrade/1.png" alt="" />
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import { ArrowRight, CaretTop } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, GaugeChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'
import { getDashboardStats } from '../../../api'

use([CanvasRenderer, LineChart, BarChart, GaugeChart, GridComponent, TooltipComponent, LegendComponent])

/* ApeAdmin color constants */
const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'

/* ---- Dashboard real data (from GET /dashboard/stats) ---- */
const stats = ref({
  user: { username: '', nickname: '' },
  user_total: 0,
  role_total: 0,
  menu_total: 0,
  dept_total: 0,
  plugin_total: 0,
  plugin_enabled: 0,
  audit_total: 0,
  auditToday: 0,
  audit: { total: 0, today: 0, recent: [] as any[] },
  trend: { dates: [] as string[], counts: [] as number[] },
  plugins: [] as any[],
})

const greetingName = computed(() => stats.value.user?.nickname || stats.value.user?.username || '管理员')
const pluginRate = computed(() => {
  const total = stats.value.plugin_total || 0
  if (!total) return 0
  return Math.round(((stats.value.plugin_enabled || 0) / total) * 100)
})

const todayDate = computed(() => {
  const d = new Date()
  return d.getDate()
})
const todayMonth = computed(() => {
  const m = new Date().getMonth() + 1
  return m + ' 月'
})

/* ---- 最近调用（MCP 审计日志）---- */
const typeLabelMap: Record<string, string> = {
  tool: '工具',
  prompt: '提示词',
  resource: '资源',
}
const activities = computed(() => {
  const recent = stats.value.audit?.recent || []
  return recent.map((item: any) => {
    const typeLabel = typeLabelMap[item.action_type] || item.action_type
    return {
      id: item.id,
      typeLabel,
      statusClass: item.status === 'success' ? 'activity-status-success' : 'activity-status-failed',
      title: `${item.username || '匿名'} 调用 ${item.target_name}`,
      subtitle: item.created_at || '',
      time: item.status === 'success' ? '成功' : '失败',
    }
  })
})

/* ---- 系统资源列表（插件）---- */
const transactions = computed(() => {
  const plugins = stats.value.plugins || []
  return plugins.map((p: any) => ({
    id: p.id,
    icon: p.enabled ? '开' : '停',
    name: p.display_name || p.name,
    delivery: p.name,
    date: p.created_at || '',
    author: '系统插件',
    days: p.version,
    income: p.enabled ? 100 : 0,
    progress: p.enabled ? 100 : 0,
    progressClass: p.enabled ? 'progress-success' : 'progress-danger',
    payment: p.enabled ? '已启用' : '已停用',
  }))
})

/* ---- 系统资源统计（社交媒体卡片替换）---- */
const sysStats = computed(() => [
  { name: '用户', trend: stats.value.user_total, value: `${stats.value.user_total}` },
  { name: '角色', trend: stats.value.role_total, value: `${stats.value.role_total}` },
  { name: '菜单', trend: stats.value.menu_total, value: `${stats.value.menu_total}` },
  { name: '部门', trend: stats.value.dept_total, value: `${stats.value.dept_total}` },
])

/* ===== ECharts Options ===== */

/* 1. MCP 调用趋势 — Area chart with gradient */
const yearlyChartOption = computed(() => ({
  series: [{
    type: 'line',
    data: stats.value.trend?.counts || [],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 5, color: PRIMARY },
    areaStyle: {
      color: {
        type: 'linear' as const,
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(90, 103, 245, 0.5)' },
          { offset: 1, color: 'rgba(90, 103, 245, 0.9)' },
        ],
      },
    },
  }],
  grid: { left: 0, right: 0, top: 10, bottom: 5 },
  xAxis: { show: false, type: 'category', data: stats.value.trend?.dates || [] },
  yAxis: { show: false, min: 0, max: 5 },
  tooltip: {
    trigger: 'axis',
    backgroundColor: PRIMARY,
    borderColor: 'transparent',
    textStyle: { color: '#fff' },
    axisPointer: { type: 'line', lineStyle: { color: PRIMARY, type: 'dashed' } },
    formatter: (params: any) => {
      const p = params[0]
      return `${p.axisValue}<br/>调用 ${p.value} 次`
    },
  },
}))

/* 2. Knob (插件启用率) — Gauge chart */
const knobChartOption = computed(() => ({
  series: [{
    type: 'gauge',
    startAngle: 90,
    endAngle: -270,
    radius: '90%',
    progress: {
      show: true,
      overlap: false,
      roundCap: true,
      clip: false,
      itemStyle: { color: PRIMARY },
    },
    axisLine: { lineStyle: { width: 10, color: [[pluginRate.value / 100, PRIMARY], [1, '#C4C4C4']] } },
    splitLine: { show: false },
    axisTick: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    data: [{ value: pluginRate.value }],
    detail: {
      valueAnimation: true,
      fontSize: 20,
      color: PRIMARY,
      offsetCenter: ['0%', '0%'],
      formatter: '{value}%',
    },
  }],
}))

/* 3. Stock Value — 今日调用占比 */
const stockChartOption = computed(() => {
  const total = stats.value.audit_total || 0
  const today = stats.value.auditToday || 0
  const rest = Math.max(total - today, 0)
  return {
    series: [
      {
        type: 'bar',
        stack: 'total',
        data: [today],
        barWidth: 18,
        itemStyle: { borderRadius: 0, color: SECONDARY },
      },
      {
        type: 'bar',
        stack: 'total',
        data: [rest],
        barWidth: 18,
        itemStyle: { borderRadius: 6, color: '#EADAD3' },
      },
    ],
    grid: { left: 0, right: 0, top: 5, bottom: 0 },
    xAxis: { type: 'category', show: false },
    yAxis: { show: false },
    tooltip: { show: false },
  }
})

/* 4. 系统统计 — 14 天调用趋势柱状图 */
const beyoChartOption = computed(() => ({
  series: [
    {
      name: 'MCP 调用',
      type: 'bar',
      data: stats.value.trend?.counts || [],
      barWidth: 18,
      barMinHeight: 2,
      itemStyle: { borderRadius: 6, color: '#B7B1D7' },
    },
  ],
  grid: { left: 0, right: 0, top: 10, bottom: 5 },
  xAxis: { type: 'category', show: false, data: stats.value.trend?.dates || [] },
  yAxis: { show: false, min: 0, max: 5 },
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: (params: any) => {
      const p = params[0]
      return `${p.axisValue}<br/>调用 ${p.value} 次`
    },
  },
}))

/* 5. 用户/角色/菜单 — 迷你趋势线 */
const investChartOption = computed(() => ({
  series: [{
    type: 'line',
    data: stats.value.trend?.counts || [],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: PRIMARY },
  }],
  grid: { left: 0, right: 0, top: 5, bottom: 3 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false, min: 0, max: 5 },
  tooltip: { trigger: 'axis' },
}))

/* 6. Gain Chart — Smooth line, secondary color */
const gainChartOption = computed(() => ({
  series: [{
    type: 'line',
    data: stats.value.trend?.counts || [],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: SECONDARY },
  }],
  grid: { left: 0, right: 0, top: 5, bottom: 3 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false, min: 0, max: 5 },
  tooltip: { trigger: 'axis' },
}))

/* 7. Profit Chart — Smooth line, success color */
const profitChartOption = computed(() => ({
  series: [{
    type: 'line',
    data: stats.value.trend?.counts || [],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: SUCCESS },
  }],
  grid: { left: 0, right: 0, top: 5, bottom: 3 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false, min: 0, max: 5 },
  tooltip: { trigger: 'axis' },
}))

/* ---- 数据加载 ---- */
async function fetchStats() {
  try {
    const data: any = await getDashboardStats()
    stats.value = {
      ...stats.value,
      user: data.user || { username: '', nickname: '' },
      user_total: data.stats?.user_total ?? 0,
      role_total: data.stats?.role_total ?? 0,
      menu_total: data.stats?.menu_total ?? 0,
      dept_total: data.stats?.dept_total ?? 0,
      plugin_total: data.stats?.plugin_total ?? 0,
      plugin_enabled: data.stats?.plugin_enabled ?? 0,
      audit_total: data.audit?.total ?? 0,
      auditToday: data.audit?.today ?? 0,
      audit: data.audit || { total: 0, today: 0, recent: [] },
      trend: data.trend || { dates: [], counts: [] },
      plugins: data.plugins || [],
    }
  } catch (e) {
    console.error('加载仪表盘数据失败:', e)
  }
}

onMounted(fetchStats)
</script>

<style scoped>
.dashboard-default {
  padding: 0;
}
.dash-container {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.dash-row {
  margin-bottom: 0;
}

/* ==================== Profile Greeting ==================== */
.profile-greeting {
  background: linear-gradient(135deg, #5A67F5 0%, #47D8FF 100%);
  height: 254px;
  position: relative;
  /* ApeAdmin 原版：插画从卡片顶部自然探出，不做裁切 */
  overflow: visible;
}
.profile-greeting .greeting-body {
  padding: 25px;
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
}
.profile-greeting .greeting-text {
  position: relative;
  z-index: 2;
  max-width: 55%;
}
.profile-greeting .greeting-text h1 {
  color: #fff;
  font-size: 30px;
  font-weight: 600;
  margin: 0 0 10px;
}
.profile-greeting .greeting-text p {
  color: #fff;
  font-size: 16px;
  width: 60%;
  margin: 0 0 20px;
  line-height: 1.5;
}
.greeting-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background-color: #fff;
  color: #5A67F5;
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}
.greeting-btn:hover {
  background-color: transparent;
  border: 1px solid #fff;
  color: #fff;
}
.greeting-btn .el-icon {
  font-size: 18px;
}
.greeting-img {
  position: absolute;
  bottom: -2px;
  right: 0;
  max-width: 42%;
}
.greeting-img img {
  /* ApeAdmin 1:1：探出卡片顶部约 9px；保持比例、不超容器 */
  width: auto;
  height: auto;
  max-width: 100%;
  max-height: 261px;
}

/* ==================== 年度概览 ==================== */
.yearly-view .card-header {
  padding: 25px 25px 0;
}
.yearly-view .card-header h3 {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 5px;
}
.yearly-view .card-header h3 .ape-badge-soft {
  float: right;
}
.weekday-label {
  color: #9993B4;
  font-size: 14px;
  margin: 0;
}
.yearly-view .card-body {
  padding: 0;
  overflow: hidden;
}
.yearly-chart {
  height: 203px;
  width: 100%;
  margin-left: -15px;
  margin-right: -15px;
  margin-bottom: -35px;
}

/* ==================== Activity Review ==================== */
.activity-review .card-header {
  padding: 25px 25px 0;
}
.activity-review .card-body {
  padding: 15px 25px 25px;
}
.activity-list {
  display: flex;
  flex-direction: column;
}
.activity-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  gap: 15px;
}
.activity-item:hover {
  background-color: rgba(90, 103, 245, 0.1);
  border-radius: 8px;
  margin: 0 -10px;
  padding: 8px 10px;
}
.activity-avatar {
  width: 40px;
  height: 40px;
  border-radius: 5px;
  object-fit: cover;
  flex-shrink: 0;
}
.activity-avatar-type {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #5A67F5;
  background: rgba(90, 103, 245, 0.12);
}
.activity-status-success {
  background: rgba(103, 193, 0, 0.14);
  color: #67C100;
}
.activity-status-failed {
  background: rgba(220, 8, 8, 0.12);
  color: #DC0808;
}
.activity-info {
  flex: 1;
  min-width: 0;
}
.activity-info h5 {
  margin: 0 0 3px;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.activity-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
.time-badge {
  background: rgba(90, 103, 245, 0.05);
  padding: 2px 4px;
  border-radius: 5px;
  flex-shrink: 0;
}
.time-badge p {
  font-size: 10px;
  color: #5A67F5;
  margin: 0;
  white-space: nowrap;
}

/* ==================== Transaction History ==================== */
.transaction-history .card-header {
  padding: 25px 25px 0;
}
.transaction-body {
  padding: 0;
  overflow: hidden;
}
.transaction-table {
  width: 100%;
  border-collapse: collapse;
}
.transaction-table thead th {
  font-size: 16px;
  font-weight: 500;
  color: #2B2B2B;
  padding: 15px 12px 15px 25px;
  text-align: left;
  border-bottom: none;
  white-space: nowrap;
}
.transaction-table tbody td {
  white-space: nowrap;
}
.transaction-table thead th:first-child {
  padding-left: 25px;
}
.transaction-table thead th:last-child {
  padding-right: 25px;
}
.transaction-table tbody tr {
  border-top: 14px solid #EFF3F9;
  border-bottom: 14px solid #EFF3F9;
}
.transaction-table tbody tr:first-child {
  border-top: none;
}
.transaction-table tbody td {
  padding: 12px 12px;
  vertical-align: middle;
  border: none;
}
.transaction-table tbody td:first-child {
  padding-left: 25px;
  border-left: 25px solid #EFF3F9;
}
.transaction-table tbody td:last-child {
  padding-right: 25px;
  border-right: 25px solid #EFF3F9;
}
.tx-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tx-icon img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
}
.tx-icon-text {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: rgba(90, 103, 245, 0.12);
  color: #5A67F5;
  font-size: 13px;
  font-weight: 600;
}
.tx-item h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.tx-item p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #909399;
}
.transaction-table h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}
.income-positive {
  color: #67C100 !important;
}
.income-negative {
  color: #DC0808 !important;
}
.progress-showcase {
  text-align: right;
}
.progress-showcase p {
  margin: 0 0 4px;
  font-size: 12px;
  color: #909399;
}
.progress-track {
  height: 5px;
  background: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 3px;
}
.progress-success .progress-fill { background: #67C100; }
.progress-warning .progress-fill { background: #E56809; }
.progress-danger .progress-fill { background: #DC0808; }
.progress-info .progress-fill { background: #3EBCB9; }

/* ==================== Value Chart Sub-cards ==================== */
.value-chart-sub1 {
  background-color: rgba(90, 103, 245, 0.12) !important;
  position: relative;
  margin-bottom: 30px;
}
.value-chart-sub2 {
  background-color: rgba(255, 164, 122, 0.15) !important;
  position: relative;
  margin-bottom: 30px;
}
.value-chart-body {
  display: flex;
  align-items: center;
  padding: 25px;
  gap: 10px;
}
.round-progress-section {
  flex: 0 0 50%;
}
.knob-chart {
  width: 100%;
  height: 120px;
}
.valuechart-detail {
  flex: 0 0 50%;
}
.valuechart-detail p {
  color: #9993B4;
  font-size: 16px;
  margin: 0 0 5px;
}
.valuechart-detail h2 {
  color: #5A67F5;
  font-size: 22px;
  margin: 0;
}
.value-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 9px;
  padding: 5px 10px;
  border-radius: 9px;
  background-color: #5A67F5;
  color: #fff;
}
.stock-chart-section {
  flex: 0 0 50%;
}
.stock-chart {
  width: 100%;
  height: 120px;
}

/* ==================== 超越边界 ==================== */
.beyo-line {
  background-color: #fff;
  border-radius: 20px;
  margin-bottom: 30px;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(8, 21, 66, 0.05);
}
.beyo-header {
  background-color: #5A67F5;
  padding: 0 15px;
  overflow: hidden;
}
.beyo-chart {
  width: 100%;
  height: 270px;
  margin-bottom: -32px;
  margin-top: -18px;
}
.beyo-detail {
  padding: 29px 20px;
}
.beyo-detail h3 {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 10px;
}
.beyo-detail > p {
  font-size: 14px;
  width: 60%;
  margin: 0 0 20px;
  color: #2B2B2B;
  line-height: 1.5;
}
.date-history {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.beyo-avatars {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: 10px;
}
.beyo-avatars li img {
  width: 34px;
  height: 34px;
  border-radius: 50%;
}
.beyo-avatars li h2 {
  margin: 0;
  padding-left: 5px;
  font-size: 22px;
  color: #5A67F5;
}
.date-label {
  text-align: center;
  background: #fff;
  padding: 10px;
  border-radius: 10px;
  line-height: 1;
  box-shadow: 0 0 10px rgba(8, 21, 66, 0.05);
}
.date-label h3 {
  margin: 0 0 2px;
  font-weight: 700;
  font-size: 20px;
  color: #5A67F5;
}
.date-label p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  text-transform: capitalize;
}

/* ==================== Investment Chart ==================== */
.investment-chart .card-body {
  padding: 25px;
}
.investment-group {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.invest-label {
  text-align: center;
  font-weight: 500;
  font-size: 18px;
  color: #5A67F5;
  margin-bottom: 5px;
}
.invest-chart-sm {
  width: 100%;
  height: 108px;
}
.chart-detail {
  text-align: center;
  margin-top: 5px;
}
.chart-detail h5 {
  color: #9993B4;
  font-size: 14px;
  font-weight: 400;
  margin: 0 0 5px;
}
.chart-detail h2 {
  font-size: 22px;
  color: #5A67F5;
  margin: 0;
}

/* ==================== 热门社交媒体 ==================== */
.social-shared .card-header {
  padding: 25px 25px 0;
}
.social-shared .card-body {
  padding: 15px 25px 25px;
}
.social-list {
  display: flex;
  flex-direction: column;
}
.social-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  gap: 12px;
}
.social-item:hover {
  background-color: rgba(90, 103, 245, 0.14);
  border-radius: 8px;
  margin: 0 -10px;
  padding: 8px 10px;
}
.social-icon img {
  width: 34px;
  height: 34px;
  border-radius: 50%;
}
.social-icon-text {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(90, 103, 245, 0.12);
  color: #5A67F5;
  font-size: 14px;
  font-weight: 600;
  margin: 0;
}
.social-info {
  flex: 1;
  min-width: 0;
}
.social-info h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.social-info p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #909399;
}
.social-trend {
  display: flex;
  align-items: center;
  gap: 5px;
}
.trend-up-icon {
  color: #67C100;
  font-size: 12px;
}
.social-trend h5 {
  margin: 0;
  font-size: 14px;
  color: #2B2B2B;
}
.social-value h5 {
  margin: 0;
  font-size: 14px;
  color: #2B2B2B;
  white-space: nowrap;
}

/* ==================== Upgrade History ==================== */
.upgrade-history {
  position: relative;
  height: 250px;
  /* ApeAdmin 原版：插画从顶部探出，不被裁切 */
  overflow: visible;
}
.upgrade-body {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 25px;
  position: relative;
  z-index: 2;
}
.upgrade-text h3 {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 10px;
}
.upgrade-text p {
  width: 65%;
  font-size: 14px;
  color: #2B2B2B;
  margin: 0 0 20px;
  line-height: 1.5;
}
.upgrade-btn {
  display: inline-block;
  background-color: #5A67F5;
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}
.upgrade-btn:hover {
  background-color: #fff !important;
  border: 1px solid #5A67F5;
  color: #5A67F5;
}
.upgrade-img {
  position: absolute;
  top: -10px;
  right: -20px;
  z-index: 1;
}
.upgrade-img img {
  /* ApeAdmin 1:1：高度补齐至卡片底部贴齐（250 - 10 + 20 = 260） */
  height: 260px;
}

/* Responsive */
@media (max-width: 1600px) {
  .yearly-chart { height: 210px; }
  .profile-greeting .greeting-text h1 { font-size: 26px; }
  .greeting-img img { max-height: 220px; }
  .transaction-body { overflow-x: auto; }
  .transaction-table thead th {
    padding: 12px 8px 12px 16px;
    font-size: 14px;
  }
  .transaction-table thead th:first-child { padding-left: 16px; }
  .transaction-table thead th:last-child { padding-right: 16px; }
  .transaction-table tbody td { padding: 10px 8px; }
  .transaction-table tbody td:first-child { padding-left: 16px; border-left: 16px solid #EFF3F9; }
  .transaction-table tbody td:last-child { padding-right: 16px; border-right: 16px solid #EFF3F9; }
}
@media (max-width: 1200px) {
  .profile-greeting { height: auto; min-height: 200px; }
  .profile-greeting .greeting-text p { width: 80%; }
  .yearly-chart { height: 200px; }
  .beyo-chart { height: 220px; }
  .greeting-img img { max-height: 200px; }
}
@media (max-width: 992px) {
  .yearly-chart { height: 200px; }
  .profile-greeting .greeting-text p { width: 100%; }
  .profile-greeting .greeting-text h1 { font-size: 22px; }
  .beyo-detail > p { width: 100%; }
  .upgrade-text p { width: 100%; }
  .greeting-img img { max-height: 180px; }
  .beyo-chart { height: 200px; }
  .transaction-body { overflow-x: auto; }
  .transaction-table thead th { font-size: 14px; }
}
@media (max-width: 768px) {
  .greeting-img { display: none; }
  .profile-greeting .greeting-text { width: 100%; max-width: 100%; }
  .profile-greeting .greeting-text p { font-size: 14px; width: 100%; }
  .profile-greeting .greeting-text h1 { font-size: 20px; }
  .transaction-table { min-width: 500px; }
  .transaction-body { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .value-chart-body { flex-direction: column; gap: 5px; }
  .round-progress-section, .valuechart-detail { flex: none; width: 100%; text-align: center; }
  .knob-chart, .stock-chart { height: 100px; }
  .best-sellers-table { min-width: 500px; }
  .investment-chart .el-row { display: flex; flex-direction: column; gap: 20px; }
  .investment-chart .el-row .el-col { width: 100%; }
}
@media (max-width: 575px) {
  .profile-greeting { min-height: 160px; }
  .profile-greeting .greeting-body { padding: 20px 18px; }
  .profile-greeting .greeting-text h1 { font-size: 18px; margin-bottom: 6px; }
  .profile-greeting .greeting-text p { font-size: 13px; margin-bottom: 14px; }
  .greeting-btn { padding: 8px 12px; font-size: 13px; }
  .yearly-view .card-header { padding: 18px 18px 0; }
  .yearly-chart { height: 170px; }
  .activity-review .card-body { padding: 12px 18px 18px; }
  .activity-item { gap: 10px; }
  .activity-avatar { width: 32px; height: 32px; }
  .transaction-table thead th { font-size: 13px; padding: 10px 8px; }
  .transaction-table tbody td { padding: 10px 8px; }
  .value-chart-body { padding: 18px; }
  .valuechart-detail h2 { font-size: 18px; }
  .valuechart-detail p { font-size: 13px; }
  .beyo-detail { padding: 20px 18px; }
  .beyo-detail h3 { font-size: 17px; }
  .beyo-detail > p { font-size: 13px; }
  .beyo-avatars li img { width: 28px; height: 28px; }
  .beyo-avatars li h2 { font-size: 18px; }
  .investment-chart .card-body { padding: 18px; }
  .invest-label { font-size: 14px; }
  .invest-chart-sm { height: 80px; }
  .chart-detail h2 { font-size: 18px; }
  .upgrade-history { height: 200px; }
  .upgrade-body { padding: 18px; }
  .upgrade-text h3 { font-size: 16px; }
  .upgrade-text p { font-size: 12px; margin-bottom: 14px; }
  .upgrade-img { display: none; }
}
</style>
