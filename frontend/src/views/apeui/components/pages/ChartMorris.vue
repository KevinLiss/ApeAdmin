<template>
  <div>
    <PageHeader title="Chart Morris" :breadcrumb="['APEUI库', 'Components', 'Chart Morris']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Area Chart</span>
          </template>
          <v-chart class="chart" :option="areaOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Stacked Area</span>
          </template>
          <v-chart class="chart" :option="stackedAreaOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Bar + Line</span>
          </template>
          <v-chart class="chart" :option="barLineOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Donut Chart</span>
          </template>
          <v-chart class="chart" :option="donutOption" autoresize />
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
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'
const INFO = '#3EBCB9'
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']

/* 1. Area Chart — gradient area */
const areaOption = {
  tooltip: { trigger: 'axis' },
  grid: { left: '3%', right: '4%', top: '8%', bottom: '5%', containLabel: true },
  xAxis: { type: 'category', data: months, boundaryGap: false },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: [120, 282, 111, 234, 220, 178, 212, 282, 231],
    smooth: true,
    symbol: 'none',
    lineStyle: { color: PRIMARY, width: 3 },
    areaStyle: {
      color: {
        type: 'linear' as const,
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(90, 103, 245, 0.6)' },
          { offset: 1, color: 'rgba(90, 103, 245, 0.02)' },
        ],
      },
    },
  }],
}

/* 2. Stacked Area — 3 series */
const stackedAreaOption = {
  tooltip: { trigger: 'axis' },
  legend: { data: ['Email', 'Affiliate', 'Direct'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: months, boundaryGap: false },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Email', type: 'line', stack: 'total', data: [120, 132, 101, 134, 90, 230, 210, 182, 191],
      smooth: true, symbol: 'none',
      areaStyle: { opacity: 0.7, color: PRIMARY },
      lineStyle: { color: PRIMARY },
    },
    {
      name: 'Affiliate', type: 'line', stack: 'total', data: [220, 182, 191, 234, 290, 330, 310, 123, 442],
      smooth: true, symbol: 'none',
      areaStyle: { opacity: 0.7, color: SECONDARY },
      lineStyle: { color: SECONDARY },
    },
    {
      name: 'Direct', type: 'line', stack: 'total', data: [150, 232, 201, 154, 190, 330, 410, 150, 232],
      smooth: true, symbol: 'none',
      areaStyle: { opacity: 0.7, color: SUCCESS },
      lineStyle: { color: SUCCESS },
    },
  ],
}

/* 3. Bar + Line combo */
const barLineOption = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
  legend: { data: ['Sales', 'Target'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: months },
  yAxis: [
    { type: 'value', name: 'Sales' },
    { type: 'value', name: 'Target' },
  ],
  series: [
    { name: 'Sales', type: 'bar', data: [320, 332, 301, 334, 390, 330, 320, 332, 301], itemStyle: { color: PRIMARY, borderRadius: [4, 4, 0, 0] } },
    { name: 'Target', type: 'line', yAxisIndex: 1, data: [300, 350, 330, 360, 400, 380, 350, 380, 350], smooth: true, lineStyle: { color: SECONDARY, width: 3 }, itemStyle: { color: SECONDARY } },
  ],
}

/* 4. Donut Chart — ring progress */
const donutOption = {
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, left: 'center' },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    center: ['50%', '45%'],
    itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
    label: { show: true, formatter: '{d}%' },
    data: [
      { value: 500, name: 'Completed', itemStyle: { color: PRIMARY } },
      { value: 300, name: 'In Progress', itemStyle: { color: SECONDARY } },
      { value: 150, name: 'Pending', itemStyle: { color: SUCCESS } },
      { value: 50, name: 'Cancelled', itemStyle: { color: INFO } },
    ],
  }],
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
