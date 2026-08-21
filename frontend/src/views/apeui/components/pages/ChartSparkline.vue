<template>
  <div>
    <PageHeader title="Chart Sparkline" :breadcrumb="['APEUI库', 'Components', 'Chart Sparkline']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Sparkline Line</span>
          </template>
          <v-chart class="chart" :option="sparklineLineOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Sparkline Bar</span>
          </template>
          <v-chart class="chart" :option="sparklineBarOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Sparkline Tristate</span>
          </template>
          <v-chart class="chart" :option="sparklineTristateOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Sparkline Bullet</span>
          </template>
          <v-chart class="chart" :option="sparklineBulletOption" autoresize />
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
import { LineChart, BarChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, GridComponent])

const PRIMARY = '#534686'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'
const DANGER = '#DC0808'

const sparkBase = {
  grid: { left: 0, right: 0, top: 10, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { show: false },
}

/* 1. Sparkline Line — no axes, thin line */
const sparklineLineOption = {
  ...sparkBase,
  series: [{
    type: 'line',
    data: [10, 30, 20, 45, 35, 55, 40, 60, 50, 70, 65, 80],
    smooth: true,
    symbol: 'none',
    lineStyle: { color: PRIMARY, width: 3 },
    areaStyle: {
      color: {
        type: 'linear' as const,
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(83, 70, 134, 0.3)' },
          { offset: 1, color: 'rgba(83, 70, 134, 0.02)' },
        ],
      },
    },
  }],
}

/* 2. Sparkline Bar — no axes */
const sparklineBarOption = {
  ...sparkBase,
  series: [{
    type: 'bar',
    data: [20, 35, 25, 50, 30, 45, 55, 40, 60, 35, 50, 45],
    itemStyle: { color: SECONDARY, borderRadius: 3 },
    barWidth: '50%',
  }],
}

/* 3. Sparkline Tristate — green/red bars (up/down) */
const tristateData = [
  { value: 30, itemStyle: { color: SUCCESS } },
  { value: -20, itemStyle: { color: DANGER } },
  { value: 40, itemStyle: { color: SUCCESS } },
  { value: -15, itemStyle: { color: DANGER } },
  { value: 50, itemStyle: { color: SUCCESS } },
  { value: -30, itemStyle: { color: DANGER } },
  { value: 35, itemStyle: { color: SUCCESS } },
  { value: -10, itemStyle: { color: DANGER } },
  { value: 45, itemStyle: { color: SUCCESS } },
  { value: -25, itemStyle: { color: DANGER } },
  { value: 55, itemStyle: { color: SUCCESS } },
  { value: -20, itemStyle: { color: DANGER } },
]
const sparklineTristateOption = {
  ...sparkBase,
  grid: { left: 0, right: 0, top: 0, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false, min: -60, max: 60 },
  series: [{
    type: 'bar',
    data: tristateData,
    barWidth: '50%',
    itemStyle: { borderRadius: 3 },
  }],
}

/* 4. Sparkline Bullet — bullet chart (target + actual) */
const sparklineBulletOption = {
  ...sparkBase,
  grid: { left: 0, right: 0, top: '25%', bottom: '25%' },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false, min: 0, max: 100 },
  series: [
    {
      name: 'Range Low',
      type: 'bar',
      stack: 'bullet',
      data: [40],
      itemStyle: { color: '#E6E6E6' },
      barWidth: 30,
      barGap: '-100%',
    },
    {
      name: 'Range Mid',
      type: 'bar',
      stack: 'bullet',
      data: [30],
      itemStyle: { color: '#C8C4D4' },
      barWidth: 30,
      barGap: '-100%',
    },
    {
      name: 'Range High',
      type: 'bar',
      stack: 'bullet',
      data: [30],
      itemStyle: { color: '#B0ABC0' },
      barWidth: 30,
      barGap: '-100%',
    },
    {
      name: 'Actual',
      type: 'bar',
      data: [65],
      itemStyle: { color: PRIMARY },
      barWidth: 10,
      barGap: '-50%',
    },
    {
      name: 'Target',
      type: 'bar',
      data: [75],
      itemStyle: { color: DANGER },
      barWidth: 2,
      barGap: '-100%',
    },
  ],
}
</script>

<style scoped>
.card-title {
  font-weight: 600;
  color: #534686;
}
.chart {
  height: 300px;
}
</style>
