<template>
  <div class="product-list-page">
    <PageHeader title="商品列表" :breadcrumb="['APEUI库', '电商模块', '商品列表']">
      <template #actions>
        <el-button type="primary" :icon="Plus" @click="onAdd">添加商品</el-button>
      </template>
    </PageHeader>

    <el-card class="koho-card" shadow="never">
      <!-- Toolbar -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input v-model="searchQuery" placeholder="按商品名称搜索..." :prefix-icon="Search" clearable style="width: 260px" />
          <el-select v-model="categoryFilter" placeholder="全部分类" clearable style="width: 180px">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 150px">
            <el-option label="已上架" value="published" />
            <el-option label="草稿" value="draft" />
            <el-option label="缺货" value="out" />
          </el-select>
        </div>
      </div>

      <!-- Table -->
      <el-table :data="pagedData" class="product-table" stripe>
        <el-table-column label="商品" min-width="240">
          <template #default="{ row }">
            <div class="product-cell">
              <div class="product-thumb" :style="{ background: row.bgColor }">
                <el-icon :size="22" color="rgba(255,255,255,0.8)"><Goods /></el-icon>
              </div>
              <div class="product-cell-info">
                <span class="product-cell-name">{{ row.name }}</span>
                <span class="product-cell-sku">SKU: {{ row.sku }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="140" />
        <el-table-column label="价格" width="120">
          <template #default="{ row }">
            <span class="price-text">${{ row.price.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100" sortable>
          <template #default="{ row }">
            <span :class="{ 'stock-low': row.stock < 50 }">{{ row.stock }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="130">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="light" round>
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sales" label="销量" width="100" sortable>
          <template #default="{ row }">
            <span class="sales-text">{{ row.sales }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Edit" @click="onEdit(row)">编辑</el-button>
            <el-button link type="danger" :icon="Delete" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredData.length"
          :page-sizes="[5, 8, 10, 20]"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Edit, Delete, Goods } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface ProductItem {
  id: number
  name: string
  sku: string
  category: string
  price: number
  stock: number
  status: 'published' | 'draft' | 'out'
  sales: number
  bgColor: string
}

const categories = ['电子产品', '时尚服饰', '家居生活', '运动户外', '美妆护肤']
const searchQuery = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(8)

const products = ref<ProductItem[]>([
  { id: 1, name: '无线蓝牙耳机', sku: 'SKU-HP-001', category: '电子产品', price: 79.99, stock: 245, status: 'published', sales: 1280, bgColor: 'linear-gradient(135deg, #5A67F5, #8FA0FF)' },
  { id: 2, name: '智能手表 Pro 7代', sku: 'SKU-SW-002', category: '电子产品', price: 199.00, stock: 78, status: 'published', sales: 856, bgColor: 'linear-gradient(135deg, #3EBCB9, #6ee0dd)' },
  { id: 3, name: '精梳棉休闲T恤', sku: 'SKU-TS-003', category: '时尚服饰', price: 29.99, stock: 560, status: 'published', sales: 2100, bgColor: 'linear-gradient(135deg, #FFA47A, #ffc4a3)' },
  { id: 4, name: '气垫跑步鞋 Air Max', sku: 'SKU-SN-004', category: '运动户外', price: 89.99, stock: 34, status: 'published', sales: 670, bgColor: 'linear-gradient(135deg, #67C100, #85d533)' },
  { id: 5, name: '智能手机 X Pro Max 256GB', sku: 'SKU-SP-005', category: '电子产品', price: 999.00, stock: 0, status: 'out', sales: 430, bgColor: 'linear-gradient(135deg, #5A67F5, #4F58E8)' },
  { id: 6, name: '陶瓷咖啡杯套装（4只装）', sku: 'SKU-MG-006', category: '家居生活', price: 34.99, stock: 320, status: 'published', sales: 450, bgColor: 'linear-gradient(135deg, #E56809, #ff8a3c)' },
  { id: 7, name: '有机护肤礼盒套装', sku: 'SKU-SK-007', category: '美妆护肤', price: 59.99, stock: 120, status: 'draft', sales: 0, bgColor: 'linear-gradient(135deg, #FFA47A, #ffd0b8)' },
  { id: 8, name: '防滑专业瑜伽垫', sku: 'SKU-YM-008', category: '运动户外', price: 49.99, stock: 180, status: 'published', sales: 920, bgColor: 'linear-gradient(135deg, #3EBCB9, #5dd4d1)' },
])

const filteredData = computed(() => {
  let result = products.value
  if (searchQuery.value) {
    result = result.filter(p => p.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  if (categoryFilter.value) {
    result = result.filter(p => p.category === categoryFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }
  return result
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const statusTagType = (status: string) => {
  if (status === 'published') return 'success'
  if (status === 'draft') return 'info'
  if (status === 'out') return 'danger'
  return 'info'
}

const statusLabel = (status: string) => {
  if (status === 'published') return '已上架'
  if (status === 'draft') return '草稿'
  if (status === 'out') return '缺货'
  return status
}

const onAdd = () => ElMessage.info('跳转到添加商品页面')
const onEdit = (row: ProductItem) => ElMessage.info(`正在编辑「${row.name}」`)
const onDelete = (row: ProductItem) => {
  ElMessageBox.confirm(`确定要删除「${row.name}」吗？`, '删除商品', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    products.value = products.value.filter(p => p.id !== row.id)
    ElMessage.success('商品删除成功')
  }).catch(() => {})
}
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.toolbar-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Table */
.product-table {
  width: 100%;
}
:deep(.product-table th) {
  font-size: 13px;
  font-weight: 600;
  color: #2B2B2B;
}
:deep(.product-table td) {
  font-size: 13px;
}
.product-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}
.product-thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.product-cell-info {
  display: flex;
  flex-direction: column;
}
.product-cell-name {
  font-size: 13px;
  font-weight: 500;
  color: #2B2B2B;
}
.product-cell-sku {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}
.price-text {
  font-weight: 600;
  color: #5A67F5;
}
.stock-low {
  color: #DC0808;
  font-weight: 500;
}
.sales-text {
  font-weight: 500;
  color: #2B2B2B;
}

:deep(.el-button--primary) {
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
:deep(.el-button--primary.is-link) {
  --el-button-text-color: #5A67F5;
  --el-button-hover-text-color: #4F58E8;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
