<template>
  <div class="product-page">
    <PageHeader title="商品管理" :breadcrumb="['APEUI库', '电商模块', '商品管理']">
      <template #actions>
        <el-button type="primary" :icon="Grid">网格视图</el-button>
      </template>
    </PageHeader>

    <!-- Toolbar -->
    <el-card class="ape-card toolbar-card" shadow="never">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-select v-model="categoryFilter" placeholder="All Categories" clearable style="width: 180px">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
          <el-select v-model="sortBy" placeholder="Sort By" clearable style="width: 180px">
            <el-option label="Price: Low to High" value="price-asc" />
            <el-option label="Price: High to Low" value="price-desc" />
            <el-option label="Top Rated" value="rating" />
            <el-option label="Newest" value="newest" />
          </el-select>
        </div>
        <div class="toolbar-right">
          <el-input v-model="searchQuery" placeholder="Search products..." :prefix-icon="Search" clearable style="width: 260px" />
        </div>
      </div>
    </el-card>

    <!-- Product Grid -->
    <el-row :gutter="30" class="product-grid">
      <el-col v-for="product in pagedProducts" :key="product.id" :xs="12" :sm="8" :md="6" style="margin-bottom: 30px">
        <el-card class="ape-card product-card" shadow="hover" :body-style="{ padding: '0' }">
          <div class="product-img" :style="{ background: product.bgColor }">
            <el-icon :size="48" color="rgba(255,255,255,0.85)"><Goods /></el-icon>
            <span class="product-badge" v-if="product.badge" :style="{ background: product.badgeColor }">{{ product.badge }}</span>
            <button class="wishlist-btn" @click="toggleWishlist(product)">
              <el-icon :size="18" :color="product.wishlisted ? '#DC0808' : '#fff'">
                <Star v-if="!product.wishlisted" />
                <StarFilled v-else />
              </el-icon>
            </button>
          </div>
          <div class="product-info">
            <span class="product-category">{{ product.category }}</span>
            <h4 class="product-name">{{ product.name }}</h4>
            <div class="product-rating">
              <el-rate v-model="product.rating" disabled size="small" />
              <span class="review-count">({{ product.reviews }})</span>
            </div>
            <div class="product-price-row">
              <span class="product-price">${{ product.price.toFixed(2) }}</span>
              <span class="product-old-price" v-if="product.oldPrice">${{ product.oldPrice.toFixed(2) }}</span>
            </div>
            <el-button type="primary" class="add-cart-btn" @click="addToCart(product)">
              <el-icon class="mr-4"><ShoppingCart /></el-icon>
              Add to Cart
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Pagination -->
    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="filteredProducts.length"
        :page-sizes="[8, 12, 16, 24]"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Goods, Star, StarFilled, ShoppingCart, Grid } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface Product {
  id: number
  name: string
  category: string
  price: number
  oldPrice?: number
  rating: number
  reviews: number
  bgColor: string
  badge?: string
  badgeColor?: string
  wishlisted: boolean
}

const categories = ['全部', '电子产品', '时尚服饰', '家居生活', '运动户外', '美妆护肤']
const categoryFilter = ref('全部')
const sortBy = ref('')
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(8)

const products = ref<Product[]>([
  { id: 1, name: '无线蓝牙耳机', category: '电子产品', price: 79.99, oldPrice: 129.99, rating: 4.5, reviews: 128, bgColor: 'linear-gradient(135deg, #5A67F5, #8FA0FF)', badge: '特惠', badgeColor: '#DC0808', wishlisted: false },
  { id: 2, name: '智能手表 Pro 7代', category: '电子产品', price: 199.00, oldPrice: 299.00, rating: 5, reviews: 342, bgColor: 'linear-gradient(135deg, #3EBCB9, #6ee0dd)', badge: '热门', badgeColor: '#E56809', wishlisted: false },
  { id: 3, name: '精梳棉休闲T恤', category: '时尚服饰', price: 29.99, rating: 4, reviews: 89, bgColor: 'linear-gradient(135deg, #FFA47A, #ffc4a3)', wishlisted: true },
  { id: 4, name: '气垫跑步鞋 Air Max', category: '运动户外', price: 89.99, oldPrice: 119.99, rating: 4.5, reviews: 215, bgColor: 'linear-gradient(135deg, #67C100, #85d533)', badge: '新品', badgeColor: '#5A67F5', wishlisted: false },
  { id: 5, name: '智能手机 X Pro Max 256GB', category: '电子产品', price: 999.00, oldPrice: 1099.00, rating: 5, reviews: 521, bgColor: 'linear-gradient(135deg, #5A67F5, #4F58E8)', badge: '热门', badgeColor: '#E56809', wishlisted: false },
  { id: 6, name: '陶瓷咖啡杯套装（4只装）', category: '家居生活', price: 34.99, rating: 4, reviews: 67, bgColor: 'linear-gradient(135deg, #E56809, #ff8a3c)', wishlisted: false },
  { id: 7, name: '有机护肤礼盒套装', category: '美妆护肤', price: 59.99, oldPrice: 89.99, rating: 4.5, reviews: 156, bgColor: 'linear-gradient(135deg, #FFA47A, #ffd0b8)', badge: '特惠', badgeColor: '#DC0808', wishlisted: true },
  { id: 8, name: '防滑专业瑜伽垫', category: '运动户外', price: 49.99, rating: 4, reviews: 98, bgColor: 'linear-gradient(135deg, #3EBCB9, #5dd4d1)', wishlisted: false },
])

const filteredProducts = computed(() => {
  let result = products.value
  if (categoryFilter.value && categoryFilter.value !== '全部') {
    result = result.filter(p => p.category === categoryFilter.value)
  }
  if (searchQuery.value) {
    result = result.filter(p => p.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  if (sortBy.value === 'price-asc') {
    result = [...result].sort((a, b) => a.price - b.price)
  } else if (sortBy.value === 'price-desc') {
    result = [...result].sort((a, b) => b.price - a.price)
  } else if (sortBy.value === 'rating') {
    result = [...result].sort((a, b) => b.rating - a.rating)
  }
  return result
})

const pagedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredProducts.value.slice(start, start + pageSize.value)
})

const addToCart = (product: Product) => {
  ElMessage.success(`${product.name} added to cart`)
}

const toggleWishlist = (product: Product) => {
  product.wishlisted = !product.wishlisted
  ElMessage.success(product.wishlisted ? `${product.name} added to wishlist` : `${product.name} removed from wishlist`)
}
</script>

<style scoped>
.toolbar-card {
  margin-bottom: 24px;
  border-radius: 12px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.toolbar-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.product-card {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s ease;
}
.product-card:hover {
  transform: translateY(-4px);
}
.product-img {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.product-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 0.5px;
}
.wishlist-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.25);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.wishlist-btn:hover {
  background: rgba(0, 0, 0, 0.45);
}
.product-info {
  padding: 16px;
}
.product-category {
  font-size: 11px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.product-name {
  font-size: 15px;
  font-weight: 500;
  color: #2B2B2B;
  margin: 6px 0 8px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}
.product-rating {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}
.review-count {
  font-size: 12px;
  color: #909399;
}
.product-price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 14px;
}
.product-price {
  font-size: 22px;
  font-weight: 600;
  color: #5A67F5;
}
.product-old-price {
  font-size: 14px;
  color: #c0c4cc;
  text-decoration: line-through;
}
.add-cart-btn {
  width: 100%;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
.mr-4 {
  margin-right: 4px;
}
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style>
