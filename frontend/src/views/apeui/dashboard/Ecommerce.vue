<template>
  <div class="dashboard-ecommerce">
    <PageHeader title="Ecommerce Dashboard" :breadcrumb="['APEUI库', 'Dashboard', 'Ecommerce']" />

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

      <!-- Row 2: Recent Orders (5/12) + Top Products (4/12) + Sales By Countries (3/12) -->
      <el-row :gutter="30" class="ecom-row">
        <!-- Recent Orders Chart -->
        <el-col :xs="24" :sm="12" :lg="10">
          <div class="koho-card recent-order">
            <div class="card-header">
              <h3>Recent Orders</h3>
            </div>
            <div class="card-body pb-0">
              <v-chart class="recent-chart" :option="recentChartOption" autoresize />
            </div>
          </div>
        </el-col>

        <!-- Top Products Table -->
        <el-col :xs="24" :sm="12" :lg="8">
          <div class="koho-card top-products">
            <div class="card-header">
              <h3>Top Products</h3>
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
                    <h5>Coupon Code</h5>
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

        <!-- Sales By Countries — Radar Chart -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="koho-card country-sales-view">
            <div class="card-header">
              <h3>Sales By Countries</h3>
            </div>
            <div class="card-body p-0">
              <v-chart class="country-chart" :option="countryChartOption" autoresize />
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Row 3: Best Sellers (5/12) + Product Slider+Review (4/12) + Weekend Offer (3/12) -->
      <el-row :gutter="30" class="ecom-row">
        <!-- Best Sellers Table -->
        <el-col :xs="24" :sm="12" :lg="10">
          <div class="koho-card best-sellers">
            <div class="card-header">
              <h3>Best Sellers</h3>
            </div>
            <div class="card-body">
              <table class="best-sellers-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Date</th>
                    <th>Product</th>
                    <th>Total</th>
                    <th>Status</th>
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
                  <img src="/koho/assets/images/dashboard-2/person1.png" alt="" />
                </div>
                <div class="review-info">
                  <h4>Johanna Parvez</h4>
                  <div class="rating-stars">
                    <el-icon v-for="n in 5" :key="n" color="#FFA47A" size="14"><Star /></el-icon>
                  </div>
                </div>
              </div>
              <div class="review-text">
                <p>I love this good looking shoes, but comfort is where it's at for Me. I can't say how well they are for playing football, but for everyday wear they are amazing. I think they're more comfortable than My lebron 17s.</p>
              </div>
            </div>
          </div>
        </el-col>

        <!-- Weekend Offer -->
        <el-col :xs="24" :sm="12" :lg="6">
          <div class="koho-card weekend-view">
            <div class="weekend-body">
              <div class="weekend-inner-bg"></div>
              <div class="weekend-img">
                <img src="/koho/assets/images/dashboard-2/headphone.png" alt="" />
              </div>
              <div class="weekend-detail">
                <h3>Special Weekend Offer</h3>
                <h5>Upto 50% Off Discount</h5>
                <a class="weekend-btn" href="javascript:void(0)">See More</a>
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
  { title: 'Total Sales', value: '54,750', icon: markRaw(ShoppingBag), iconBg: '#5A67F5', chartOption: makeStatChartOption(PRIMARY, '#dad8e0') },
  { title: 'Total Income', value: '$35,532', icon: markRaw(Money), iconBg: '#FFA47A', chartOption: makeStatChartOption(SECONDARY, '#faded1') },
  { title: 'Orders Paid', value: '55,900', icon: markRaw(Document), iconBg: '#5A67F5', chartOption: makeStatChartOption(PRIMARY, '#dad8e0') },
  { title: 'Total Visitor', value: '67,900', icon: markRaw(User), iconBg: '#FFA47A', chartOption: makeStatChartOption(SECONDARY, '#faded1') },
]

