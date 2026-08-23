<template>
  <div class="dashboard-monitor">
    <PageHeader title="系统仪表盘" :breadcrumb="['系统仪表盘']" />

    <div class="dash-container">
      <!-- Row 1: 欢迎回来 (10/24) + CPU 使用 (7/24) + 内存使用 (7/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- 欢迎回来 -->
        <el-col :xs="24" :sm="24" :lg="10">
          <div class="ape-card profile-greeting">
            <div class="greeting-body">
              <div class="greeting-text">
                <h1>欢迎回来，{{ displayName }}</h1>
                <p>{{ sysData.system?.hostname || 'ApeAdmin' }} · 运行 {{ formatUptime(sysData.system?.uptime_seconds || 0) }}</p>
                <div class="greeting-stats">
                  <div class="gs-item">
                    <span class="gs-label">进程数</span>
                    <span class="gs-value">{{ sysData.system?.process_count || 0 }}</span>
                  </div>
                  <div class="gs-divider"></div>
                  <div class="gs-item">
                    <span class="gs-label">操作系统</span>
                    <span class="gs-value">{{ sysData.system?.os || '-' }}</span>
                  </div>
                </div>
              </div>
              <div class="greeting-img">
                <img src="/assets/images/dashboard/profile-greeting/bg.png" alt="" />
              </div>
            </div>
          </div>
        </el-col>

        <!-- CPU 使用 -->
        <el-col :xs="24" :sm="12" :lg="7">
          <div class="ape-card metric-card">
            <div class="card-header">
              <h3>CPU 使用情况</h3>
              <span class="metric-badge" :class="getMetricClass(sysData.cpu?.percent || 0)">实时</span>
            </div>
            <div class="card-body">
              <v-chart class="metric-chart" :option="cpuChartOption" autoresize />
              <div class="metric-info">
                <div class="mi-item">
                  <span class="mi-label">使用率</span>
                  <span class="mi-value">{{ sysData.cpu?.percent || 0 }}%</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">物理核心</span>
                  <span class="mi-value">{{ sysData.cpu?.cores_physical || 0 }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">逻辑核心</span>
                  <span class="mi-value">{{ sysData.cpu?.cores_logical || 0 }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">负载均衡</span>
                  <span class="mi-value">{{ (sysData.cpu?.load_avg || [0,0,0]).join(' / ') }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 内存使用 -->
        <el-col :xs="24" :sm="12" :lg="7">
          <div class="ape-card metric-card">
            <div class="card-header">
              <h3>内存使用情况</h3>
              <span class="metric-badge" :class="getMetricClass(sysData.memory?.percent || 0)">实时</span>
            </div>
            <div class="card-body">
              <v-chart class="metric-chart" :option="memChartOption" autoresize />
              <div class="metric-info">
                <div class="mi-item">
                  <span class="mi-label">已用</span>
                  <span class="mi-value">{{ formatBytes(sysData.memory?.used || 0) }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">可用</span>
                  <span class="mi-value">{{ formatBytes(sysData.memory?.available || 0) }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">总量</span>
                  <span class="mi-value">{{ formatBytes(sysData.memory?.total || 0) }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">使用率</span>
                  <span class="mi-value">{{ sysData.memory?.percent || 0 }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 2: 磁盘情况 (8/24) + 网络情况 (8/24) + 系统信息 (8/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- 磁盘情况 -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="ape-card metric-card">
            <div class="card-header">
              <h3>磁盘情况</h3>
              <span class="metric-badge" :class="getMetricClass(sysData.disk?.percent || 0)">/</span>
            </div>
            <div class="card-body">
              <v-chart class="metric-chart" :option="diskChartOption" autoresize />
              <div class="metric-info">
                <div class="mi-item">
                  <span class="mi-label">已用</span>
                  <span class="mi-value">{{ formatBytes(sysData.disk?.used || 0) }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">可用</span>
                  <span class="mi-value">{{ formatBytes(sysData.disk?.free || 0) }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">总量</span>
                  <span class="mi-value">{{ formatBytes(sysData.disk?.total || 0) }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">使用率</span>
                  <span class="mi-value">{{ sysData.disk?.percent || 0 }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 网络情况 -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="ape-card metric-card">
            <div class="card-header">
              <h3>网络情况</h3>
              <span class="metric-badge">实时</span>
            </div>
            <div class="card-body">
              <v-chart class="metric-chart" :option="netChartOption" autoresize />
              <div class="metric-info">
                <div class="mi-item">
                  <span class="mi-label">发送速率</span>
                  <span class="mi-value">{{ formatBytes(sysData.network?.sent_rate || 0) }}/s</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">接收速率</span>
                  <span class="mi-value">{{ formatBytes(sysData.network?.recv_rate || 0) }}/s</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">累计发送</span>
                  <span class="mi-value">{{ formatBytes(sysData.network?.bytes_sent || 0) }}</span>
                </div>
                <div class="mi-item">
                  <span class="mi-label">累计接收</span>
                  <span class="mi-value">{{ formatBytes(sysData.network?.bytes_recv || 0) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 系统信息 -->
        <el-col :xs="24" :sm="24" :lg="8">
          <div class="ape-card info-card">
            <div class="card-header">
              <h3>系统信息</h3>
            </div>
            <div class="card-body">
              <div class="info-list">
                <div class="info-item">
                  <span class="info-label"><el-icon><Cpu /></el-icon> 主机名</span>
                  <span class="info-value">{{ sysData.system?.hostname || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label"><el-icon><Monitor /></el-icon> 操作系统</span>
                  <span class="info-value">{{ sysData.system?.os || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label"><el-icon><Timer /></el-icon> 运行时长</span>
                  <span class="info-value">{{ formatUptime(sysData.system?.uptime_seconds || 0) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label"><el-icon><Operation /></el-icon> 进程数</span>
                  <span class="info-value">{{ sysData.system?.process_count || 0 }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label"><el-icon><Coin /></el-icon> Swap 使用</span>
                  <span class="info-value">
                    {{ formatBytes(sysData.memory?.swap_used || 0) }} / {{ formatBytes(sysData.memory?.swap_total || 0) }}
                    ({{ sysData.memory?.swap_percent || 0 }}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 3: 已安装插件 (12/24) + 可用 MCP 列表 (12/24) -->
      <el-row :gutter="30" class="dash-row">
        <el-col :xs="24" :lg="12">
          <div class="ape-card list-card">
            <div class="card-header">
              <h3>已安装插件</h3>
              <span class="list-count">共 {{ sysData.plugins?.length || 0 }} 个</span>
            </div>
            <div class="card-body">
              <table class="info-table">
                <thead>
                  <tr>
                    <th>插件名称</th>
                    <th>版本</th>
                    <th>状态</th>
                    <th>安装日期</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="p in (sysData.plugins || [])" :key="p.id">
                    <td>
                      <div class="table-primary">
                        <el-icon class="table-icon"><Box /></el-icon>
                        <span>{{ p.display_name || p.name }}</span>
                      </div>
                    </td>
                    <td>v{{ p.version }}</td>
                    <td>
                      <span class="status-tag" :class="p.enabled ? 'status-on' : 'status-off'">
                        {{ p.enabled ? '已启用' : '已停用' }}
                      </span>
                    </td>
                    <td>{{ p.created_at || '-' }}</td>
                  </tr>
                  <tr v-if="!sysData.plugins?.length">
                    <td colspan="4" class="empty-row">暂无已安装插件</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-col>

        <el-col :xs="24" :lg="12">
          <div class="ape-card list-card">
            <div class="card-header">
              <h3>可用 MCP 列表</h3>
              <span class="list-count">共 {{ sysData.mcp_tools?.length || 0 }} 个</span>
            </div>
            <div class="card-body">
              <table class="info-table">
                <thead>
                  <tr>
                    <th>工具名称</th>
                    <th>描述</th>
                    <th>所需权限</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="t in (sysData.mcp_tools || [])" :key="t.name">
                    <td>
                      <div class="table-primary">
                        <el-icon class="table-icon"><Connection /></el-icon>
                        <span>{{ t.name }}</span>
                      </div>
                    </td>
                    <td class="desc-cell">{{ t.description || '-' }}</td>
                    <td>
                      <div class="perm-tags">
                        <span v-for="p in (t.required_permissions || [])" :key="p" class="perm-tag">{{ p }}</span>
                        <span v-if="!t.required_permissions?.length" class="perm-free">无需权限</span>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="!sysData.mcp_tools?.length">
                    <td colspan="3" class="empty-row">暂无可用 MCP 工具</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 4: 系统在线用户 (24/24) -->
      <el-row :gutter="30" class="dash-row">
        <el-col :span="24">
          <div class="ape-card list-card">
            <div class="card-header">
              <h3>系统在线用户</h3>
              <span class="list-count">最近 24 小时内 {{ sysData.online_users?.length || 0 }} 人在线</span>
            </div>
            <div class="card-body">
              <table class="info-table">
                <thead>
                  <tr>
                    <th>用户名</th>
                    <th>昵称</th>
                    <th>最近登录时间</th>
                    <th>登录 IP</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in (sysData.online_users || [])" :key="u.id">
                    <td>
                      <div class="table-primary">
                        <el-icon class="table-icon"><User /></el-icon>
                        <span>{{ u.username }}</span>
                      </div>
                    </td>
                    <td>{{ u.nickname || '-' }}</td>
                    <td>{{ u.last_login_at || '-' }}</td>
                    <td>{{ u.last_login_ip || '-' }}</td>
                    <td>
                      <span class="status-tag status-on">
                        <span class="online-dot"></span> 在线
                      </span>
                    </td>
                  </tr>
                  <tr v-if="!sysData.online_users?.length">
                    <td colspan="5" class="empty-row">最近 24 小时内无用户登录</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, reactive, computed } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart, BarChart, LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { Monitor, Cpu, Timer, Operation, Coin, Box, Connection, User } from '@element-plus/icons-vue'
import { getDashboardSystem } from '@/api'
import { useUserStore } from '@/stores/user'

use([CanvasRenderer, GaugeChart, BarChart, LineChart, TooltipComponent, LegendComponent, GridComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'
const WARNING = '#E56809'
const DANGER = '#DC0808'

// 当前登录用户（显示登录用户名）
const userStore = useUserStore()
const displayName = computed(() => userStore.username || '管理员')

// 系统数据（响应式）
const sysData = reactive<any>({})

// CPU 历史记录（用于趋势图）
const cpuHistory = ref<number[]>(Array(30).fill(0))
const memHistory = ref<number[]>(Array(30).fill(0))
const netSentHistory = ref<number[]>(Array(30).fill(0))
const netRecvHistory = ref<number[]>(Array(30).fill(0))

import { ref } from 'vue'

// 格式化字节
function formatBytes(n: number): string {
  if (!n) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++ }
  return `${n.toFixed(1)} ${units[i]}`
}

// 格式化运行时长
function formatUptime(seconds: number): string {
  const d = Math.floor(seconds / 86400)
  const h = Math.floor((seconds % 86400) / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  const parts: string[] = []
  if (d) parts.push(`${d}天`)
  if (h) parts.push(`${h}小时`)
  if (m) parts.push(`${m}分钟`)
  if (!d && !h) parts.push(`${s}秒`)
  return parts.join(' ') || '0秒'
}

// 根据使用率返回 CSS 类名
function getMetricClass(percent: number): string {
  if (percent >= 90) return 'badge-danger'
  if (percent >= 75) return 'badge-warning'
  if (percent >= 50) return 'badge-info'
  return 'badge-success'
}

// ===== ECharts Options =====
const cpuChartOption = computed(() => ({
  series: [{
    type: 'gauge',
    startAngle: 90,
    endAngle: -270,
    radius: '85%',
    progress: {
      show: true,
      overlap: false,
      roundCap: true,
      clip: false,
      itemStyle: { color: PRIMARY },
    },
    axisLine: { lineStyle: { width: 10, color: [[(sysData.cpu?.percent || 0) / 100, PRIMARY], [1, '#E8E8F5']] } },
    splitLine: { show: false },
    axisTick: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    data: [{ value: sysData.cpu?.percent || 0 }],
    detail: {
      valueAnimation: true,
      fontSize: 22,
      fontWeight: 'bold',
      color: PRIMARY,
      offsetCenter: ['0%', '0%'],
      formatter: '{value}%',
    },
  }],
}))

const memChartOption = computed(() => ({
  series: [{
    type: 'gauge',
    startAngle: 90,
    endAngle: -270,
    radius: '85%',
    progress: {
      show: true,
      overlap: false,
      roundCap: true,
      clip: false,
      itemStyle: { color: SECONDARY },
    },
    axisLine: { lineStyle: { width: 10, color: [[(sysData.memory?.percent || 0) / 100, SECONDARY], [1, '#E8E8F5']] } },
    splitLine: { show: false },
    axisTick: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    data: [{ value: sysData.memory?.percent || 0 }],
    detail: {
      valueAnimation: true,
      fontSize: 22,
      fontWeight: 'bold',
      color: SECONDARY,
      offsetCenter: ['0%', '0%'],
      formatter: '{value}%',
    },
  }],
}))

const diskChartOption = computed(() => ({
  series: [{
    type: 'gauge',
    startAngle: 90,
    endAngle: -270,
    radius: '85%',
    progress: {
      show: true,
      overlap: false,
      roundCap: true,
      clip: false,
      itemStyle: { color: SUCCESS },
    },
    axisLine: { lineStyle: { width: 10, color: [[(sysData.disk?.percent || 0) / 100, SUCCESS], [1, '#E8E8F5']] } },
    splitLine: { show: false },
    axisTick: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    data: [{ value: sysData.disk?.percent || 0 }],
    detail: {
      valueAnimation: true,
      fontSize: 22,
      fontWeight: 'bold',
      color: SUCCESS,
      offsetCenter: ['0%', '0%'],
      formatter: '{value}%',
    },
  }],
}))

const netChartOption = computed(() => ({
  series: [
    {
      name: '发送',
      type: 'line',
      data: netSentHistory.value,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: PRIMARY },
      areaStyle: {
        color: {
          type: 'linear' as const,
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(90, 103, 245, 0.3)' },
            { offset: 1, color: 'rgba(90, 103, 245, 0.02)' },
          ],
        },
      },
    },
    {
      name: '接收',
      type: 'line',
      data: netRecvHistory.value,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 2, color: SECONDARY },
      areaStyle: {
        color: {
          type: 'linear' as const,
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(255, 164, 122, 0.3)' },
            { offset: 1, color: 'rgba(255, 164, 122, 0.02)' },
          ],
        },
      },
    },
  ],
  grid: { left: 5, right: 5, top: 25, bottom: 5 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { trigger: 'axis', formatter: (params: any) => params.map((p: any) => `${p.seriesName}: ${formatBytes(p.value)}/s`).join('<br/>') },
  legend: {
    data: ['发送', '接收'],
    bottom: 0,
    itemWidth: 12,
    itemHeight: 12,
    textStyle: { fontSize: 11, color: '#9993B4' },
  },
}))

// 获取数据
async function fetchData() {
  try {
    const res = await getDashboardSystem()
    Object.assign(sysData, res)
    // 更新网络历史
    cpuHistory.value.shift()
    cpuHistory.value.push(sysData.cpu?.percent || 0)
    memHistory.value.shift()
    memHistory.value.push(sysData.memory?.percent || 0)
    netSentHistory.value.shift()
    netSentHistory.value.push(sysData.network?.sent_rate || 0)
    netRecvHistory.value.shift()
    netRecvHistory.value.push(sysData.network?.recv_rate || 0)
  } catch (e) {
    console.error('[Monitor] 获取系统数据失败:', e)
  }
}

let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  fetchData()
  pollTimer = setInterval(fetchData, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped>
.dashboard-monitor {
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

/* ==================== Welcome Card ==================== */
.profile-greeting {
  background: linear-gradient(135deg, #5A67F5 0%, #47D8FF 100%);
  height: 254px;
  position: relative;
  overflow: hidden;
}
.greeting-body {
  padding: 30px;
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.greeting-text {
  position: relative;
  z-index: 2;
  max-width: 65%;
}
.greeting-text h1 {
  color: #fff;
  font-size: 26px;
  font-weight: 600;
  margin: 0 0 8px;
  white-space: nowrap;
}
.greeting-text p {
  color: rgba(255,255,255,0.85);
  font-size: 13px;
  margin: 0 0 20px;
  line-height: 1.5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.greeting-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}
.gs-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.gs-label {
  color: rgba(255,255,255,0.7);
  font-size: 12px;
}
.gs-value {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}
.gs-divider {
  width: 1px;
  height: 30px;
  background: rgba(255,255,255,0.3);
}
.greeting-img {
  position: absolute;
  bottom: -2px;
  right: -20px;
  z-index: 1;
  height: 100%;
  display: flex;
  align-items: flex-end;
  pointer-events: none;
}
.greeting-img img {
  height: 230px;
  object-fit: contain;
}

/* ==================== Metric Cards (CPU / Memory / Disk / Network) ==================== */
.metric-card .card-header {
  padding: 20px 20px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.metric-card .card-header h3 {
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0;
}
.metric-badge {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: 9px;
  background: rgba(103, 193, 0, 0.1);
  color: #67C100;
}
.badge-success { background: rgba(103, 193, 0, 0.1); color: #67C100; }
.badge-info { background: rgba(62, 188, 185, 0.1); color: #3EBCB9; }
.badge-warning { background: rgba(229, 104, 9, 0.1); color: #E56809; }
.badge-danger { background: rgba(220, 8, 8, 0.1); color: #DC0808; }

.metric-card .card-body {
  padding: 15px 20px 20px;
}
.metric-chart {
  width: 100%;
  height: 140px;
}
.metric-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}
.mi-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 12px;
  background: #F8F9FB;
  border-radius: 8px;
}
.mi-label {
  color: #909399;
  font-size: 12px;
}
.mi-value {
  color: #2B2B2B;
  font-size: 13px;
  font-weight: 500;
}

/* ==================== System Info Card ==================== */
.info-card .card-header {
  padding: 20px 20px 0;
}
.info-card .card-header h3 {
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0;
}
.info-card .card-body {
  padding: 15px 20px 20px;
}
.info-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #F1F3FF;
}
.info-item:last-child {
  border-bottom: none;
}
.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
}
.info-label .el-icon {
  font-size: 16px;
  color: #5A67F5;
}
.info-value {
  color: #2B2B2B;
  font-size: 14px;
  font-weight: 500;
  text-align: right;
}

/* ==================== List Cards (Plugins / MCP / Users) ==================== */
.list-card .card-header {
  padding: 20px 25px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.list-card .card-header h3 {
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0;
}
.list-count {
  font-size: 13px;
  color: #909399;
}
.list-card .card-body {
  padding: 15px 0 0;
}
.info-table {
  width: 100%;
  border-collapse: collapse;
}
.info-table thead th {
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
  padding: 12px 12px;
  text-align: left;
  border-bottom: 2px solid #F1F3FF;
}
.info-table thead th:first-child { padding-left: 25px; }
.info-table thead th:last-child { padding-right: 25px; }
.info-table tbody tr {
  border-bottom: 1px solid #F8F9FB;
  transition: background 0.2s;
}
.info-table tbody tr:hover {
  background: #F8F9FB;
}
.info-table tbody td {
  padding: 12px 12px;
  font-size: 13px;
  color: #2B2B2B;
  vertical-align: middle;
}
.info-table tbody td:first-child { padding-left: 25px; }
.info-table tbody td:last-child { padding-right: 25px; }
.table-primary {
  display: flex;
  align-items: center;
  gap: 8px;
}
.table-icon {
  font-size: 16px;
  color: #5A67F5;
  flex-shrink: 0;
}
.desc-cell {
  color: #909399;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  white-space: nowrap;
}
.status-on {
  background: rgba(103, 193, 0, 0.1);
  color: #67C100;
}
.status-off {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}
.online-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #67C100;
  display: inline-block;
}
.perm-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.perm-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(90, 103, 245, 0.1);
  color: #5A67F5;
}
.perm-free {
  font-size: 12px;
  color: #909399;
}
.empty-row {
  text-align: center !important;
  color: #909399 !important;
  padding: 30px 0 !important;
}

/* ==================== Responsive ==================== */
@media (max-width: 1400px) {
  .profile-greeting .greeting-text h1 { font-size: 20px; }
  .greeting-img img { height: 190px; }
  .greeting-img { right: -10px; }
}
@media (max-width: 1200px) {
  .profile-greeting { height: auto; min-height: 200px; }
  .profile-greeting .greeting-text h1 { font-size: 20px; }
  .greeting-text { max-width: 100%; }
  .greeting-stats { flex-wrap: wrap; gap: 10px; }
  .gs-divider { display: none; }
  .greeting-img { display: none; }
}
@media (max-width: 992px) {
  .metric-chart { height: 120px; }
}
@media (max-width: 768px) {
  .profile-greeting { min-height: 160px; }
  .profile-greeting .greeting-body { padding: 20px; }
  .greeting-img { display: none; }
  .profile-greeting .greeting-text { width: 100%; }
  .profile-greeting .greeting-text h1 { font-size: 20px; }
  .metric-info { grid-template-columns: 1fr; }
  .info-table { min-width: 500px; }
  .list-card .card-body { overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
</style>
