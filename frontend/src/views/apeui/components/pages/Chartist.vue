<template>
  <div>
    <PageHeader title="Chartist" :breadcrumb="['APEUI库', 'Components', 'Chartist']" />

    <el-row :gutter="30">
      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Radar Chart</span>
          </template>
          <v-chart class="chart" :option="radarOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Funnel Chart</span>
          </template>
          <v-chart class="chart" :option="funnelOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Polar Bar</span>
          </template>
          <v-chart class="chart" :option="polarBarOption" autoresize />
        </el-card>
      </el-col>

      <el-col :span="12" style="margin-bottom: 16px">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Sunburst</span>
          </template>
          <v-chart class="chart" :option="sunburstOption" autoresize />
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
import { RadarChart, BarChart, SunburstChart, FunnelChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, RadarComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, RadarChart, BarChart, SunburstChart, FunnelChart, GridComponent, TooltipComponent, RadarComponent, LegendComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'
const INFO = '#3EBCB9'
const WARNING = '#E56809'
const DANGER = '#DC0808'

/* 1. Radar Chart — 6 dimensions, 2 series */
const radarOption = {
  tooltip: { trigger: 'item' },
  legend: { data: ['Actual', 'Target'], bottom: 0 },
  radar: {
    indicator: [
      { name: 'Sales', max: 100 },
      { name: 'Marketing', max: 100 },
      { name: 'Support', max: 100 },
      { name: 'Development', max: 100 },
      { name: 'Administration', max: 100 },
      { name: 'R&D', max: 100 },
    ],
    splitArea: {
      areaStyle: {
        color: ['rgba(90, 103, 245, 0.05)', 'rgba(90, 103, 245, 0.1)'],
      },
    },
  },
  series: [{
    type: 'radar',
    data: [
      {
        value: [75, 85, 65, 90, 70, 80],
        name: 'Actual',
        lineStyle: { color: PRIMARY },
        itemStyle: { color: PRIMARY },
        areaStyle: { color: 'rgba(90, 103, 245, 0.3)' },
      },
      {
        value: [90, 90, 80, 95, 85, 90],
        name: 'Target',
        lineStyle: { color: SECONDARY },
        itemStyle: { color: SECONDARY },
        areaStyle: { color: 'rgba(255, 164, 122, 0.3)' },
      },
    ],
  }],
}

/* 2. Funnel Chart — 5 layers */
const funnelOption = {
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { bottom: 0, left: 'center' },
  series: [{
    type: 'funnel',
    top: '5%',
    bottom: '15%',
    left: '10%',
    right: '10%',
    minSize: '30%',
    gap: 4,
    label: { show: true, position: 'inside' },
    itemStyle: { borderWidth: 0 },
    data: [
      { value: 100, name: 'Visits', itemStyle: { color: PRIMARY } },
      { value: 80, name: 'Sign-ups', itemStyle: { color: INFO } },
      { value: 60, name: 'Trials', itemStyle: { color: SUCCESS } },
      { value: 40, name: 'Purchases', itemStyle: { color: SECONDARY } },
      { value: 20, name: 'Subscriptions', itemStyle: { color: WARNING } },
    ],
  }],
}

/* 3. Polar Bar — polar coordinate bar */
const polarBarOption = {
  tooltip: { trigger: 'item' },
  polar: { radius: '75%' },
  angleAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], startAngle: 90 },
  radiusAxis: { type: 'value', axisLine: { lineStyle: { color: '#ccc' } } },
  series: [{
    type: 'bar',
    coordinateSystem: 'polar',
    data: [120, 200, 150, 80, 70, 110, 130],
    itemStyle: { color: PRIMARY, borderRadius: 3 },
  }],
}

/* 4. Sunburst — hierarchical data */
const sunburstOption = {
  tooltip: { trigger: 'item' },
  series: [{
    type: 'sunburst',
    radius: ['15%', '90%'],
    center: ['50%', '50%'],
    itemStyle: { borderColor: '#fff', borderWidth: 2 },
    label: { show: true, fontSize: 11 },
    data: [
      {
        name: 'Products',
        itemStyle: { color: PRIMARY },
        children: [
          { name: 'Electronics', value: 30, itemStyle: { color: '#7B6BA5' } },
          { name: 'Clothing', value: 20, itemStyle: { color: '#9B8BBE' } },
        ],
      },
      {
        name: 'Services',
        itemStyle: { color: SECONDARY },
        children: [
          { name: 'Consulting', value: 15, itemStyle: { color: '#FFBE9E' } },
          { name: 'Support', value: 10, itemStyle: { color: '#FFD4BD' } },
        ],
      },
      {
        name: 'Others',
        itemStyle: { color: SUCCESS },
        children: [
          { name: 'Books', value: 12, itemStyle: { color: '#8FD94E' } },
          { name: 'Toys', value: 8, itemStyle: { color: '#A6E270' } },
          {
            name: 'More',
            itemStyle: { color: INFO },
            children: [
              { name: 'Food', value: 5, itemStyle: { color: '#6DD4D2' } },
              { name: 'Sports', value: 4, itemStyle: { color: '#95E0DE' } },
            ],
          },
        ],
      },
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
