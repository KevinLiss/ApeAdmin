<template>
  <div class="dashboard-default">
    <PageHeader title="Default Dashboard" :breadcrumb="['APEUI库', 'Dashboard', 'Default']" />

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

    <!-- 第一行：销售趋势 + 最新活动 -->
    <el-row :gutter="16" class="content-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>Sales Trend</template>
          <div class="chart-placeholder">
            <span>Sales Chart</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>Latest Activity</template>
          <el-timeline>
            <el-timeline-item
              v-for="act in activities"
              :key="act.time"
              :timestamp="act.time"
              :type="act.type"
            >
              {{ act.content }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：最近订单 + Top Products -->
    <el-row :gutter="16" class="content-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>Recent Orders</template>
          <el-table :data="orders" style="width: 100%" size="small">
            <el-table-column prop="id" label="Order ID" width="110" />
            <el-table-column prop="customer" label="Customer" />
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="amount" label="Amount" width="100" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>Top Products</template>
          <div class="top-products">
            <div class="product-item" v-for="(p, i) in topProducts" :key="p.name">
              <div class="product-rank">{{ i + 1 }}</div>
              <div class="product-info">
                <div class="product-name">{{ p.name }}</div>
                <div class="product-sales">{{ p.sales }} sales</div>
              </div>
              <div class="product-revenue">{{ p.revenue }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { ArrowUp, ArrowDown, Money, ShoppingCart, User, TrendCharts } from '@element-plus/icons-vue'
import { markRaw } from 'vue'

const statCards = [
  { label: 'Total Sales', value: '$54,210', icon: markRaw(Money), bg: '#534686', trend: '+12%', trendUp: true, trendLabel: 'from last month' },
  { label: 'New Orders', value: '1,489', icon: markRaw(ShoppingCart), bg: '#67C100', trend: '-3%', trendUp: false, trendLabel: 'from last month' },
  { label: 'Total Users', value: '8,425', icon: markRaw(User), bg: '#E56809', trend: '+8%', trendUp: true, trendLabel: 'from last month' },
  { label: 'Conversion', value: '3.5%', icon: markRaw(TrendCharts), bg: '#3EBCB9', trend: '+0.5%', trendUp: true, trendLabel: 'from last month' },
]

const activities = [
  { content: 'New order #ORD-00231 placed by Alice', time: '2026-08-20 10:30', type: 'primary' as const },
  { content: 'Product "Wireless Headphones" restocked', time: '2026-08-20 09:15', type: 'success' as const },
  { content: 'User registration spike: +24 new users', time: '2026-08-19 18:00', type: 'warning' as const },
  { content: 'Payment gateway maintenance completed', time: '2026-08-19 14:20', type: 'info' as const },
  { content: 'Monthly sales report generated', time: '2026-08-18 08:00', type: 'primary' as const },
]

const orders = [
  { id: 'ORD-00231', customer: 'Alice Johnson', date: '2026-08-20', amount: '$320.00', status: 'Paid' },
  { id: 'ORD-00230', customer: 'Bob Smith', date: '2026-08-19', amount: '$150.50', status: 'Pending' },
  { id: 'ORD-00229', customer: 'Carol White', date: '2026-08-19', amount: '$890.00', status: 'Paid' },
  { id: 'ORD-00228', customer: 'David Brown', date: '2026-08-18', amount: '$45.99', status: 'Refunded' },
  { id: 'ORD-00227', customer: 'Eva Green', date: '2026-08-18', amount: '$210.00', status: 'Paid' },
]

const topProducts = [
  { name: 'Wireless Headphones Pro', sales: 1240, revenue: '$62,000' },
  { name: 'Smart Watch Series 6', sales: 980, revenue: '$49,000' },
  { name: 'Bluetooth Speaker Mini', sales: 756, revenue: '$22,680' },
  { name: 'USB-C Hub 7-in-1', sales: 643, revenue: '$12,860' },
  { name: 'Mechanical Keyboard', sales: 521, revenue: '$26,050' },
]

function statusType(status: string) {
  const map: Record<string, string> = {
    Paid: 'success',
    Pending: 'warning',
    Refunded: 'danger',
  }
  return map[status] || 'info'
}
</script>

<style scoped>
.dashboard-default {
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

.chart-placeholder {
  height: 300px;
  border-radius: 8px;
  background: linear-gradient(135deg, #534686, #7b6fb5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder span {
  color: #fff;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 1px;
}

.top-products {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.product-item {
  display: flex;
  align-items: center;
  gap: 14px;
}

.product-rank {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f0ecf8;
  color: #534686;
  font-weight: 700;
  font-size: 15px;
  flex-shrink: 0;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.product-sales {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.product-revenue {
  font-size: 15px;
  font-weight: 700;
  color: #534686;
}
</style>
