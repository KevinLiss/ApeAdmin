<template>
  <div class="wishlist-page">
    <PageHeader title="心愿单" :breadcrumb="['APEUI库', '电商模块', '心愿单']">
      <template #actions>
        <el-button :icon="ShoppingCart" @click="addAllToCart">全部移入购物车</el-button>
      </template>
    </PageHeader>

    <!-- 顶部：排序 + 批量操作 -->
    <el-card shadow="never" class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <span class="wishlist-count">共 <strong>{{ products.length }}</strong> 件收藏商品</span>
          <el-divider direction="vertical" />
          <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
        </div>
        <div class="toolbar-right">
          <el-select v-model="sortBy" placeholder="排序方式" style="width: 160px">
            <el-option label="最新添加" value="newest" />
            <el-option label="价格从低到高" value="price-asc" />
            <el-option label="价格从高到低" value="price-desc" />
            <el-option label="名称 A-Z" value="name-asc" />
          </el-select>
          <el-button v-if="selectedIds.length > 0" type="danger" plain :icon="Delete" @click="batchRemove">
            移除收藏 ({{ selectedIds.length }})
          </el-button>
          <el-button v-if="selectedIds.length > 0" type="primary" plain :icon="ShoppingCart" @click="batchAddToCart">
            移入购物车 ({{ selectedIds.length }})
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 商品网格 -->
    <div v-if="sortedProducts.length > 0">
      <el-row :gutter="30">
        <el-col :span="6" v-for="product in sortedProducts" :key="product.id" class="product-col">
          <el-card shadow="hover" :class="['product-card', { selected: selectedIds.includes(product.id) }]">
            <div class="product-image" :style="{ background: product.bgColor }">
              <el-icon :size="48" :color="product.iconColor"><component :is="product.icon" /></el-icon>
              <el-checkbox
                v-model="product.checked"
                class="product-checkbox"
                @change="handleCheck(product)"
              />
              <div class="product-badge" v-if="product.badge">{{ product.badge }}</div>
            </div>
            <div class="product-info">
              <div class="product-name">{{ product.name }}</div>
              <div class="product-category">{{ product.category }}</div>
              <div class="product-price-row">
                <span class="product-price">${{ product.price.toFixed(2) }}</span>
                <span class="product-original" v-if="product.originalPrice">${{ product.originalPrice.toFixed(2) }}</span>
              </div>
              <div class="product-meta">
                <el-rate v-model="product.rating" disabled size="small" />
                <span class="review-count">({{ product.reviews }})</span>
              </div>
              <div class="product-actions">
                <el-button type="primary" size="small" :icon="ShoppingCart" @click="addToCart(product)" class="action-btn">移入购物车</el-button>
                <el-button type="danger" size="small" :icon="Delete" circle @click="removeProduct(product)" />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 空收藏 -->
    <el-card shadow="never" v-else>
      <el-empty description="您的收藏清单还是空的" :image-size="120">
        <el-button type="primary" :icon="Goods">去逛逛</el-button>
      </el-empty>
    </el-card>

    <!-- 移入购物车成功提示 -->
    <el-dialog v-model="cartDialogVisible" title="已加入购物车" width="420px">
      <div class="cart-dialog-content">
        <el-icon :size="48" color="#67C100"><CircleCheck /></el-icon>
        <p class="cart-dialog-text">商品已成功加入购物车！</p>
        <div class="cart-dialog-product" v-if="lastAdded">
          <span>{{ lastAdded.name }}</span>
          <span class="cart-dialog-price">${{ lastAdded.price.toFixed(2) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="cartDialogVisible = false">继续收藏</el-button>
        <el-button type="primary" @click="cartDialogVisible = false">去购物车</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { ShoppingCart, Delete, Goods, CircleCheck, Iphone, Notebook, Watch, Headset, Monitor, Camera } from '@element-plus/icons-vue'
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const sortBy = ref('newest')
const selectAll = ref(false)
const cartDialogVisible = ref(false)
const lastAdded = ref(null as any)

const products = ref([
  { id: 1, name: 'iPhone 15 Pro Max 256GB', category: '手机数码', price: 1199.00, originalPrice: 1299.00, rating: 5, reviews: 128, badge: '热销', icon: Iphone, bgColor: '#EDF2FF', iconColor: '#5A67F5', checked: false },
  { id: 2, name: 'MacBook Air M3 13英寸', category: '笔记本电脑', price: 999.00, originalPrice: 1099.00, rating: 5, reviews: 86, badge: '新品', icon: Notebook, bgColor: '#fff3ec', iconColor: '#FFA47A', checked: false },
  { id: 3, name: 'Apple Watch Ultra 2', category: '智能穿戴', price: 799.00, originalPrice: null, rating: 4, reviews: 54, badge: '', icon: Watch, bgColor: '#e8f7f6', iconColor: '#3EBCB9', checked: false },
  { id: 4, name: 'AirPods Pro 2 (USB-C)', category: '音频设备', price: 249.00, originalPrice: 279.00, rating: 5, reviews: 210, badge: '推荐', icon: Headset, bgColor: '#eef7e8', iconColor: '#67C100', checked: false },
  { id: 5, name: 'iMac 24英寸 M3', category: '台式电脑', price: 1499.00, originalPrice: null, rating: 4, reviews: 32, badge: '', icon: Monitor, bgColor: '#fdeaea', iconColor: '#DC0808', checked: false },
  { id: 6, name: 'GoPro HERO12 Black', category: '摄影摄像', price: 449.00, originalPrice: 499.00, rating: 4, reviews: 67, badge: '促销', icon: Camera, bgColor: '#fef4e8', iconColor: '#E56809', checked: false },
])

const selectedIds = computed(() => products.value.filter(p => p.checked).map(p => p.id))

const sortedProducts = computed(() => {
  const list = [...products.value]
  switch (sortBy.value) {
    case 'price-asc': return list.sort((a, b) => a.price - b.price)
    case 'price-desc': return list.sort((a, b) => b.price - a.price)
    case 'name-asc': return list.sort((a, b) => a.name.localeCompare(b.name))
    default: return list
  }
})

function handleSelectAll(val: boolean) {
  products.value.forEach(p => p.checked = val)
}

function handleCheck(product: any) {
  selectAll.value = products.value.every(p => p.checked)
}

function addToCart(product: any) {
  lastAdded.value = product
  cartDialogVisible.value = true
}

function removeProduct(product: any) {
  ElMessageBox.confirm(`确定要移除「${product.name}」吗？`, '移除收藏', {
    confirmButtonText: '确定移除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    products.value = products.value.filter(p => p.id !== product.id)
    ElMessage.success('已移除收藏')
  }).catch(() => {})
}

function batchRemove() {
  ElMessageBox.confirm(`确定要移除选中的 ${selectedIds.value.length} 件商品吗？`, '批量移除', {
    confirmButtonText: '确定移除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    products.value = products.value.filter(p => !p.checked)
    selectAll.value = false
    ElMessage.success('批量移除成功')
  }).catch(() => {})
}

function batchAddToCart() {
  ElMessage.success(`已将 ${selectedIds.value.length} 件商品加入购物车`)
  products.value.forEach(p => { if (p.checked) p.checked = false })
  selectAll.value = false
}

function addAllToCart() {
  ElMessage.success(`已将全部 ${products.value.length} 件收藏商品加入购物车`)
}
</script>

<style scoped>
.toolbar-card {
  margin-bottom: 20px;
}

.toolbar-card :deep(.el-card__body) {
  padding: 12px 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.wishlist-count {
  font-size: 14px;
  color: #606266;
}

.wishlist-count strong {
  color: #5A67F5;
  font-size: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-col {
  margin-bottom: 30px;
}

.product-card {
  overflow: hidden;
  transition: all 0.3s;
}

.product-card.selected {
  border-color: #5A67F5;
  box-shadow: 0 0 0 2px rgba(90, 103, 245, 0.15);
}

.product-card :deep(.el-card__body) {
  padding: 0;
}

.product-image {
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-radius: 4px 4px 0 0;
}

.product-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
}

.product-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #5A67F5;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 12px;
}

.product-info {
  padding: 14px 16px;
}

.product-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-category {
  font-size: 12px;
  color: #c0c4cc;
  margin-bottom: 8px;
}

.product-price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.product-price {
  font-size: 18px;
  font-weight: 700;
  color: #5A67F5;
}

.product-original {
  font-size: 13px;
  color: #c0c4cc;
  text-decoration: line-through;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
}

.review-count {
  font-size: 12px;
  color: #c0c4cc;
}

.product-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
}

/* 弹窗 */
.cart-dialog-content {
  text-align: center;
  padding: 10px 0;
}

.cart-dialog-text {
  font-size: 16px;
  color: #303133;
  margin: 12px 0;
}

.cart-dialog-product {
  display: flex;
  justify-content: space-between;
  padding: 10px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
}

.cart-dialog-price {
  font-weight: 600;
  color: #5A67F5;
}
</style>
