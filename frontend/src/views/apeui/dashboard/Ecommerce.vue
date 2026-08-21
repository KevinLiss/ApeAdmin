<template>
  <div class="dashboard-ecommerce">
    <PageHeader title="电商看板" :breadcrumb="['APEUI库', '数据看板', '电商看板']" />

    <div class="ecom-container">
      <!-- Row 1: 4 stat cards with mini charts -->
      <el-row :gutter="30" class="ecom-row">
        <el-col :xs="12" :sm="12" :lg="6" v-for="stat in statCards" :key="stat.title">
          <div class="koho-card sale-chart">
            <div class="sale-chart-body">
              <div class="sale-detail">
                <div class="sale-icon" :style="{ background: stat.iconBg }">
                  <el-icon :size="22" color="#fff"><component :is="stat.icon" /></el-icon>
                </div>
                <div class="sale-content">
                  <h3>{{ stat.title }}</h3>
                  <p>{{ stat.value }}</p>
                </div>
              </div>
              <div class="mini-chart-wrap">
                <v-chart class="mini-chart" :option="stat.chartOption" autoresize />
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 2: 最近订单 (5/12) + 热销商品 (4/12) + 各国销售额 (3/12) -->
      <el-row :gutter="30" class="ecom-row">
        <!-- 最近订单 Chart -->
        <el-col :xs="24" :sm="12" :lg="10">
          <div class="koho-card recent-order">
            <div class="card-header">
              <h3>最近订单</h3>
            </div>
            <div class="card-body pb-0">
              <v-chart class="recent-chart" :option="recentChartOption" autoresize />
            </div>
          </div>
        </el-col>

        <!-- 热销商品 Table -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="koho-card top-products">
            <div class="card-header">
              <h3>热销商品</h3>
            </div>
            <div class="card-body">
              <div class="top-products-list">
                <div class="tp-item" v-for="p in topProducts" :key="p.code">
                  <div class="tp-product">
                    <div class="tp-icon">
                      <img :src="p.icon" alt="" />
                    </div>
                    <div>
                      <h5>{{ p.name }}</h5>
                      <p>{{ p.items }} Items</p>
                    </div>
                  </div>
                  <div class="tp-coupon">
                    <h5>优惠码</h5>
                    <p>{{ p.code }}</p>
                  </div>
                  <div class="tp-flag">
                    <span class="flag-emoji">{{ p.flag }}</span>
                  </div>
                  <div class="tp-discount">
                    <h5>{{ p.discount }}</h5>
                    <p>{{ p.price }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 各国销售额 — Radar Chart -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="koho-card country-sales-view">
            <div class="card-header">
              <h3>各国销售额</h3>
            </div>
            <div class="card-body p-0">
              <v-chart class="country-chart" :option="countryChartOption" autoresize />
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 3: 畅销榜单 (5/12) + Product Slider+Review (4/12) + Weekend Offer (3/12) -->
      <el-row :gutter="30" class="ecom-row">
        <!-- 畅销榜单 Table -->
        <el-col :xs="24" :sm="12" :lg="10">
          <div class="koho-card best-sellers">
            <div class="card-header">
              <h3>畅销榜单</h3>
            </div>
            <div class="card-body">
              <table class="best-sellers-table">
                <thead>
                  <tr>
                    <th>名称</th>
                    <th>日期</th>
                    <th>商品</th>
                    <th>合计</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="seller in bestSellers" :key="seller.id">
                    <td>
                      <div class="seller-name">
                        <div class="seller-avatar">
                          <img :src="seller.avatar" alt="" />
                        </div>
                        <div>
                          <h5>{{ seller.name }}</h5>
                          <p>{{ seller.year }}</p>
                        </div>
                      </div>
                    </td>
                    <td><h5>{{ seller.date }}</h5></td>
                    <td><h5>{{ seller.product }}</h5></td>
                    <td><h5>{{ seller.total }}</h5></td>
                    <td>
                      <div class="status-showcase">
                        <p>{{ seller.progress }}%</p>
                        <div class="progress-track" :class="seller.progressClass">
                          <div class="progress-fill" :style="{ width: seller.progress + '%' }"></div>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </el-col>

        <!-- Product Cards + Review -->
        <el-col :xs="24" :sm="12" :lg="8">
          <el-row :gutter="30">
            <el-col :sm="12" v-for="product in productCards" :key="product.id">
              <div class="koho-card rated-product" :class="product.bgClass">
                <div class="rated-product-body">
                  <div class="rated-img-wrap">
                    <img :src="product.img" alt="" />
                    <span class="rated-badge">{{ product.badge }}</span>
                  </div>
                  <div class="rated-detail">
                    <h4>{{ product.name }}</h4>
                    <h3>{{ product.price }}</h3>
                    <div class="rating-stars">
                      <el-icon v-for="n in 5" :key="n" color="#FFA47A" size="14"><Star /></el-icon>
                    </div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>

          <div class="koho-card product-review">
            <div class="review-body">
              <div class="review-header">
                <div class="review-avatar">
                  <img src="/assets/images/dashboard-2/person1.png" alt="" />
                </div>
                <div class="review-info">
                  <h4>乔安娜·帕尔韦兹</h4>
                  <div class="rating-stars">
                    <el-icon v-for="n in 5" :key="n" color="#FFA47A" size="14"><Star /></el-icon>
                  </div>
                </div>
                <span class="quote-icon">&ldquo;</span>
              </div>
              <div class="review-text">
                <p>我很喜欢这双漂亮的鞋，但舒适度才是我最看重的。虽然没法评价它们踢足球时的表现，但日常穿着简直太棒了。比我的勒布朗17代还要舒服。</p>
              </div>
            </div>
          </div>
        </el-col>

        <!-- Weekend Offer (Koho 1:1) -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="koho-card weekend-view">
            <div class="weekend-body">
              <div class="weekend-inner-bg"></div>
              <div class="weekend-img">
                <img src="/assets/images/dashboard-2/headphone.png" alt="headphone" />
              </div>
              <div class="weekend-detail">
                <h3>周末特惠</h3>
                <h5>低至5折优惠</h5>
                <a class="weekend-btn" href="javascript:void(0)">查看更多</a>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { Star } from '@element-plus/icons-vue'
import { markRaw } from 'vue'
import {
  ShoppingBag,
  Money,
  Document,
  User,
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, RadarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, RadarComponent } from 'echarts/components'

use([CanvasRenderer, BarChart, LineChart, RadarChart, GridComponent, TooltipComponent, RadarComponent])

const PRIMARY = '#5A67F5'
const SECONDARY = '#FFA47A'

/* ---- Helper: stacked bar chart option for stat cards ---- */
function makeStatChartOption(color1: string, color2: string) {
  return {
    series: [
      { type: 'bar', stack: 'total', data: [20, 60, 50, 70, 40, 80, 20], barWidth: 12, itemStyle: { borderRadius: 0, color: color1 } },
      { type: 'bar', stack: 'total', data: [80, 40, 50, 30, 60, 20, 20], barWidth: 12, itemStyle: { borderRadius: 2, color: color2 } },
    ],
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    xAxis: { type: 'category', show: false },
    yAxis: { show: false },
    tooltip: { show: false },
  }
}

/* ---- Stat Cards ---- */
const statCards = [
  { title: '总销售', value: '54,750', icon: markRaw(ShoppingBag), iconBg: '#5A67F5', chartOption: makeStatChartOption(PRIMARY, '#dad8e0') },
  { title: '总收入', value: '$35,532', icon: markRaw(Money), iconBg: '#FFA47A', chartOption: makeStatChartOption(SECONDARY, '#faded1') },
  { title: '已支付订单', value: '55,900', icon: markRaw(Document), iconBg: '#5A67F5', chartOption: makeStatChartOption(PRIMARY, '#dad8e0') },
  { title: '总访客', value: '67,900', icon: markRaw(User), iconBg: '#FFA47A', chartOption: makeStatChartOption(SECONDARY, '#faded1') },
]

/* ---- 热销商品 ---- */
const topProducts = [
  { icon: '/assets/images/dashboard-2/chair.png', name: '深色木椅', items: 100, code: 'PIX001', flag: '🇬🇧', discount: '-51%', price: '$99.00' },
  { icon: '/assets/images/dashboard-2/shoes.png', name: '男士运动鞋', items: 150, code: 'PIX002', flag: '🇺🇸', discount: '-78%', price: '$66.00' },
  { icon: '/assets/images/dashboard-2/pot.png', name: "时尚花盆", items: 105, code: 'PIX003', flag: '🇿🇦', discount: '-04%', price: '$116.00' },
  { icon: '/assets/images/dashboard-2/purse.png', name: '旅行手提袋', items: 600, code: 'PIX004', flag: '🇦🇹', discount: '-60%', price: '$99.00' },
  { icon: '/assets/images/dashboard-2/watch.png', name: '小米手表 Revolve', items: 541, code: 'PIX005', flag: '🇧🇷', discount: '-50%', price: '$58.00' },
]

/* ---- 畅销榜单 ---- */
const bestSellers = [
  { id: 1, avatar: '/assets/images/dashboard-2/person1.png', name: '约翰·凯特', year: '2019', date: '8月6日', product: '品牌鞋', total: '$37,618', progress: 65, progressClass: 'progress-success' },
  { id: 2, avatar: '/assets/images/dashboard-2/person2.png', name: '哈里·文特', year: '2020', date: '3月21日', product: '耳机', total: '$59,105', progress: 45, progressClass: 'progress-warning' },
  { id: 3, avatar: '/assets/images/dashboard-2/person3.png', name: '洛丁·迪奥', year: '2020', date: '3月9日', product: '手机', total: '$10,155', progress: 85, progressClass: 'progress-danger' },
  { id: 4, avatar: '/assets/images/dashboard-2/person4.png', name: '霍伦·霍斯', year: '2020', date: '2月14日', product: '时尚服饰', total: '$90,568', progress: 75, progressClass: 'progress-info' },
  { id: 5, avatar: '/assets/images/dashboard-2/person5.png', name: '芬特·杰西', year: '2020', date: '1月21日', product: '书店', total: '$10,652', progress: 45, progressClass: 'progress-warning' },
]

/* ---- Product Cards ---- */
const productCards = [
  { id: 1, img: '/assets/images/dashboard-2/wellington-shoes.png', name: '威灵顿鞋', price: '$325.25', badge: '新品', bgClass: 'bg-secondary-card' },
  { id: 2, img: '/assets/images/dashboard-2/apple-watch.png', name: '苹果智能手表', price: '$1185.99', badge: '热门', bgClass: 'bg-primary-card' },
]

/* ===== ECharts ===== */

/* 最近订单 — Area + Line combo */
const recentChartOption = {
  series: [
    {
      type: 'line',
      data: [150, 470, 250, 380, 100, 480, 420],
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 5, color: SECONDARY },
    },
    {
      type: 'line',
      data: [220, 160, 230, 150, 220, 130, 200],
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 0, color: PRIMARY },
      areaStyle: { color: PRIMARY, opacity: 0.2 },
    },
  ],
  grid: { left: 30, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'],
    axisLine: { show: false },
    axisTick: { show: false },
    axisLabel: { color: '#909399', fontSize: 12 },
  },
  yAxis: { show: false },
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
}

