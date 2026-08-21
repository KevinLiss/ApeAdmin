<template>
  <div>
    <PageHeader title="旋钮图表" :breadcrumb="['APEUI库', '组件示例', '旋钮图表']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">基础仪表盘</span>
          </template>
          <v-chart class="chart" :option="basicGaugeOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Speedometer</span>
          </template>
          <v-chart class="chart" :option="speedometerOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Dual Gauge</span>
          </template>
          <v-chart class="chart" :option="dualGaugeOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Progress Gauge</span>
          </template>
          <v-chart class="chart" :option="progressGaugeOption" autoresize />
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
import { GaugeChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'

use([CanvasRenderer, GaugeChart, TooltipComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'
const INFO = '#3EBCB9'

/* 1. 基础仪表盘 — 65% */
const basicGaugeOption = {
  series: [{
    type: 'gauge',
    radius: '85%',
    progress: { show: true, width: 18, itemStyle: { color: PRIMARY } },
    axisLine: { lineStyle: { width: 18, color: [[1, '#E6E6E6']] } },
    axisTick: { show: false },
    splitLine: { length: 15, lineStyle: { color: '#999', width: 2 } },
    axisLabel: { distance: 25, color: '#999' },
    pointer: { itemStyle: { color: PRIMARY } },
    anchor: { show: true, size: 20, itemStyle: { color: PRIMARY } },
    detail: { valueAnimation: true, fontSize: 28, offsetCenter: [0, '70%'], formatter: '{value}%', color: PRIMARY },
    data: [{ value: 65 }],
  }],
}

/* 2. Speedometer — 0-200 */
const speedometerOption = {
  series: [{
    type: 'gauge',
    min: 0,
    max: 200,
    radius: '85%',
    axisLine: {
      lineStyle: {
        width: 20,
        color: [
          [0.3, SUCCESS],
          [0.7, SECONDARY],
          [1, '#DC0808'],
        ],
      },
    },
    axisTick: { show: false },
    splitLine: { length: 15, lineStyle: { color: '#fff', width: 3 } },
    axisLabel: { distance: 25, color: '#999' },
    pointer: { itemStyle: { color: 'auto' } },
    detail: { valueAnimation: true, fontSize: 28, offsetCenter: [0, '70%'], formatter: '{value} km/h', color: PRIMARY },
    data: [{ value: 120 }],
  }],
}

/* 3. Dual Gauge — two gauges in one */
const dualGaugeOption = {
  series: [
    {
      type: 'gauge',
      min: 0,
      max: 100,
      radius: '75%',
      center: ['30%', '50%'],
      progress: { show: true, width: 14, itemStyle: { color: PRIMARY } },
      axisLine: { lineStyle: { width: 14, color: [[1, '#E6E6E6']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { valueAnimation: true, fontSize: 20, formatter: '{value}%', color: PRIMARY },
      data: [{ value: 72 }],
    },
    {
      type: 'gauge',
      min: 0,
      max: 100,
      radius: '75%',
      center: ['70%', '50%'],
      progress: { show: true, width: 14, itemStyle: { color: SECONDARY } },
      axisLine: { lineStyle: { width: 14, color: [[1, '#E6E6E6']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { valueAnimation: true, fontSize: 20, formatter: '{value}%', color: SECONDARY },
      data: [{ value: 45 }],
    },
  ],
}

/* 4. Progress Gauge — with progress ring */
const progressGaugeOption = {
  series: [{
    type: 'gauge',
    startAngle: 90,
    endAngle: -270,
    radius: '85%',
    pointer: { show: false },
    progress: {
      show: true,
      overlap: false,
      roundCap: true,
      clip: false,
      itemStyle: { color: INFO },
    },
    axisLine: { lineStyle: { width: 20, color: [[1, '#E6E6E6']] } },
    splitLine: { show: false },
    axisTick: { show: false },
    axisLabel: { show: false },
    data: [{ value: 85 }],
    detail: {
      valueAnimation: true,
      fontSize: 30,
      color: INFO,
      offsetCenter: ['0%', '0%'],
      formatter: '{value}%',
    },
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
