<template>
  <div>
    <PageHeader title="Chart.js 图表" :breadcrumb="['APEUI库', '组件示例', 'Chart.js 图表']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">基础柱状图</span>
          </template>
          <v-chart class="chart" :option="basicBarOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Grouped Bar</span>
          </template>
          <v-chart class="chart" :option="groupedBarOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Stacked Bar</span>
          </template>
          <v-chart class="chart" :option="stackedBarOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Horizontal Bar</span>
          </template>
          <v-chart class="chart" :option="horizontalBarOption" autoresize />
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
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'

/* 1. 基础柱状图 — purple bars, 6 months */
const basicBarOption = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', top: '10%', bottom: '5%', containLabel: true },
  xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
  yAxis: { type: 'value' },
  series: [{
    type: 'bar',
    data: [120, 200, 150, 80, 70, 110],
    itemStyle: { color: PRIMARY, borderRadius: [4, 4, 0, 0] },
    barWidth: '50%',
  }],
}

/* 2. Grouped Bar — 3 groups x 5 categories */
const groupedBarOption = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['2023', '2024', '2025'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: ['电子产品', '服装', '食品', '图书', '玩具'] },
  yAxis: { type: 'value' },
  series: [
    { name: '2023', type: 'bar', data: [320, 332, 301, 334, 390], itemStyle: { color: PRIMARY, borderRadius: [4, 4, 0, 0] } },
    { name: '2024', type: 'bar', data: [220, 182, 191, 234, 290], itemStyle: { color: SECONDARY, borderRadius: [4, 4, 0, 0] } },
    { name: '2025', type: 'bar', data: [150, 232, 201, 154, 190], itemStyle: { color: SUCCESS, borderRadius: [4, 4, 0, 0] } },
  ],
}

/* 3. Stacked Bar — 3 series stacked */
const stackedBarOption = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['直接', '邮件', '联盟'], bottom: 0 },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '15%', containLabel: true },
  xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', 'Jul'] },
  yAxis: { type: 'value' },
  series: [
    { name: '直接', type: 'bar', stack: 'total', data: [320, 332, 301, 334, 390, 330, 320], itemStyle: { color: PRIMARY } },
    { name: '邮件', type: 'bar', stack: 'total', data: [120, 132, 101, 134, 90, 230, 210], itemStyle: { color: SECONDARY } },
    { name: '联盟', type: 'bar', stack: 'total', data: [220, 182, 191, 234, 290, 330, 310], itemStyle: { color: SUCCESS } },
  ],
}

/* 4. Horizontal Bar — 8 categories */
const horizontalBarOption = {
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', top: '5%', bottom: '3%', containLabel: true },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日', '额外'], axisLabel: { width: 60 } },
  series: [{
    type: 'bar',
    data: [120, 200, 150, 80, 70, 110, 130, 90],
    itemStyle: { color: PRIMARY, borderRadius: [0, 4, 4, 0] },
    barWidth: '60%',
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
