<template>
  <div>
    <PageHeader title="Google 图表" :breadcrumb="['APEUI库', '组件示例', 'Google 图表']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">折线与柱状组合图</span>
          </template>
          <v-chart class="chart" :option="comboOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Candlestick</span>
          </template>
          <v-chart class="chart" :option="candlestickOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Scatter Plot</span>
          </template>
          <v-chart class="chart" :option="scatterOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Bubble Chart</span>
          </template>
          <v-chart class="chart" :option="bubbleOption" autoresize />
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
import { BarChart, LineChart, ScatterChart, CandlestickChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, BarChart, LineChart, ScatterChart, CandlestickChart, GridComponent, TooltipComponent, LegendComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'

/* 1. 折线与柱状组合图 — dual y-axis */
const comboOption = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { data: ['Revenue', 'Growth'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'] },
  yAxis: [
    { type: 'value', name: 'Revenue', position: 'left' },
    { type: 'value', name: 'Growth %', position: 'right' },
  ],
  series: [
    { name: 'Revenue', type: 'bar', data: [320, 332, 301, 334, 390, 330, 320], itemStyle: { color: PRIMARY, borderRadius: [4, 4, 0, 0] } },
    { name: 'Growth', type: 'line', yAxisIndex: 1, data: [10, 15, 12, 20, 18, 25, 22], smooth: true, lineStyle: { color: SECONDARY, width: 3 }, itemStyle: { color: SECONDARY } },
  ],
}

/* 2. Candlestick — 7 K-lines */
const candlestickOption = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { data: ['K-Line'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: ['Aug 12', 'Aug 13', 'Aug 14', 'Aug 15', 'Aug 16', 'Aug 17', 'Aug 18'] },
  yAxis: { type: 'value', scale: true },
  series: [{
    type: 'candlestick',
    data: [
      [20, 34, 10, 38],
      [40, 35, 30, 50],
      [31, 38, 28, 44],
      [38, 42, 22, 45],
      [42, 50, 35, 55],
      [50, 46, 40, 58],
      [46, 54, 42, 60],
    ],
    itemStyle: {
      color: SUCCESS,
      color0: '#DC0808',
      borderColor: SUCCESS,
      borderColor0: '#DC0808',
    },
  }],
}

/* 3. Scatter Plot — 3 groups */
function genScatter(centerX: number, centerY: number, count: number) {
  return Array.from({ length: count }, () => [
    +(centerX + (Math.random() - 0.5) * 30).toFixed(2),
    +(centerY + (Math.random() - 0.5) * 30).toFixed(2),
  ])
}
const scatterOption = {
  tooltip: { trigger: 'item' },
  legend: { data: ['Group A', 'Group B', 'Group C'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'value', min: 0, max: 100 },
  yAxis: { type: 'value', min: 0, max: 100 },
  series: [
    { name: 'Group A', type: 'scatter', data: genScatter(25, 25, 30), itemStyle: { color: PRIMARY } },
    { name: 'Group B', type: 'scatter', data: genScatter(75, 75, 30), itemStyle: { color: SECONDARY } },
    { name: 'Group C', type: 'scatter', data: genScatter(50, 50, 30), itemStyle: { color: SUCCESS } },
  ],
}

/* 4. Bubble Chart — scatter with symbolSize */
function genBubble(centerX: number, centerY: number, count: number) {
  return Array.from({ length: count }, () => [
    +(centerX + (Math.random() - 0.5) * 40).toFixed(2),
    +(centerY + (Math.random() - 0.5) * 40).toFixed(2),
    Math.round(Math.random() * 40 + 10),
  ])
}
const bubbleOption = {
  tooltip: { trigger: 'item' },
  legend: { data: ['East', 'West', 'North'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'value', min: 0, max: 100 },
  yAxis: { type: 'value', min: 0, max: 100 },
  series: [
    { name: 'East', type: 'scatter', data: genBubble(30, 70, 15), symbolSize: (d: number[]) => d[2], itemStyle: { color: PRIMARY, opacity: 0.7 } },
    { name: 'West', type: 'scatter', data: genBubble(70, 30, 15), symbolSize: (d: number[]) => d[2], itemStyle: { color: SECONDARY, opacity: 0.7 } },
    { name: 'North', type: 'scatter', data: genBubble(50, 50, 15), symbolSize: (d: number[]) => d[2], itemStyle: { color: SUCCESS, opacity: 0.7 } },
  ],
}
</script>

<style scoped>
.card-title {
  font-weight: 600;
  color: #5A67F5;
}
.chart {
  height: 320px;
}
</style>