/* Country Sales — Radar */
const countryChartOption = {
  series: [{
    type: 'radar',
    data: [{ value: [20, 100, 40, 30, 50, 80, 33], areaStyle: { color: SECONDARY }, lineStyle: { color: SECONDARY, width: 2 } }],
    symbol: 'circle',
    symbolSize: 5,
    itemStyle: { color: SECONDARY },
  }],
  radar: {
    indicator: [
      { name: 'Sun', max: 100 },
      { name: 'Mon', max: 100 },
      { name: 'Tue', max: 100 },
      { name: 'Wed', max: 100 },
      { name: 'Thu', max: 100 },
      { name: 'Fri', max: 100 },
      { name: 'Sat', max: 100 },
    ],
    axisName: { color: '#909399', fontSize: 12 },
    splitArea: { show: false },
    splitLine: { lineStyle: { color: '#e9edf3' } },
    axisLine: { lineStyle: { color: '#e9edf3' } },
  },
  tooltip: { trigger: 'item' },
}
</script>

<style scoped>
.dashboard-ecommerce {
  padding: 0;
}
.ecom-container {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.ecom-row {
  margin-bottom: 0;
}

/* ==================== Sale Chart (Stat Cards) ==================== */
.sale-chart .sale-chart-body {
  display: flex;
  align-items: center;
  padding: 25px;
  gap: 10px;
}
.sale-detail {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}
.sale-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.sale-content h3 {
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 5px;
}
.sale-content p {
  font-size: 24px;
  font-weight: 600;
  color: #2B2B2B;
  margin: 0;
}
.mini-chart-wrap {
  width: 80px;
  flex-shrink: 0;
}
.mini-chart {
  width: 80px;
  height: 100px;
}

/* ==================== 最近订单 ==================== */
.recent-order .card-body {
  padding: 0 25px 0;
}
.recent-chart {
  width: 100%;
  height: 355px;
}

/* ==================== 热销商品 ==================== */
.top-products .card-body {
  padding: 15px 25px 25px;
}
.top-products-list {
  display: flex;
  flex-direction: column;
}
.tp-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  gap: 15px;
  border-bottom: 1px solid #f5f5f5;
}
.tp-item:last-child {
  border-bottom: none;
}
.tp-product {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
.tp-icon img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
}
.tp-product h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.tp-product p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #909399;
}
.tp-coupon {
  text-align: center;
}
.tp-coupon h5 {
  margin: 0;
  font-size: 13px;
  color: #909399;
}
.tp-coupon p {
  margin: 2px 0 0;
  font-size: 13px;
  font-weight: 500;
  color: #5A67F5;
}
.tp-flag {
  font-size: 22px;
}
.tp-discount h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #DC0808;
}
.tp-discount p {
  margin: 2px 0 0;
  font-size: 13px;
  color: #2B2B2B;
}

