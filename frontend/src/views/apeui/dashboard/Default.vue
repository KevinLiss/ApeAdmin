<template>
  <div class="dashboard-default">
    <PageHeader title="默认看板" :breadcrumb="['APEUI库', '数据看板', '默认看板']" />

    <div class="dash-container">
      <!-- Row 1: Profile Greeting (10/24) + 年度概览 (8/24) + Activity Review (6/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- Profile Greeting -->
        <el-col :xs="24" :sm="12" :lg="10">
          <div class="ape-card profile-greeting">
            <div class="greeting-body">
              <div class="greeting-text">
                <h1>欢迎回来，威廉</h1>
                <p>本周进度已完成 40%！设定新目标，持续提升成绩</p>
                <a class="greeting-btn" href="javascript:void(0)">
                  继续
                  <el-icon><ArrowRight /></el-icon>
                </a>
              </div>
              <div class="greeting-img">
                <img src="/assets/images/dashboard/profile-greeting/bg.png" alt="" />
              </div>
            </div>
          </div>
        </el-col>

        <!-- 年度概览 -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="ape-card yearly-view">
            <div class="card-header">
              <h3>年度概览 <span class="ape-badge-soft">50/100</span></h3>
              <h5 class="weekday-label">本周</h5>
            </div>
            <div class="card-body p-0">
              <v-chart class="yearly-chart" :option="yearlyChartOption" autoresize />
            </div>
          </div>
        </el-col>

        <!-- Activity Review -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="ape-card activity-review">
            <div class="card-header">
              <h3>活动</h3>
            </div>
            <div class="card-body">
              <div class="activity-list">
                <div class="activity-item" v-for="act in activities" :key="act.id">
                  <img :src="act.avatar" alt="" class="activity-avatar" />
                  <div class="activity-info">
                    <h5>{{ act.title }}</h5>
                    <p>{{ act.subtitle }}</p>
                  </div>
                  <div class="time-badge">
                    <p>{{ act.time }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 2: Transaction (10/24) + Value Chart sub-cards (6/24) + 超越边界 (8/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- Transaction History -->
        <el-col :xs="24" :lg="10">
          <div class="ape-card transaction-history">
            <div class="card-header">
              <h3>交易</h3>
            </div>
            <div class="transaction-body">
              <table class="transaction-table">
                <thead>
                  <tr>
                    <th>项目名称</th>
                    <th>日期时间</th>
                    <th>收入</th>
                    <th>进度</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="tx in transactions" :key="tx.id">
                    <td>
                      <div class="tx-item">
                        <div class="tx-icon">
                          <img :src="tx.icon" alt="" />
                        </div>
                        <div>
                          <h5>{{ tx.name }}</h5>
                          <p>{{ tx.delivery }}</p>
                        </div>
                      </div>
                    </td>
                    <td>
                      <h5>{{ tx.date }}</h5>
                      <p>{{ tx.days }}</p>
                    </td>
                    <td>
                      <h5 :class="{ 'income-positive': tx.income > 0, 'income-negative': tx.income < 0 }">
                        {{ tx.income > 0 ? '+' : '' }}${{ Math.abs(tx.income) }}
                      </h5>
                    </td>
                    <td>
                      <div class="progress-showcase">
                        <p>{{ tx.progress }}%</p>
                        <div class="progress-track" :class="tx.progressClass">
                          <div class="progress-fill" :style="{ width: tx.progress + '%' }"></div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <h5>{{ tx.payment }}</h5>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-col>

        <!-- Value Chart: 2 sub-cards stacked -->
        <el-col :xs="24" :lg="6">
          <div class="value-chart-sub1 ape-card">
            <div class="value-chart-body">
              <div class="round-progress-section">
                <v-chart class="knob-chart" :option="knobChartOption" autoresize />
              </div>
              <div class="valuechart-detail">
                <p>销售总额</p>
                <h2>$7454.25</h2>
              </div>
            </div>
            <span class="value-badge">新增</span>
          </div>
          <div class="value-chart-sub2 ape-card">
            <div class="value-chart-body">
              <div class="stock-chart-section">
                <v-chart class="stock-chart" :option="stockChartOption" autoresize />
              </div>
              <div class="valuechart-detail">
                <p>今日销售</p>
                <h2>$5263.04</h2>
              </div>
            </div>
            <span class="value-badge">热门</span>
          </div>
        </el-col>

        <!-- 超越边界 -->
        <el-col :xs="24" :lg="8">
          <div class="beyo-line">
            <div class="beyo-header">
              <v-chart class="beyo-chart" :option="beyoChartOption" autoresize />
            </div>
            <div class="beyo-detail">
              <h3>系统运营概览 <span class="ape-badge-soft">6 小时前</span></h3>
              <p>本周系统稳定运行 99.9%，累计处理请求 128 万次，异常率低于 0.1%。</p>
              <div class="date-history">
                <ul class="beyo-avatars">
                  <li><img src="/assets/images/dashboard/beyo-line/1.png" alt="" /></li>
                  <li><img src="/assets/images/dashboard/beyo-line/2.png" alt="" /></li>
                  <li><img src="/assets/images/dashboard/beyo-line/3.png" alt="" /></li>
                  <li><img src="/assets/images/dashboard/beyo-line/4.png" alt="" /></li>
                  <li><h2>+ 350</h2></li>
                </ul>
                <div class="date-label">
                  <h3>21</h3>
                  <p>八月</p>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 3: Investment Chart 3-col (10/24) + 热门社交媒体 (6/24) + Upgrade History (8/24) -->
      <el-row :gutter="30" class="dash-row">
        <!-- Investment Chart -->
        <el-col :xs="24" :lg="10">
          <div class="ape-card investment-chart">
            <div class="card-body">
              <el-row :gutter="20">
                <el-col :sm="8">
                  <div class="investment-group">
                    <span class="invest-label">+13.6%</span>
                    <v-chart class="invest-chart-sm" :option="investChartOption" autoresize />
                    <div class="chart-detail">
                      <h5>总投资</h5>
                      <h2>$7,454.25</h2>
                    </div>
                  </div>
                </el-col>
                <el-col :sm="8">
                  <div class="investment-group">
                    <span class="invest-label">+15.4%</span>
                    <v-chart class="invest-chart-sm" :option="gainChartOption" autoresize />
                    <div class="chart-detail">
                      <h5>总收益</h5>
                      <h2>$5,328.10</h2>
                    </div>
                  </div>
                </el-col>
                <el-col :sm="8">
                  <div class="investment-group">
                    <span class="invest-label">+11.2%</span>
                    <v-chart class="invest-chart-sm" :option="profitChartOption" autoresize />
                    <div class="chart-detail">
                      <h5>6 个月利润</h5>
                      <h2>$3,186.47</h2>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-col>

        <!-- 热门社交媒体 -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="ape-card social-shared">
            <div class="card-header">
              <h3>热门社交媒体</h3>
            </div>
            <div class="card-body">
              <div class="social-list">
                <div class="social-item" v-for="social in socialMedia" :key="social.name">
                  <div class="social-icon">
                    <img :src="social.icon" alt="" />
                  </div>
                  <div class="social-info">
                    <h5>{{ social.name }}</h5>
                    <p>社交媒体</p>
                  </div>
                  <div class="social-trend">
                    <el-icon class="trend-up-icon"><CaretTop /></el-icon>
                    <h5>{{ social.trend }}</h5>
                  </div>
                  <div class="social-value">
                    <h5>{{ social.value }}</h5>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- Upgrade History -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="ape-card upgrade-history">
            <div class="upgrade-body">
              <div class="upgrade-text">
                <h3>立即购买更多空间！</h3>
                <p>邀请 2 位好友，即可获得 5 GB 额外空间。</p>
                <a class="upgrade-btn" href="javascript:void(0)">立即升级</a>
              </div>
            </div>
            <div class="upgrade-img">
              <img src="/assets/images/dashboard/upgrade/1.png" alt="" />
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { ArrowRight, CaretTop } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, GaugeChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, GaugeChart, GridComponent, TooltipComponent, LegendComponent])

/* ApeAdmin color constants */
const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'
const SUCCESS = '#67C100'

/* ---- Activity Review data ---- */
const activities = [
  { id: 1, avatar: '/assets/images/dashboard/activity/1.jpg', title: 'Jim Smith 的审核请求', subtitle: '2026年8月21日 09:15 于广州', time: '14分钟前' },
  { id: 2, avatar: '/assets/images/dashboard/activity/2.jpg', title: '新增联系人', subtitle: '2026年8月20日 16:30 于深圳', time: '2小时前' },
  { id: 3, avatar: '/assets/images/dashboard/activity/3.jpg', title: '已发送审核 (020)888-3002', subtitle: '2026年8月20日 14:05 于上海', time: '5小时前' },
]

/* ---- Transaction History data ----
 * 收入统一为正值（绿色 + 号），币种统一 $
 * 进度条颜色按进度高低着色：<60% 红、60-79% 橙、80-89% 青、≥90% 绿
 */
const transactions = [
  { id: 1, icon: '/assets/images/dashboard/transaction/1.png', name: '耐克运动鞋 NK', delivery: '免运费', date: '2026年8月18日', days: '6天内', income: 456, progress: 65, progressClass: 'progress-warning', payment: 'PayPal' },
  { id: 2, icon: '/assets/images/dashboard/transaction/2.png', name: '女士手提包', delivery: '运费$83.65', date: '2026年8月15日', days: '5天内', income: 1280, progress: 45, progressClass: 'progress-danger', payment: '信用卡' },
  { id: 3, icon: '/assets/images/dashboard/transaction/3.png', name: '太阳镜', delivery: '免运费', date: '2026年8月10日', days: '4个月内', income: 4232, progress: 85, progressClass: 'progress-info', payment: 'PayPal' },
  { id: 4, icon: '/assets/images/dashboard/transaction/4.png', name: '棉质T恤', delivery: '运费$283.65', date: '2026年8月5日', days: '8天内', income: 645, progress: 75, progressClass: 'progress-warning', payment: '信用卡' },
]

/* ---- 社交媒体 data ---- */
const socialMedia = [
  { name: 'Facebook', icon: '/assets/images/dashboard/social-media/fb.png', trend: '3.7%', value: '$24,000' },
  { name: 'Instagram', icon: '/assets/images/dashboard/social-media/insta.png', trend: '3.7%', value: '$33,000' },
  { name: 'Twitter', icon: '/assets/images/dashboard/social-media/twit.png', trend: '7.6%', value: '$72,000' },
]

/* ===== ECharts Options ===== */

/* 1. 年度概览 — Area chart with gradient */
const yearlyChartOption = {
  series: [{
    type: 'line',
    data: [20, 20, 50, 90, 70, 80, 30, 45, 35, 95, 70, 45, 90],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 5, color: PRIMARY },
    areaStyle: {
      color: {
        type: 'linear' as const,
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(90, 103, 245, 0.5)' },
          { offset: 1, color: 'rgba(90, 103, 245, 0.9)' },
        ],
      },
    },
  }],
  grid: { left: 0, right: 0, top: 10, bottom: 0 },
  xAxis: { show: false, type: 'category' },
  yAxis: { show: false },
  tooltip: {
    trigger: 'axis',
    backgroundColor: PRIMARY,
    borderColor: 'transparent',
    textStyle: { color: '#fff' },
    axisPointer: { type: 'line', lineStyle: { color: PRIMARY, type: 'dashed' } },
  },
}

