<template>
  <div>
    <PageHeader title="Peity 图表" :breadcrumb="['APEUI库', '组件示例', 'Peity 图表']" />

    <el-row :gutter="30">
      <!-- 迷你折线图 -->
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">迷你折线图</span>
          </template>
          <div class="mini-grid">
            <div class="mini-item">
              <span class="mini-label">Visitors</span>
              <v-chart class="mini-chart" :option="miniLine1" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Revenue</span>
              <v-chart class="mini-chart" :option="miniLine2" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Orders</span>
              <v-chart class="mini-chart" :option="miniLine3" autoresize />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Mini Bar Charts -->
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Mini Bar Charts</span>
          </template>
          <div class="mini-grid">
            <div class="mini-item">
              <span class="mini-label">Week Sales</span>
              <v-chart class="mini-chart" :option="miniBar1" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Monthly</span>
              <v-chart class="mini-chart" :option="miniBar2" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Quarter</span>
              <v-chart class="mini-chart" :option="miniBar3" autoresize />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Mini Pie Charts -->
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Mini Pie Charts</span>
          </template>
          <div class="mini-grid">
            <div class="mini-item">
              <span class="mini-label">Traffic</span>
              <v-chart class="mini-chart" :option="miniPie1" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Devices</span>
              <v-chart class="mini-chart" :option="miniPie2" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Sources</span>
              <v-chart class="mini-chart" :option="miniPie3" autoresize />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- Mini Area Charts -->
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Mini Area Charts</span>
          </template>
          <div class="mini-grid">
            <div class="mini-item">
              <span class="mini-label">Page Views</span>
              <v-chart class="mini-chart" :option="miniArea1" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Sessions</span>
              <v-chart class="mini-chart" :option="miniArea2" autoresize />
            </div>
            <div class="mini-item">
              <span class="mini-label">Bounce Rate</span>
              <v-chart class="mini-chart" :option="miniArea3" autoresize />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../PageHeader.vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'
const INFO = '#3EBCB9'
const WARNING = '#E56809'

/* Common mini chart config (no axes, no grid lines) */
const miniBase = {
  grid: { left: 0, right: 0, top: 5, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { show: false },
}

/* --- 迷你折线图 --- */
const miniLine1 = {
  ...miniBase,
  series: [{ type: 'line', data: [5, 20, 15, 35, 25, 40, 30, 50, 45], smooth: true, symbol: 'none', lineStyle: { color: PRIMARY, width: 2 } }],
}
const miniLine2 = {
  ...miniBase,
  series: [{ type: 'line', data: [30, 25, 40, 35, 50, 45, 55, 60, 52], smooth: true, symbol: 'none', lineStyle: { color: SECONDARY, width: 2 } }],
}
const miniLine3 = {
  ...miniBase,
  series: [{ type: 'line', data: [10, 30, 20, 45, 35, 50, 40, 55, 48], smooth: true, symbol: 'none', lineStyle: { color: SUCCESS, width: 2 } }],
}

/* --- Mini Bar Charts --- */
const miniBar1 = {
  ...miniBase,
  series: [{ type: 'bar', data: [20, 35, 25, 40, 30, 50, 45], itemStyle: { color: PRIMARY, borderRadius: 2 }, barWidth: '60%' }],
}
const miniBar2 = {
  ...miniBase,
  series: [{ type: 'bar', data: [30, 25, 45, 35, 50, 40, 55], itemStyle: { color: SECONDARY, borderRadius: 2 }, barWidth: '60%' }],
}
const miniBar3 = {
  ...miniBase,
  series: [{ type: 'bar', data: [15, 30, 20, 40, 25, 35, 50], itemStyle: { color: SUCCESS, borderRadius: 2 }, barWidth: '60%' }],
}

/* --- Mini Pie Charts --- */
const miniPieBase = {
  tooltip: { show: false },
  legend: { show: false },
}
const miniPie1 = {
  ...miniPieBase,
  series: [{
    type: 'pie', radius: ['40%', '65%'], center: ['50%', '50%'],
    label: { show: false },
    data: [
      { value: 60, itemStyle: { color: PRIMARY } },
      { value: 40, itemStyle: { color: '#E6E6E6' } },
    ],
  }],
}
const miniPie2 = {
  ...miniPieBase,
  series: [{
    type: 'pie', radius: ['40%', '65%'], center: ['50%', '50%'],
    label: { show: false },
    data: [
      { value: 45, itemStyle: { color: SECONDARY } },
      { value: 55, itemStyle: { color: '#E6E6E6' } },
    ],
  }],
}
const miniPie3 = {
  ...miniPieBase,
  series: [{
    type: 'pie', radius: ['40%', '65%'], center: ['50%', '50%'],
    label: { show: false },
    data: [
      { value: 70, itemStyle: { color: SUCCESS } },
      { value: 30, itemStyle: { color: '#E6E6E6' } },
    ],
  }],
}

/* --- Mini Area Charts --- */
function makeArea(data: number[], color: string) {
  return {
    ...miniBase,
    series: [{
      type: 'line', data, smooth: true, symbol: 'none',
      lineStyle: { color, width: 2 },
      areaStyle: {
        color: {
          type: 'linear' as const,
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: color + '80' },
            { offset: 1, color: color + '05' },
          ],
        },
      },
    }],
  }
}
const miniArea1 = makeArea([10, 25, 15, 35, 30, 45, 40, 55, 50], PRIMARY)
const miniArea2 = makeArea([20, 15, 30, 25, 40, 35, 50, 45, 60], SECONDARY)
const miniArea3 = makeArea([30, 20, 40, 25, 50, 30, 55, 40, 60], SUCCESS)
</script>

<style scoped>
.card-title {
  font-weight: 600;
  color: #5A67F5;
}
.mini-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.mini-item {
  flex: 1;
  min-width: 140px;
  text-align: center;
}
.mini-label {
  display: block;
  font-size: 13px;
  color: #6c757d;
  margin-bottom: 4px;
}
.mini-chart {
  height: 80px;
}
</style>
