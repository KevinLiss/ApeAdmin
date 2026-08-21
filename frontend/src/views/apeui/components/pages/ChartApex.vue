<template>
  <div>
    <PageHeader title="Apex 图表" :breadcrumb="['APEUI库', '组件示例', 'Apex 图表']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">基础折线图</span>
          </template>
          <v-chart class="chart" :option="basicLineOption" autoresize />
        </el-card>
      </el-col>

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
            <span class="card-title">Smooth Line</span>
          </template>
          <v-chart class="chart" :option="smoothLineOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Stepped Line</span>
          </template>
          <v-chart class="chart" :option="steppedLineOption" autoresize />
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
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

/* 1. 基础折线图 — 3 lines */
const basicLineOption = {
  tooltip: { trigger: 'axis' },
  legend: { data: ['Product A', 'Product B', 'Product C'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: months, boundaryGap: false },
  yAxis: { type: 'value' },
  series: [
    { name: 'Product A', type: 'line', data: [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 330], itemStyle: { color: PRIMARY } },
    { name: 'Product B', type: 'line', data: [220, 182, 191, 234, 290, 330, 310, 123, 442, 321, 90, 149], itemStyle: { color: SECONDARY } },
    { name: 'Product C', type: 'line', data: [150, 232, 201, 154, 190, 330, 410, 150, 232, 201, 154, 190], itemStyle: { color: SUCCESS } },
  ],
}

/* 2. Area Chart — 2 area lines with gradient */
const areaOption = {
  tooltip: { trigger: 'axis' },
  legend: { data: ['Revenue', 'Profit'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: months, boundaryGap: false },
  yAxis: { type: 'value' },
  series: [
    {
      name: 'Revenue',
      type: 'line',
      data: [320, 332, 301, 334, 390, 330, 320, 332, 301, 334, 390, 330],
      areaStyle: {
        color: {
          type: 'linear' as const,
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(90, 103, 245, 0.5)' },
            { offset: 1, color: 'rgba(90, 103, 245, 0.02)' },
          ],
        },
      },
      lineStyle: { color: PRIMARY, width: 3 },
      itemStyle: { color: PRIMARY },
    },
    {
      name: 'Profit',
      type: 'line',
      data: [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 150],
      areaStyle: {
        color: {
          type: 'linear' as const,
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(255, 164, 122, 0.5)' },
            { offset: 1, color: 'rgba(255, 164, 122, 0.02)' },
          ],
        },
      },
      lineStyle: { color: SECONDARY, width: 3 },
      itemStyle: { color: SECONDARY },
    },
  ],
}

/* 3. Smooth Line — 2 smooth curves */
const smoothLineOption = {
  tooltip: { trigger: 'axis' },
  legend: { data: ['Desktop', 'Mobile'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: months, boundaryGap: false },
  yAxis: { type: 'value' },
  series: [
    { name: 'Desktop', type: 'line', smooth: true, data: [320, 332, 301, 334, 390, 330, 320, 332, 301, 334, 390, 330], lineStyle: { color: PRIMARY, width: 3 }, itemStyle: { color: PRIMARY } },
    { name: 'Mobile', type: 'line', smooth: true, data: [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 150], lineStyle: { color: SECONDARY, width: 3 }, itemStyle: { color: SECONDARY } },
  ],
}

/* 4. Stepped Line — step chart */
const steppedLineOption = {
  tooltip: { trigger: 'axis' },
  legend: { data: ['Step Start', 'Step Middle', 'Step End'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: months, boundaryGap: false },
  yAxis: { type: 'value' },
  series: [
    { name: 'Step Start', type: 'line', step: 'start', data: [120, 132, 101, 134, 90, 230, 210, 182, 191, 234, 290, 150], lineStyle: { color: PRIMARY, width: 2 }, itemStyle: { color: PRIMARY } },
    { name: 'Step Middle', type: 'line', step: 'middle', data: [220, 282, 201, 234, 190, 330, 310, 150, 232, 201, 154, 190], lineStyle: { color: SECONDARY, width: 2 }, itemStyle: { color: SECONDARY } },
    { name: 'Step End', type: 'line', step: 'end', data: [150, 232, 201, 154, 190, 330, 410, 150, 232, 201, 154, 190], lineStyle: { color: SUCCESS, width: 2 }, itemStyle: { color: SUCCESS } },
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