/* ==================== Country Sales ==================== */
.country-sales-view .card-body {
  padding: 0;
}
.country-chart {
  width: 100%;
  height: 335px;
}

/* ==================== 畅销榜单 ==================== */
.best-sellers .card-body {
  padding: 15px 25px 25px;
}
.best-sellers-table {
  width: 100%;
  border-collapse: collapse;
}
.best-sellers-table thead th {
  font-size: 16px;
  font-weight: 500;
  color: #2B2B2B;
  padding: 0 10px 15px 0;
  text-align: left;
  border-bottom: none;
}
.best-sellers-table tbody td {
  padding: 12px 10px 12px 0;
  vertical-align: middle;
  border-bottom: 1px solid #f5f5f5;
}
.best-sellers-table tbody tr:last-child td {
  border-bottom: none;
}
.seller-name {
  display: flex;
  align-items: center;
  gap: 12px;
}
.seller-avatar img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}
.seller-name h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.seller-name p {
  margin: 2px 0 0;
  font-size: 12px;
  color: #909399;
}
.best-sellers-table h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
}
.status-showcase {
  text-align: right;
}
.status-showcase p {
  margin: 0 0 4px;
  font-size: 12px;
  color: #909399;
}
.progress-track {
  height: 5px;
  background: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
  min-width: 60px;
}
.progress-fill {
  height: 100%;
  border-radius: 3px;
}
.progress-success .progress-fill { background: #67C100; }
.progress-warning .progress-fill { background: #E56809; }
.progress-danger .progress-fill { background: #DC0808; }
.progress-info .progress-fill { background: #3EBCB9; }

/* ==================== Rated Product Cards ==================== */
.rated-product {
  margin-bottom: 30px;
}
.bg-secondary-card {
  background-color: rgba(255, 164, 122, 0.1) !important;
}
.bg-primary-card {
  background-color: rgba(90, 103, 245, 0.1) !important;
}
.rated-product-body {
  padding: 25px;
}
.rated-img-wrap {
  position: relative;
  text-align: center;
  margin-bottom: 15px;
}
.rated-img-wrap img {
  max-height: 120px;
  width: auto;
  max-width: 100%;
  object-fit: contain;
}
.rated-badge {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 9px;
  padding: 5px 10px;
  border-radius: 9px;
  background-color: #5A67F5;
  color: #fff;
}
.rated-detail {
  text-align: center;
}
.rated-detail h4 {
  font-size: 16px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 8px;
}
.rated-detail h3 {
  font-size: 22px;
  font-weight: 600;
  color: #2B2B2B;
  margin: 0 0 10px;
}
.rating-stars {
  display: flex;
  justify-content: center;
  gap: 2px;
}

/* ==================== Product Review ==================== */
.product-review {
  margin-bottom: 30px;
}
.review-body {
  padding: 25px;
}
.review-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  position: relative;
}
.review-header .quote-icon {
  position: absolute;
  top: -5px;
  right: 0;
  font-size: 48px;
  color: rgba(90, 103, 245, 0.08);
  pointer-events: none;
}
.review-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
}
.review-info h4 {
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 5px;
}
.review-text p {
  font-size: 14px;
  color: #2B2B2B;
  line-height: 1.6;
  margin: 0;
}

/* ==================== Weekend Offer (Koho 1:1) ==================== */
.weekend-view {
  position: relative;
  overflow-x: hidden;
  /* Koho 原版：深紫底色 + offer-banner.svg 背景图 */
  background-image: url("/assets/images/dashboard-2/offer-banner.svg");
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  background-color: #5A67F5;
  height: 100%;
  min-height: 250px;
}
.weekend-body {
  padding: 25px;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
/* Koho 原版 inner-bg：bg-ribbons.png 重复纹理 + 缓慢滚动动画 */
.weekend-inner-bg {
  background: url(/assets/images/dashboard-2/bg-ribbons.png) repeat;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  animation: anime1 5s linear infinite;
  border-radius: 20px;
  pointer-events: none;
}
@keyframes anime1 {
  0% { background-position: 0 -80px; }
  100% { background-position: 0 0; }
}
.weekend-img {
  position: relative;
  z-index: 1;
  margin-bottom: 15px;
}
.weekend-img img {
  height: 80px;
  width: auto;
  object-fit: contain;
  transition: transform 0.3s;
}
/* Koho 原版 hover 弹跳动画 */
.weekend-body:hover .weekend-img img {
  animation: anime2 1s linear alternate infinite;
}
@keyframes anime2 {
  0% { transform: translateY(0); }
  100% { transform: translateY(-8px); }
}
.weekend-detail {
  position: relative;
  z-index: 1;
  display: grid;
  justify-items: center;
}
.weekend-detail h3 {
  font-size: 20px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 5px;
  text-align: center;
}
.weekend-detail h5 {
  font-size: 16px;
  color: #9993B4;
  font-weight: 400;
  margin: 0 0 15px;
}
.weekend-btn {
  display: inline-flex;
  align-items: center;
  background-color: #ffffff;
  color: #5A67F5;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  line-height: 1;
  z-index: 2;
  transition: all 0.2s;
}
.weekend-btn:hover {
  opacity: 0.85;
}

@media (max-width: 992px) {
  .recent-chart { height: 280px; }
  .country-chart { height: 280px; }
}
</style>