/* ---- Top Products ---- */
const topProducts = [
  { icon: '/koho/assets/images/dashboard-2/chair.png', name: 'Wood Chair Dark', items: 100, code: 'PIX001', flag: '🇬🇧', discount: '-51%', price: '$99.00' },
  { icon: '/koho/assets/images/dashboard-2/shoes.png', name: 'Sneaker For Men', items: 150, code: 'PIX002', flag: '🇺🇸', discount: '-78%', price: '$66.00' },
  { icon: '/koho/assets/images/dashboard-2/pot.png', name: 'Tree Stylish Pot', items: 105, code: 'PIX003', flag: '🇿🇦', discount: '-04%', price: '$116.00' },
  { icon: '/koho/assets/images/dashboard-2/purse.png', name: 'Ulrich Duffel Bag', items: 600, code: 'PIX004', flag: '🇦🇹', discount: '-60%', price: '$99.00' },
  { icon: '/koho/assets/images/dashboard-2/watch.png', name: 'Mi Watch Revolve', items: 541, code: 'PIX005', flag: '🇧🇷', discount: '-50%', price: '$58.00' },
]

/* ---- Best Sellers ---- */
const bestSellers = [
  { id: 1, avatar: '/koho/assets/images/dashboard-2/person1.png', name: 'John Keter', year: '2019', date: '06 August', product: 'Brande Shoes', total: '$37,618', progress: 65, progressClass: 'progress-success' },
  { id: 2, avatar: '/koho/assets/images/dashboard-2/person2.png', name: 'Harry Venter', year: '2020', date: '21 March', product: 'Headphone', total: '$59,105', progress: 45, progressClass: 'progress-warning' },
  { id: 3, avatar: '/koho/assets/images/dashboard-2/person3.png', name: 'Loadin Deo', year: '2020', date: '09 March', product: 'Cell Phone', total: '$10,155', progress: 85, progressClass: 'progress-danger' },
  { id: 4, avatar: '/koho/assets/images/dashboard-2/person4.png', name: 'Horen Hors', year: '2020', date: '14 February', product: 'Fashion', total: '$90,568', progress: 75, progressClass: 'progress-info' },
  { id: 5, avatar: '/koho/assets/images/dashboard-2/person5.png', name: 'Fenter Jessy', year: '2020', date: '21 January', product: 'Bookshop', total: '$10,652', progress: 45, progressClass: 'progress-warning' },
]

/* ---- Product Cards ---- */
const productCards = [
  { id: 1, img: '/koho/assets/images/dashboard-2/wellington-shoes.png', name: 'Wellington Shoes', price: '$325.25', badge: 'New', bgClass: 'bg-secondary-card' },
  { id: 2, img: '/koho/assets/images/dashboard-2/apple-watch.png', name: 'Apple Smartwatch', price: '$1185.99', badge: 'Hot', bgClass: 'bg-primary-card' },
]

/* ===== ECharts ===== */

/* Recent Orders — Area + Line combo */
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
    data: ['Jan', 'Feb', 'Mar', 'April', 'May', 'June', 'July'],
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

/* ==================== Recent Orders ==================== */
.recent-order .card-body {
  padding: 0 25px 0;
}
.recent-chart {
  width: 100%;
  height: 355px;
}

/* ==================== Top Products ==================== */
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

/* ==================== Best Sellers ==================== */
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
  height: 120px;
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

/* ==================== Weekend Offer ==================== */
.weekend-view {
  position: relative;
  overflow: hidden;
  height: 250px;
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
.weekend-inner-bg {
  position: absolute;
  inset: 15px;
  border: 2px dashed rgba(90, 103, 245, 0.2);
  border-radius: 15px;
}
.weekend-img img {
  height: 80px;
  margin-bottom: 15px;
}
.weekend-detail h3 {
  font-size: 20px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 8px;
}
.weekend-detail h5 {
  font-size: 16px;
  color: #2B2B2B;
  font-weight: 400;
  margin: 0 0 20px;
}
.weekend-btn {
  display: inline-block;
  background-color: #5A67F5;
  color: #fff;
  padding: 10px 25px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
}
.weekend-btn:hover {
  background-color: #fff;
  border: 1px solid #5A67F5;
  color: #5A67F5;
}

@media (max-width: 992px) {
  .recent-chart { height: 280px; }
  .country-chart { height: 280px; }
}
</style>