/* 2. Knob (Sale Value) — Gauge chart */
const knobChartOption = {
  series: [{
    type: 'gauge',
    startAngle: 90,
    endAngle: -270,
    radius: '90%',
    progress: {
      show: true,
      overlap: false,
      roundCap: true,
      clip: false,
      itemStyle: { color: PRIMARY },
    },
    axisLine: { lineStyle: { width: 10, color: [[62 / 100, PRIMARY], [1, '#C4C4C4']] } },
    splitLine: { show: false },
    axisTick: { show: false },
    axisLabel: { show: false },
    pointer: { show: false },
    data: [{ value: 62 }],
    detail: {
      valueAnimation: true,
      fontSize: 20,
      color: PRIMARY,
      offsetCenter: ['0%', '0%'],
      formatter: '{value}%',
    },
  }],
}

/* 3. Stock Value — Stacked bar 100% */
const stockChartOption = {
  series: [
    {
      type: 'bar',
      stack: 'total',
      data: [20, 30, 40, 80, 50],
      barWidth: 18,
      itemStyle: { borderRadius: 0, color: SECONDARY },
    },
    {
      type: 'bar',
      stack: 'total',
      data: [80, 70, 60, 20, 50],
      barWidth: 18,
      itemStyle: { borderRadius: 6, color: '#EADAD3' },
    },
  ],
  grid: { left: 0, right: 0, top: 5, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { show: false },
}

/* 4. 系统运营概览 — Bar chart 3 series */
const beyoChartOption = {
  series: [
    { name: '净利润', type: 'bar', data: [30, 70, 40, 50, 70, 50, 90], barWidth: 18, itemStyle: { borderRadius: 6, color: '#B7B1D7' } },
    { name: 'Revenue', type: 'bar', data: [60, 40, 30, 60, 80, 70, 75], barWidth: 18, itemStyle: { borderRadius: 6, color: '#B7B1D7' } },
    { name: 'Free Cash Flow', type: 'bar', data: [40, 60, 35, 90, 60, 60, 60], barWidth: 18, itemStyle: { borderRadius: 6, color: '#FFFFFF' } },
  ],
  grid: { left: 0, right: 0, top: 10, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
}

/* 5. Investment Chart — Smooth line, no grid */
const investChartOption = {
  series: [{
    type: 'line',
    data: [5, 20, 5, 50, 25, 50, 20, 60],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: PRIMARY },
  }],
  grid: { left: 0, right: 0, top: 5, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { trigger: 'axis' },
}

/* 6. Gain Chart — Smooth line, secondary color */
const gainChartOption = {
  series: [{
    type: 'line',
    data: [20, 10, 20, 10, 20, 15, 25],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: SECONDARY },
  }],
  grid: { left: 0, right: 0, top: 5, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { trigger: 'axis' },
}

/* 7. Profit Chart — Smooth line, success color */
const profitChartOption = {
  series: [{
    type: 'line',
    data: [20, 15, 20, 15, 18, 14, 20, 15],
    smooth: true,
    symbol: 'none',
    lineStyle: { width: 3, color: SUCCESS },
  }],
  grid: { left: 0, right: 0, top: 5, bottom: 0 },
  xAxis: { type: 'category', show: false },
  yAxis: { show: false },
  tooltip: { trigger: 'axis' },
}
</script>

<style scoped>
.dashboard-default {
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

/* ==================== Profile Greeting ==================== */
.profile-greeting {
  background: linear-gradient(135deg, #5A67F5 0%, #47D8FF 100%);
  height: 254px;
  position: relative;
  /* ApeAdmin 原版：插画从卡片顶部自然探出，不做裁切 */
  overflow: visible;
}
.profile-greeting .greeting-body {
  padding: 25px;
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
}
.profile-greeting .greeting-text {
  position: relative;
  z-index: 2;
}
.profile-greeting .greeting-text h1 {
  color: #fff;
  font-size: 30px;
  font-weight: 600;
  margin: 0 0 10px;
}
.profile-greeting .greeting-text p {
  color: #fff;
  font-size: 16px;
  width: 60%;
  margin: 0 0 20px;
  line-height: 1.5;
}
.greeting-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background-color: #fff;
  color: #5A67F5;
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}
.greeting-btn:hover {
  background-color: transparent;
  border: 1px solid #fff;
  color: #fff;
}
.greeting-btn .el-icon {
  font-size: 18px;
}
.greeting-img {
  position: absolute;
  bottom: -2px;
  right: 0;
}
.greeting-img img {
  /* ApeAdmin 1:1：探出卡片顶部约 9px */
  height: 261px;
}

/* ==================== 年度概览 ==================== */
.yearly-view .card-header {
  padding: 25px 25px 0;
}
.yearly-view .card-header h3 {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 5px;
}
.yearly-view .card-header h3 .ape-badge-soft {
  float: right;
}
.weekday-label {
  color: #9993B4;
  font-size: 14px;
  margin: 0;
}
.yearly-view .card-body {
  padding: 0;
  overflow: hidden;
}
.yearly-chart {
  height: 203px;
  width: 100%;
  margin-left: -15px;
  margin-right: -15px;
  margin-bottom: -35px;
}

/* ==================== Activity Review ==================== */
.activity-review .card-header {
  padding: 25px 25px 0;
}
.activity-review .card-body {
  padding: 15px 25px 25px;
}
.activity-list {
  display: flex;
  flex-direction: column;
}
.activity-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  gap: 15px;
}
.activity-item:hover {
  background-color: rgba(90, 103, 245, 0.1);
  border-radius: 8px;
  margin: 0 -10px;
  padding: 8px 10px;
}
.activity-avatar {
  width: 40px;
  height: 40px;
  border-radius: 5px;
  object-fit: cover;
  flex-shrink: 0;
}
.activity-info {
  flex: 1;
  min-width: 0;
}
.activity-info h5 {
  margin: 0 0 3px;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.activity-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
.time-badge {
  background: rgba(90, 103, 245, 0.05);
  padding: 2px 4px;
  border-radius: 5px;
  flex-shrink: 0;
}
.time-badge p {
  font-size: 10px;
  color: #5A67F5;
  margin: 0;
  white-space: nowrap;
}

/* ==================== Transaction History ==================== */
.transaction-history .card-header {
  padding: 25px 25px 0;
}
.transaction-body {
  padding: 0;
  overflow: hidden;
}
.transaction-table {
  width: 100%;
  border-collapse: collapse;
}
.transaction-table thead th {
  font-size: 16px;
  font-weight: 500;
  color: #2B2B2B;
  padding: 15px 12px 15px 25px;
  text-align: left;
  border-bottom: none;
}
.transaction-table thead th:first-child {
  padding-left: 25px;
}
.transaction-table thead th:last-child {
  padding-right: 25px;
}
.transaction-table tbody tr {
  border-top: 14px solid #EFF3F9;
  border-bottom: 14px solid #EFF3F9;
}
.transaction-table tbody tr:first-child {
  border-top: none;
}
.transaction-table tbody td {
  padding: 12px 12px;
  vertical-align: middle;
  border: none;
}
.transaction-table tbody td:first-child {
  padding-left: 25px;
  border-left: 25px solid #EFF3F9;
}
.transaction-table tbody td:last-child {
  padding-right: 25px;
  border-right: 25px solid #EFF3F9;
}
.tx-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tx-icon img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
}
.tx-item h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.tx-item p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #909399;
}
.transaction-table h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}
.income-positive {
  color: #67C100 !important;
}
.income-negative {
  color: #DC0808 !important;
}
.progress-showcase {
  text-align: right;
}
.progress-showcase p {
  margin: 0 0 4px;
  font-size: 12px;
  color: #909399;
}
.progress-track {
  height: 5px;
  background: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 3px;
}
.progress-success .progress-fill { background: #67C100; }
.progress-warning .progress-fill { background: #E56809; }
.progress-danger .progress-fill { background: #DC0808; }
.progress-info .progress-fill { background: #3EBCB9; }

/* ==================== Value Chart Sub-cards ==================== */
.value-chart-sub1 {
  background-color: rgba(90, 103, 245, 0.12) !important;
  position: relative;
  margin-bottom: 30px;
}
.value-chart-sub2 {
  background-color: rgba(255, 164, 122, 0.15) !important;
  position: relative;
  margin-bottom: 30px;
}
.value-chart-body {
  display: flex;
  align-items: center;
  padding: 25px;
  gap: 10px;
}
.round-progress-section {
  flex: 0 0 50%;
}
.knob-chart {
  width: 100%;
  height: 120px;
}
.valuechart-detail {
  flex: 0 0 50%;
}
.valuechart-detail p {
  color: #9993B4;
  font-size: 16px;
  margin: 0 0 5px;
}
.valuechart-detail h2 {
  color: #5A67F5;
  font-size: 22px;
  margin: 0;
}
.value-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 9px;
  padding: 5px 10px;
  border-radius: 9px;
  background-color: #5A67F5;
  color: #fff;
}
.stock-chart-section {
  flex: 0 0 50%;
}
.stock-chart {
  width: 100%;
  height: 120px;
}

/* ==================== 超越边界 ==================== */
.beyo-line {
  background-color: #fff;
  border-radius: 20px;
  margin-bottom: 30px;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(8, 21, 66, 0.05);
}
.beyo-header {
  background-color: #5A67F5;
  padding: 0 15px;
  overflow: hidden;
}
.beyo-chart {
  width: 100%;
  height: 270px;
  margin-bottom: -32px;
  margin-top: -18px;
}
.beyo-detail {
  padding: 29px 20px;
}
.beyo-detail h3 {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 10px;
}
.beyo-detail > p {
  font-size: 14px;
  width: 60%;
  margin: 0 0 20px;
  color: #2B2B2B;
  line-height: 1.5;
}
.date-history {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.beyo-avatars {
  display: flex;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  gap: 10px;
}
.beyo-avatars li img {
  width: 34px;
  height: 34px;
  border-radius: 50%;
}
.beyo-avatars li h2 {
  margin: 0;
  padding-left: 5px;
  font-size: 22px;
  color: #5A67F5;
}
.date-label {
  text-align: center;
  background: #fff;
  padding: 10px;
  border-radius: 10px;
  line-height: 1;
  box-shadow: 0 0 10px rgba(8, 21, 66, 0.05);
}
.date-label h3 {
  margin: 0 0 2px;
  font-weight: 700;
  font-size: 20px;
  color: #5A67F5;
}
.date-label p {
  margin: 0;
  font-size: 12px;
  color: #909399;
  text-transform: capitalize;
}

/* ==================== Investment Chart ==================== */
.investment-chart .card-body {
  padding: 25px;
}
.investment-group {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.invest-label {
  text-align: center;
  font-weight: 500;
  font-size: 18px;
  color: #5A67F5;
  margin-bottom: 5px;
}
.invest-chart-sm {
  width: 100%;
  height: 108px;
}
.chart-detail {
  text-align: center;
  margin-top: 5px;
}
.chart-detail h5 {
  color: #9993B4;
  font-size: 14px;
  font-weight: 400;
  margin: 0 0 5px;
}
.chart-detail h2 {
  font-size: 22px;
  color: #5A67F5;
  margin: 0;
}

/* ==================== 热门社交媒体 ==================== */
.social-shared .card-header {
  padding: 25px 25px 0;
}
.social-shared .card-body {
  padding: 15px 25px 25px;
}
.social-list {
  display: flex;
  flex-direction: column;
}
.social-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  gap: 12px;
}
.social-item:hover {
  background-color: rgba(90, 103, 245, 0.14);
  border-radius: 8px;
  margin: 0 -10px;
  padding: 8px 10px;
}
.social-icon img {
  width: 34px;
  height: 34px;
  border-radius: 50%;
}
.social-info {
  flex: 1;
  min-width: 0;
}
.social-info h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.social-info p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #909399;
}
.social-trend {
  display: flex;
  align-items: center;
  gap: 5px;
}
.trend-up-icon {
  color: #67C100;
  font-size: 12px;
}
.social-trend h5 {
  margin: 0;
  font-size: 14px;
  color: #2B2B2B;
}
.social-value h5 {
  margin: 0;
  font-size: 14px;
  color: #2B2B2B;
  white-space: nowrap;
}

/* ==================== Upgrade History ==================== */
.upgrade-history {
  position: relative;
  height: 250px;
  /* ApeAdmin 原版：插画从顶部探出，不被裁切 */
  overflow: visible;
}
.upgrade-body {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 25px;
  position: relative;
  z-index: 2;
}
.upgrade-text h3 {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 10px;
}
.upgrade-text p {
  width: 65%;
  font-size: 14px;
  color: #2B2B2B;
  margin: 0 0 20px;
  line-height: 1.5;
}
.upgrade-btn {
  display: inline-block;
  background-color: #5A67F5;
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}
.upgrade-btn:hover {
  background-color: #fff !important;
  border: 1px solid #5A67F5;
  color: #5A67F5;
}
.upgrade-img {
  position: absolute;
  top: -10px;
  right: -20px;
  z-index: 1;
}
.upgrade-img img {
  /* ApeAdmin 1:1：高度补齐至卡片底部贴齐（250 - 10 + 20 = 260） */
  height: 260px;
}

/* Responsive */
@media (max-width: 1400px) {
  .yearly-chart { height: 210px; }
}
@media (max-width: 992px) {
  .yearly-chart { height: 200px; }
  .profile-greeting .greeting-text p { width: 100%; }
  .beyo-detail > p { width: 100%; }
}
@media (max-width: 768px) {
  .greeting-img { display: none; }
}
</style>
