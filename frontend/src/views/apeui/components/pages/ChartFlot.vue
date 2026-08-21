<template>
  <div>
    <PageHeader title="Flot 图表" :breadcrumb="['APEUI库', '组件示例', 'Flot 图表']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">基础饼图</span>
          </template>
          <v-chart class="chart" :option="basicPieOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Doughnut Chart</span>
          </template>
          <v-chart class="chart" :option="doughnutOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Half Pie</span>
          </template>
          <v-chart class="chart" :option="halfPieOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Rose Chart</span>
          </template>
          <v-chart class="chart" :option="roseOption" autoresize />
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
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'
const INFO = '#3EBCB9'
const WARNING = '#E56809'

/* 1. 基础饼图 — 5 sectors */
const basicPieOption = {
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, left: 'center' },
  series: [{
    type: 'pie',
    radius: '60%',
    center: ['50%', '45%'],
    data: [
      { value: 1048, name: 'Search', itemStyle: { color: PRIMARY } },
      { value: 735, name: 'Direct', itemStyle: { color: SECONDARY } },
      { value: 580, name: 'Email', itemStyle: { color: SUCCESS } },
      { value: 484, name: 'Union', itemStyle: { color: INFO } },
      { value: 300, name: 'Video', itemStyle: { color: WARNING } },
    ],
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } },
  }],
}

/* 2. Doughnut — 4 sectors */
const doughnutOption = {
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, left: 'center' },
  series: [{
    type: 'pie',
    radius: ['40%', '65%'],
    center: ['50%', '45%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: { label: { show: true, fontSize: 18, fontWeight: 'bold' } },
    data: [
      { value: 1048, name: 'Chrome', itemStyle: { color: PRIMARY } },
      { value: 735, name: 'Firefox', itemStyle: { color: SECONDARY } },
      { value: 580, name: 'Safari', itemStyle: { color: SUCCESS } },
      { value: 484, name: 'Edge', itemStyle: { color: INFO } },
    ],
  }],
}

/* 3. Half Pie — semicircle */
const halfPieOption = {
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, left: 'center' },
  series: [{
    type: 'pie',
    radius: '70%',
    center: ['50%', '75%'],
    startAngle: 180,
    endAngle: 360,
    data: [
      { value: 25, name: 'A', itemStyle: { color: PRIMARY } },
      { value: 30, name: 'B', itemStyle: { color: SECONDARY } },
      { value: 20, name: 'C', itemStyle: { color: SUCCESS } },
      { value: 15, name: 'D', itemStyle: { color: INFO } },
      { value: 10, name: 'E', itemStyle: { color: WARNING } },
    ],
  }],
}

/* 4. Rose Chart — nightingale */
const roseOption = {
  tooltip: { trigger: 'item' },
  legend: { bottom: 0, left: 'center' },
  series: [{
    type: 'pie',
    radius: ['15%', '70%'],
    center: ['50%', '45%'],
    roseType: 'area',
    itemStyle: { borderRadius: 4 },
    data: [
      { value: 40, name: 'Mon', itemStyle: { color: PRIMARY } },
      { value: 38, name: 'Tue', itemStyle: { color: SECONDARY } },
      { value: 32, name: 'Wed', itemStyle: { color: SUCCESS } },
      { value: 30, name: 'Thu', itemStyle: { color: INFO } },
      { value: 28, name: 'Fri', itemStyle: { color: WARNING } },
      { value: 26, name: 'Sat', itemStyle: { color: '#DC0808' } },
      { value: 24, name: 'Sun', itemStyle: { color: '#8B5CF6' } },
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
