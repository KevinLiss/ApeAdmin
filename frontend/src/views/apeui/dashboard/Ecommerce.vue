<template>
  <div class="dashboard-ecommerce">
    <PageHeader title="Ecommerce Dashboard" :breadcrumb="['APEUI库', 'Dashboard', 'Ecommerce']" />

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <div class="stat-card">
          <div class="stat-icon" :style="{ background: card.bg }">
            <el-icon :size="26" color="#fff"><component :is="card.icon" /></el-icon>
          </div>
          <div class="stat-body">
            <div class="stat-label">{{ card.label }}</div>
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-trend">
              <span :class="card.trendUp ? 'up' : 'down'">
                <el-icon><ArrowUp v-if="card.trendUp" /><ArrowDown v-else /></el-icon>
                {{ card.trend }}
              </span>
              <span class="trend-label">{{ card.trendLabel }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 内容区：产品分类饼图 + 最新订单 -->
    <el-row :gutter="16" class="content-row">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>Product Categories</template>
          <div class="pie-placeholder">
            <span>Category Pie Chart</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>Latest Orders</template>
          <el-table :data="orders" style="width: 100%" size="small">
            <el-table-column prop="id" label="Order ID" width="120" />
            <el-table-column prop="customer" label="Customer" />
            <el-table-column prop="product" label="Product" />
            <el-table-column prop="amount" label="Amount" width="100" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { ArrowUp, ArrowDown, Money, ShoppingCart, View, PieChart } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

const statCards = [
  { label: 'Revenue', value: '$95,420', icon: markRaw(Money), bg: '#534686', trend: '+15%', trendUp: true, trendLabel: 'vs last week' },
  { label: 'Orders', value: '2,310', icon: markRaw(ShoppingCart), bg: '#67C100', trend: '+6%', trendUp: true, trendLabel: 'vs last week' },
  { label: 'Visitors', value: '48,200', icon: markRaw(View), bg: '#E56809', trend: '+12%', trendUp: true, trendLabel: 'vs last week' },
  { label: 'Bounce Rate', value: '32%', icon: markRaw(PieChart), bg: '#3EBCB9', trend: '-2%', trendUp: false, trendLabel: 'vs last week' },
]

const orders = [
  { id: 'ORD-00301', customer: 'Frank Miller', product: 'Smart Watch', amount: '$199.00', status: 'Paid' },
  { id: 'ORD-00300', customer: 'Grace Lee', product: 'Earbuds Pro', amount: '$89.99', status: 'Pending' },
  { id: 'ORD-00299', customer: 'Henry Chen', product: 'Tablet Stand', amount: '$25.00', status: 'Shipped' },
  { id: 'ORD-00298', customer: 'Ivy Wang', product: 'Wireless Charger', amount: '$35.50', status: 'Paid' },
  { id: 'ORD-00297', customer: 'Jack Wilson', product: 'Laptop Sleeve', amount: '$42.00', status: 'Refunded' },
]

function statusType(status: string) {
  const map: Record<string, string> = {
    Paid: 'success',
    Pending: 'warning',
    Shipped: 'primary',
    Refunded: 'danger',
  }
  return map[status] || 'info'
}
</script>

<style scoped>
.dashboard-ecommerce {
  padding: 0;
}

.stat-row {
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-trend {
  font-size: 12px;
  margin-top: 4px;
}

.stat-trend .up {
  color: #67c100;
}

.stat-trend .down {
  color: #f56c6c;
}

.stat-trend .up .el-icon,
.stat-trend .down .el-icon {
  vertical-align: -2px;
}

.trend-label {
  color: #909399;
  margin-left: 4px;
}

.content-row {
  margin-bottom: 16px;
}

.pie-placeholder {
  height: 280px;
  border-radius: 8px;
  background: linear-gradient(135deg, #534686, #9b8fd0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-placeholder span {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}
</style>
