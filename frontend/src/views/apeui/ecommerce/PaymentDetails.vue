<template>
  <div class="payment-details-page">
    <PageHeader title="支付详情" :breadcrumb="['APEUI库', '电商模块', '支付详情']" />

    <!-- 顶部统计卡片 -->
    <el-row :gutter="30" class="stat-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ background: stat.bg, color: stat.color }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-trend" :class="stat.trendUp ? 'up' : 'down'">
              <el-icon><CaretTop v-if="stat.trendUp" /><CaretBottom v-else /></el-icon>
              {{ stat.change }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="30" class="main-row">
      <!-- 左侧：交易记录表格 -->
      <el-col :span="17">
        <el-card shadow="never" class="table-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">交易记录</span>
              <div class="header-tools">
                <el-input v-model="searchKey" placeholder="搜索订单号/客户" clearable style="width: 220px" :prefix-icon="Search" />
                <el-select v-model="statusFilter" placeholder="状态" clearable style="width: 130px">
                  <el-option label="全部" value="" />
                  <el-option label="已支付" value="已支付" />
                  <el-option label="待处理" value="待处理" />
                  <el-option label="已退款" value="已退款" />
                  <el-option label="支付失败" value="支付失败" />
                </el-select>
                <el-button type="primary" :icon="Download">导出</el-button>
              </div>
            </div>
          </template>
          <el-table :data="filteredTransactions" stripe style="width: 100%">
            <el-table-column prop="orderNo" label="订单号" min-width="150" />
            <el-table-column prop="customer" label="客户" min-width="130" />
            <el-table-column prop="amount" label="金额" min-width="110" align="right">
              <template #default="{ row }">
                <span class="amount-text">${{ row.amount.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="method" label="支付方式" min-width="130">
              <template #default="{ row }">
                <el-tag effect="plain" size="small">{{ row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="110">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" effect="light">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date" label="日期" min-width="120" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewDetail(row)">查看</el-button>
                <el-button v-if="row.status === '待处理'" link type="warning" size="small" @click="remind(row)">催收</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 右侧：支付方式分布 -->
      <el-col :span="7">
        <el-card shadow="never" class="distribution-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">支付方式分布</span>
            </div>
          </template>
          <div class="distribution-list">
            <div class="dist-item" v-for="item in methodDistribution" :key="item.name">
              <div class="dist-top">
                <span class="dist-label">
                  <span class="dist-dot" :style="{ background: item.color }"></span>
                  {{ item.name }}
                </span>
                <span class="dist-value">{{ item.percentage }}%</span>
              </div>
              <el-progress :percentage="item.percentage" :color="item.color" :stroke-width="8" :show-text="false" />
              <div class="dist-amount">${{ item.amount.toFixed(2) }}</div>
            </div>
          </div>
          <el-divider />
          <div class="dist-summary">
            <div class="summary-row">
              <span>交易总笔数</span>
              <span class="summary-val">{{ transactions.length }}</span>
            </div>
            <div class="summary-row">
              <span>成功率</span>
              <span class="summary-val" style="color: #67C100">87.5%</span>
            </div>
            <div class="summary-row">
              <span>平均交易额</span>
              <span class="summary-val">${{ avgAmount }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 交易详情弹窗 -->
    <el-dialog v-model="detailVisible" title="交易详情" width="520px">
      <el-descriptions :column="1" border v-if="currentDetail">
        <el-descriptions-item label="订单号">{{ currentDetail.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ currentDetail.customer }}</el-descriptions-item>
        <el-descriptions-item label="金额"><span class="amount-text">${{ currentDetail.amount.toFixed(2) }}</span></el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ currentDetail.method }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTagType(currentDetail.status)" effect="light">{{ currentDetail.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="日期">{{ currentDetail.date }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue'
import { Search, Download, CaretTop, CaretBottom, Money, Wallet, Clock, RefreshLeft } from '@element-plus/icons-vue'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const searchKey = ref('')
const statusFilter = ref('')
const detailVisible = ref(false)
const currentDetail = ref(null as any)

const stats = [
  { label: '总收入', value: '$48,520.00', change: '12.5%', trendUp: true, icon: Money, bg: '#EDF2FF', color: '#5A67F5' },
  { label: '本月收入', value: '$12,380.00', change: '8.2%', trendUp: true, icon: Wallet, bg: '#fff3ec', color: '#FFA47A' },
  { label: '待收款', value: '$3,240.00', change: '3.1%', trendUp: false, icon: Clock, bg: '#e8f7f6', color: '#3EBCB9' },
  { label: '退款', value: '$860.00', change: '2.4%', trendUp: false, icon: RefreshLeft, bg: '#fdeaea', color: '#DC0808' },
]

const transactions = ref([
  { orderNo: 'ORD-2026-0801', customer: '张伟', amount: 1280.00, method: 'Visa', status: '已支付', date: '2026-08-01' },
  { orderNo: 'ORD-2026-0802', customer: '李娜', amount: 560.00, method: 'PayPal', status: '待处理', date: '2026-08-03' },
  { orderNo: 'ORD-2026-0803', customer: '王芳', amount: 2340.50, method: '万事达卡', status: '已支付', date: '2026-08-05' },
  { orderNo: 'ORD-2026-0804', customer: '刘强', amount: 890.00, method: '微信支付', status: '已退款', date: '2026-08-07' },
  { orderNo: 'ORD-2026-0805', customer: '陈静', amount: 1670.00, method: '支付宝', status: '已支付', date: '2026-08-09' },
  { orderNo: 'ORD-2026-0806', customer: '赵磊', amount: 420.00, method: 'Visa', status: '支付失败', date: '2026-08-11' },
  { orderNo: 'ORD-2026-0807', customer: '孙丽', amount: 3120.00, method: '万事达卡', status: '已支付', date: '2026-08-13' },
  { orderNo: 'ORD-2026-0808', customer: '周涛', amount: 780.00, method: 'PayPal', status: '待处理', date: '2026-08-15' },
])

const methodDistribution = [
  { name: 'Visa', percentage: 38, amount: 1700.00, color: '#5A67F5' },
  { name: 'Mastercard', percentage: 25, amount: 5460.50, color: '#FFA47A' },
  { name: 'PayPal', percentage: 17, amount: 1340.00, color: '#3EBCB9' },
  { name: '支付宝', percentage: 12, amount: 1670.00, color: '#67C100' },
  { name: '微信支付', percentage: 8, amount: 890.00, color: '#E56809' },
]

const filteredTransactions = computed(() => {
  return transactions.value.filter(t => {
    const matchSearch = !searchKey.value || t.orderNo.toLowerCase().includes(searchKey.value.toLowerCase()) || t.customer.includes(searchKey.value)
    const matchStatus = !statusFilter.value || t.status === statusFilter.value
    return matchSearch && matchStatus
  })
})

const avgAmount = computed(() => {
  const total = transactions.value.reduce((sum, t) => sum + t.amount, 0)
  return (total / transactions.value.length).toFixed(2)
})

function statusTagType(status: string) {
  const map: Record<string, string> = {
    '已支付': 'success',
    '待处理': 'warning',
    '已退款': 'info',
    '支付失败': 'danger',
  }
  return map[status] || ''
}

function viewDetail(row: any) {
  currentDetail.value = row
  detailVisible.value = true
}

function remind(row: any) {
  ElMessage.success(`已向 ${row.customer} 发送催收通知`)
}
</script>

<style scoped>
.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
  margin-top: 4px;
}

.stat-trend.up {
  color: #67C100;
}

.stat-trend.down {
  color: #DC0808;
}

.main-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.header-tools {
  display: flex;
  gap: 10px;
  align-items: center;
}

.amount-text {
  font-weight: 600;
  color: #5A67F5;
}

.distribution-card {
  height: 100%;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.dist-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.dist-label {
  font-size: 13px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 6px;
}

.dist-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dist-value {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.dist-amount {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.dist-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
}

.summary-val {
  font-weight: 600;
  color: #303133;
}
</style>
