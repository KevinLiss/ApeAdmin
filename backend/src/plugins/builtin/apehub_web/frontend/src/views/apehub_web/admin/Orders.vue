<template>
  <el-card shadow="never">
    <template #header>订单管理</template>
    <el-table v-loading="loading" :data="orders" stripe>
      <el-table-column prop="order_no" label="订单号" min-width="180" />
      <el-table-column prop="username" label="用户" width="120" />
      <el-table-column prop="plugin_name" label="插件" min-width="160" />
      <el-table-column label="金额" width="100"><template #default="{ row }">¥{{ row.amount?.toFixed(2) }}</template></el-table-column>
      <el-table-column label="状态" width="100"><template #default="{ row }"><el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag></template></el-table-column>
      <el-table-column label="创建时间" width="170"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
    </el-table>
    <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
    <div v-if="total > query.page_size" class="pager"><el-pagination v-model:current-page="query.page" :page-size="query.page_size" :total="total" layout="prev, pager, next" @current-change="load" /></div>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getAdminOrders } from '@/api/apehub_web'

const orders = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const query = ref({ page: 1, page_size: 20 })
const statusLabel = (status: string) => ({ pending: '待支付', paid: '已支付', cancelled: '已取消', refunded: '已退款' }[status] || status)
const statusType = (status: string) => ({ pending: 'warning', paid: 'success', cancelled: 'info', refunded: 'danger' }[status] || 'info')
const formatDate = (value: string) => value ? value.replace('T', ' ').slice(0, 16) : '-'

const load = async () => {
  loading.value = true
  try {
    const data = await getAdminOrders(query.value)
    orders.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.pager { display: flex; justify-content: center; margin-top: 16px; }
</style>
