<template>
  <div class="product-page-detail">
    <PageHeader title="商品详情页" :breadcrumb="['APEUI库', '电商模块', '商品详情页']" />

    <!-- Product Detail -->
    <el-row :gutter="30" class="detail-row">
      <!-- Left: Gallery -->
      <el-col :xs="24" :sm="24" :md="12" :lg="10">
        <div class="gallery-main-img" :style="{ background: mainImageBg }">
          <el-icon :size="80" color="rgba(255,255,255,0.6)"><Goods /></el-icon>
          <span class="discount-tag" :style="{ background: '#DC0808' }">-20%</span>
        </div>
        <el-row :gutter="12" class="thumbs-row">
          <el-col :span="6" v-for="(thumb, i) in thumbnails" :key="i">
            <div
              class="thumb"
              :style="{ background: thumb.bg }"
              :class="{ active: activeThumb === i }"
              @click="activeThumb = i"
            >
              <el-icon :size="24" color="rgba(255,255,255,0.7)"><Goods /></el-icon>
            </div>
          </el-col>
        </el-row>
      </el-col>

      <!-- Right: Info -->
      <el-col :xs="24" :sm="24" :md="12" :lg="14">
        <div class="product-detail-info">
          <span class="detail-category">电子产品</span>
          <h2 class="detail-title">无线蓝牙降噪耳机</h2>
          <div class="detail-rating-row">
            <el-rate v-model="rating" disabled size="large" />
            <span class="review-link">（256 条评价）</span>
          </div>
          <div class="detail-price-row">
            <span class="detail-price">$159.99</span>
            <span class="detail-old-price">$199.99</span>
            <el-tag type="danger" effect="dark" round>20% 折扣</el-tag>
          </div>
          <p class="detail-short-desc">
            Experience premium sound quality with active noise cancellation. Up to 40 hours of battery life and ultra-fast USB-C charging.
          </p>

          <!-- Color Selection -->
          <div class="option-row">
            <span class="option-label">颜色：</span>
            <div class="color-options">
              <span
                v-for="color in colors"
                :key="color.name"
                class="color-dot"
                :style="{ background: color.hex }"
                :class="{ active: selectedColor === color.name }"
                @click="selectedColor = color.name"
              >
                <el-icon v-if="selectedColor === color.name" :size="12" color="#fff"><Check /></el-icon>
              </span>
            </div>
          </div>

          <!-- Size Selection -->
          <div class="option-row">
            <span class="option-label">尺码：</span>
            <div class="size-options">
              <button
                v-for="size in sizes"
                :key="size"
                class="size-btn"
                :class="{ active: selectedSize === size }"
                @click="selectedSize = size"
              >{{ size }}</button>
            </div>
          </div>

          <!-- Quantity + Actions -->
          <div class="action-row">
            <div class="quantity-block">
              <span class="option-label">数量：</span>
              <el-input-number v-model="quantity" :min="1" :max="10" />
            </div>
            <div class="action-buttons">
              <el-button type="primary" size="large" @click="addToCart">
                <el-icon class="mr-4"><ShoppingCart /></el-icon>加入购物车
              </el-button>
              <el-button type="danger" size="large" @click="buyNow">
                <el-icon class="mr-4"><Lightning /></el-icon>立即购买
              </el-button>
              <el-button size="large" circle @click="toggleWishlist">
                <el-icon :color="wishlisted ? '#DC0808' : '#5A67F5'">
                  <StarFilled v-if="wishlisted" />
                  <Star v-else />
                </el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Tabs -->
    <el-card class="koho-card detail-tabs-card" shadow="never">
      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="Description" name="description">
          <div class="tab-content">
            <p>The 无线蓝牙降噪耳机 deliver an immersive audio experience with cutting-edge technology. Featuring advanced ANC that blocks up to 90% of ambient noise, these headphones are perfect for travel, work, or relaxation.</p>
            <ul class="feature-list">
              <li><strong>主动降噪：</strong> 一键屏蔽外界干扰</li>
              <li><strong>40 小时续航：</strong> 单次充电，全天畅听</li>
              <li><strong>USB-C 快充：</strong> 充电 10 分钟，畅听 5 小时</li>
              <li><strong>优质记忆棉：</strong> 蛋白皮革耳罩，全天佩戴舒适</li>
              <li><strong>蓝牙 5.3：</strong> 多点配对，连接稳定可靠</li>
            </ul>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Reviews" name="reviews">
          <div class="tab-content reviews-content">
            <div class="review-summary">
              <div class="rating-overview">
                <h2>4.6</h2>
                <el-rate v-model="rating" disabled size="small" />
                <p>基于 256 条用户评价</p>
              </div>
              <div class="rating-breakdown">
                <div class="rating-bar-item" v-for="bar in ratingBars" :key="bar.label">
                  <span class="bar-label">{{ bar.label }}</span>
                  <div class="bar-track"><div class="bar-fill" :style="{ width: bar.value + '%', background: '#5A67F5' }"></div></div>
                  <span class="bar-value">{{ bar.value }}%</span>
                </div>
              </div>
            </div>
            <el-divider />
            <div class="review-list">
              <div class="review-item" v-for="review in reviews" :key="review.id">
                <div class="review-avatar">{{ review.user.charAt(0) }}</div>
                <div class="review-body">
                  <div class="review-head">
                    <span class="review-user">{{ review.user }}</span>
                    <el-rate v-model="review.stars" disabled size="small" />
                  </div>
                  <p class="review-text">{{ review.text }}</p>
                  <span class="review-date">{{ review.date }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Shipping" name="shipping">
          <div class="tab-content">
            <div class="shipping-info" v-for="info in shippingInfo" :key="info.title">
              <div class="shipping-icon" :style="{ background: info.bg }">
                <el-icon :size="22" color="#fff"><component :is="info.icon" /></el-icon>
              </div>
              <div>
                <h5>{{ info.title }}</h5>
                <p>{{ info.desc }}</p>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 相关商品 -->
    <el-card class="koho-card related-card" shadow="never">
      <h3 class="section-title">相关商品</h3>
      <el-row :gutter="30">
        <el-col :xs="12" :sm="12" :md="6" v-for="rp in relatedProducts" :key="rp.id">
          <div class="related-product-card">
            <div class="related-img" :style="{ background: rp.bgColor }">
              <el-icon :size="36" color="rgba(255,255,255,0.7)"><Goods /></el-icon>
            </div>
            <div class="related-info">
              <h5>{{ rp.name }}</h5>
              <el-rate v-model="rp.rating" disabled size="small" />
              <span class="related-price">${{ rp.price.toFixed(2) }}</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue'
import { ElMessage } from 'element-plus'
import { Goods, Check, ShoppingCart, Lightning, Star, StarFilled, Van, Box, Wallet } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const mainImageBg = 'linear-gradient(135deg, #5A67F5, #8FA0FF)'
const activeThumb = ref(0)
const rating = ref(4.6)
const selectedColor = ref('Purple')
const selectedSize = ref('Standard')
const quantity = ref(1)
const wishlisted = ref(false)
const activeTab = ref('description')

const thumbnails = [
  { bg: 'linear-gradient(135deg, #5A67F5, #8FA0FF)' },
  { bg: 'linear-gradient(135deg, #FFA47A, #ffc4a3)' },
  { bg: 'linear-gradient(135deg, #3EBCB9, #6ee0dd)' },
  { bg: 'linear-gradient(135deg, #67C100, #85d533)' },
]

const colors = [
  { name: 'Purple', hex: '#5A67F5' },
  { name: 'Coral', hex: '#FFA47A' },
  { name: 'Teal', hex: '#3EBCB9' },
  { name: 'Green', hex: '#67C100' },
  { name: 'Black', hex: '#2B2B2B' },
]

const sizes = ['小号', '标准', '大号', '加大号']

const ratingBars = [
  { label: '5 Star', value: 72 },
  { label: '4 Star', value: 18 },
  { label: '3 Star', value: 7 },
  { label: '2 Star', value: 2 },
  { label: '1 Star', value: 1 },
]

const reviews = ref([
  { id: 1, user: 'Sarah Johnson', stars: 5, date: 'Aug 15, 2026', text: 'Best headphones I have ever owned! The noise cancellation is incredible and the sound quality is top-notch. Battery lasts for days.' },
  { id: 2, user: 'Mike Chen', stars: 5, date: 'Aug 10, 2026', text: '长时间佩戴也很舒适。降噪功能在飞行中表现出色。强烈推荐！' },
  { id: 3, user: 'Emily Davis', stars: 4, date: 'Aug 2, 2026', text: 'Sound is amazing but wish the case was a bit smaller. Overall very satisfied with the purchase.' },
])

const shippingInfo = [
  { title: 'Free Shipping', desc: 'Free standard shipping on all orders over $50', icon: markRaw(Van), bg: '#5A67F5' },
  { title: '快速配送', desc: 'Express delivery available (1-3 business days)', icon: markRaw(Box), bg: '#3EBCB9' },
  { title: '轻松退货', desc: '30-day money-back guarantee, no questions asked', icon: markRaw(Wallet), bg: '#FFA47A' },
]

const relatedProducts = ref([
  { id: 1, name: '智能手表 Pro', price: 199.00, rating: 5, bg: 'linear-gradient(135deg, #3EBCB9, #6ee0dd)' },
  { id: 2, name: 'Wireless Earbuds', price: 59.99, rating: 4.5, bg: 'linear-gradient(135deg, #FFA47A, #ffc4a3)' },
  { id: 3, name: 'Bluetooth Speaker', price: 39.99, rating: 4, bg: 'linear-gradient(135deg, #67C100, #85d533)' },
  { id: 4, name: 'USB-C Charger', price: 24.99, rating: 4.5, bg: 'linear-gradient(135deg, #E56809, #ff8a3c)' },
])

const addToCart = () => {
  ElMessage.success('商品已加入购物车')
}
const buyNow = () => {
  ElMessage.success('正在跳转到结算页面...')
}
const toggleWishlist = () => {
  wishlisted.value = !wishlisted.value
  ElMessage.success(wishlisted.value ? '已加入收藏' : '已移出收藏')
}
</script>

<style scoped>
/* Gallery */
.gallery-main-img {
  height: 380px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 12px;
}
.discount-tag {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}
.thumbs-row {
  margin-bottom: 24px;
}
.thumb {
  height: 80px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}
.thumb.active {
  border-color: #5A67F5;
}

/* Detail Info */
.product-detail-info {
  padding: 0 8px;
}
.detail-category {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.detail-title {
  font-size: 24px;
  font-weight: 600;
  color: #2B2B2B;
  margin: 8px 0 12px;
  line-height: 1.3;
}
.detail-rating-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.review-link {
  font-size: 14px;
  color: #909399;
}
.detail-price-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-price {
  font-size: 32px;
  font-weight: 700;
  color: #5A67F5;
}
.detail-old-price {
  font-size: 18px;
  color: #c0c4cc;
  text-decoration: line-through;
}
.detail-short-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
  margin-bottom: 24px;
}

/* Options */
.option-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.option-label {
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
  min-width: 70px;
}
.color-options {
  display: flex;
  gap: 10px;
}
.color-dot {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}
.color-dot.active {
  border-color: #5A67F5;
}
.size-options {
  display: flex;
  gap: 8px;
}
.size-btn {
  padding: 8px 18px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  color: #606266;
  transition: all 0.2s;
}
.size-btn.active {
  background: #5A67F5;
  border-color: #5A67F5;
  color: #fff;
}
.size-btn:hover {
  border-color: #5A67F5;
}

/* Actions */
.action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 24px;
}
.quantity-block {
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
:deep(.el-button--primary) {
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
:deep(.el-button--danger) {
  --el-button-bg-color: #DC0808;
  --el-button-border-color: #DC0808;
  --el-button-hover-bg-color: #f02c2c;
  --el-button-hover-border-color: #f02c2c;
}

/* Tabs */
.detail-tabs-card {
  margin-top: 30px;
  border-radius: 12px;
}
:deep(.detail-tabs .el-tabs__item.is-active) {
  color: #5A67F5;
}
:deep(.detail-tabs .el-tabs__active-bar) {
  background-color: #5A67F5;
}
:deep(.detail-tabs .el-tabs__item:hover) {
  color: #5A67F5;
}
.tab-content {
  padding: 16px 0;
  color: #606266;
  line-height: 1.8;
}
.feature-list {
  list-style: none;
  padding: 0;
  margin: 16px 0 0;
}
.feature-list li {
  padding: 8px 0 8px 20px;
  position: relative;
  font-size: 14px;
  color: #606266;
}
.feature-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 16px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #5A67F5;
}

/* Reviews */
.review-summary {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
}
.rating-overview {
  text-align: center;
  padding: 16px 24px;
  border-right: 1px solid #ebeef5;
}
.rating-overview h2 {
  font-size: 42px;
  font-weight: 700;
  color: #5A67F5;
  margin: 0 0 8px;
}
.rating-overview p {
  font-size: 13px;
  color: #909399;
  margin: 8px 0 0;
}
.rating-breakdown {
  flex: 1;
  min-width: 200px;
}
.rating-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.bar-label {
  font-size: 12px;
  color: #909399;
  width: 45px;
}
.bar-track {
  flex: 1;
  height: 6px;
  background: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 3px;
}
.bar-value {
  font-size: 12px;
  color: #909399;
  width: 30px;
}
.review-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.review-item {
  display: flex;
  gap: 14px;
}
.review-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #5A67F5;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0;
}
.review-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}
.review-user {
  font-size: 14px;
  font-weight: 600;
  color: #2B2B2B;
}
.review-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 6px;
}
.review-date {
  font-size: 12px;
  color: #c0c4cc;
}

/* Shipping */
.shipping-info {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #f5f5f5;
}
.shipping-info:last-child {
  border-bottom: none;
}
.shipping-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.shipping-info h5 {
  margin: 0 0 4px;
  font-size: 15px;
  color: #5A67F5;
}
.shipping-info p {
  margin: 0;
  font-size: 13px;
  color: #606266;
}

/* Related */
.related-card {
  margin-top: 30px;
  border-radius: 12px;
}
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #5A67F5;
  margin: 0 0 20px;
}
.related-product-card {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}
.related-img {
  height: 120px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}
.related-info h5 {
  font-size: 14px;
  font-weight: 500;
  color: #2B2B2B;
  margin: 0 0 6px;
}
.related-price {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #5A67F5;
  margin-top: 6px;
}
.mr-4 {
  margin-right: 4px;
}
</style>
