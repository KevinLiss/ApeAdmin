<template>
  <div class="orders-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card total">
        <div class="stat-icon">📋</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总订单</div>
        </div>
      </div>
      <div class="stat-card paid">
        <div class="stat-icon">✅</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.paid }}</div>
          <div class="stat-label">已支付</div>
        </div>
      </div>
      <div class="stat-card pending">
        <div class="stat-icon">⏳</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待支付</div>
        </div>
      </div>
      <div class="stat-card refunded">
        <div class="stat-icon">↩️</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.refunded }}</div>
          <div class="stat-label">已退款</div>
        </div>
      </div>
      <div class="stat-card revenue">
        <div class="stat-icon">💰</div>
        <div class="stat-body">
          <div class="stat-value">{{ fmtMoney(stats.revenue) }} <small>USDT</small></div>
          <div class="stat-label">已收总额</div>
        </div>
      </div>
    </div>

    <!-- 主卡片 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <span class="header-note">购买记录 · 分成明细 · 退款处理</span>
        </div>
      </template>

      <div class="toolbar">
        <el-input v-model="localStatus" placeholder="状态筛选" clearable style="width: 130px" @change="filterByStatus" />
        <el-button type="primary" @click="load">查询</el-button>
      </div>

      <el-table :data="filteredOrders" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="订单号" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="order-no">{{ row.order_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="plugin_name" label="插件" min-width="150" show-overflow-tooltip />
        <el-table-column label="金额" width="100">
          <template #default="{ row }">
            <span class="amount-text">{{ fmtMoney(row.amount) }} USDT</span>
          </template>
        </el-table-column>
        <el-table-column label="服务费 / 开发者收益" width="160">
          <template #default="{ row }">
            <div class="fee-cell">
              <span>服务费 {{ fmtMoney(row.service_fee) }} USDT</span>
              <small>收益 {{ fmtMoney(row.developer_income) }} USDT</small>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light" round>{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="支付时间" width="160">
          <template #default="{ row }">{{ row.paid_at ? formatDate(row.paid_at) : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'paid'" text type="danger" @click="openRefund(row)">退款</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无订单" /></template>
      </el-table>

      <div class="pager" v-if="total > query.page_size">
        <el-pagination v-model:current-page="query.page" :page-size="query.page_size" :total="total" layout="prev, pager, next" @current-change="load" />
      </div>
    </el-card>

    <!-- 退款弹窗 -->
    <el-dialog v-model="refundVisible" title="订单退款" width="480px" destroy-on-close>
      <div class="dialog-body">
        <div class="order-info">
          <div class="info-row">
            <span class="info-label">订单号</span>
            <span class="info-val">{{ refundRow?.order_no }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">插件</span>
            <span class="info-val">{{ refundRow?.plugin_name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">金额</span>
            <span class="info-val amount">{{ fmtMoney(refundRow?.amount) }} USDT</span>
          </div>
          <div class="info-row">
            <span class="info-label">用户</span>
            <span class="info-val">{{ refundRow?.username }}</span>
          </div>
        </div>
        <div class="dialog-hint warn">
          <el-icon><WarningFilled /></el-icon>
          <span>退款将通过 LemPay 原路返回。退款后用户下载权限将被撤销，开发者收益同步扣减。</span>
        </div>
        <el-input v-model="refundReason" type="textarea" :rows="3" style="margin-top: 12px" placeholder="退款原因（必填）" />
      </div>
      <template #footer>
        <el-button @click="refundVisible = false">取消</el-button>
        <el-button type="danger" :loading="refundLoading" @click="confirmRefund">确认退款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'
import { getAdminOrders, refundAdminOrder } from '@/api/apehub_web'

const orders = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const query = ref({ page: 1, page_size: 20 })
const localStatus = ref('')
const refundVisible = ref(false)
const refundRow = ref<any>(null)
const refundReason = ref('')
const refundLoading = ref(false)

const stats = ref({ total: 0, paid: 0, pending: 0, refunded: 0, revenue: 0 })

const statusLabel = (s: string) => ({ pending: '待支付', paid: '已支付', cancelled: '已取消', refunded: '已退款' }[s] || s)
const statusType = (s: string) => ({ pending: 'warning', paid: 'success', cancelled: 'info', refunded: 'danger' } as any)[s] || 'info'
const formatDate = (v: string) => v ? v.replace('T', ' ').slice(0, 16) : '-'

// 金额格式化：最多 2 位小数，去除多余尾零
const fmtMoney = (v: any) => {
  const n = Number(v || 0)
  if (!isFinite(n)) return '0'
  return n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

// 前端筛选（后端暂不支持 status 参数）
const filteredOrders = computed(() => {
  if (!localStatus.value) return orders.value
  return orders.value.filter(o => o.status === localStatus.value)
})

const filterByStatus = () => { query.value.page = 1; load() }

const load = async () => {
  loading.value = true
  try {
    const data = await getAdminOrders(query.value)
    orders.value = data.items || []
    total.value = data.total || 0
    // 计算统计
    const s = { total: data.total || 0, paid: 0, pending: 0, refunded: 0, revenue: 0 }
    for (const o of orders.value) {
      if (o.status === 'paid') { s.paid++; s.revenue += Number(o.amount) }
      if (o.status === 'pending') s.pending++
      if (o.status === 'refunded') s.refunded++
    }
    stats.value = s
  } finally { loading.value = false }
}

const openRefund = (row: any) => {
  refundRow.value = row
  refundReason.value = ''
  refundVisible.value = true
}
const confirmRefund = async () => {
  if (!refundRow.value) return
  if (!refundReason.value.trim()) return ElMessage.warning('请填写退款原因')
  refundLoading.value = true
  try {
    await refundAdminOrder(refundRow.value.id, { reason: refundReason.value.trim() })
    ElMessage.success('退款已提交')
    refundVisible.value = false
    await load()
  } finally { refundLoading.value = false }
}

onMounted(load)
</script>

<style scoped>
.stats-row { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-card {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 24px; border-radius: 12px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-lighter);
  min-width: 140px; flex: 1; transition: all 0.2s;
}
.stat-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.stat-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.stat-card.total .stat-icon { background: #e6f0ff; }
.stat-card.paid .stat-icon { background: #e8f5e9; }
.stat-card.pending .stat-icon { background: #fef3e2; }
.stat-card.refunded .stat-icon { background: #fde2e2; }
.stat-card.revenue .stat-icon { background: #e6e6fa; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-value small { font-size: 12px; font-weight: 400; color: var(--el-text-color-secondary); }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-note { color: var(--el-text-color-secondary); font-size: 12px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }

.order-no { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; }
.amount-text { font-weight: 600; color: #e6a23c; }
.fee-cell { display: flex; flex-direction: column; }
.fee-cell small { font-size: 11px; color: #67c23a; }

.dialog-body { padding: 4px 0; }
.order-info {
  display: flex; flex-direction: column; gap: 10px;
  padding: 16px; margin-bottom: 16px;
  background: var(--el-fill-color-lighter);
  border-radius: 10px;
}
.info-row { display: flex; justify-content: space-between; align-items: center; }
.info-label { font-size: 13px; color: var(--el-text-color-secondary); }
.info-val { font-size: 14px; font-weight: 500; color: var(--el-text-color-primary); }
.info-val.amount { color: #e6a23c; font-weight: 700; }
.dialog-hint {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 14px; border-radius: 8px; font-size: 13px;
  background: #fef3e2; color: #e65100;
}
.dialog-hint .el-icon { margin-top: 1px; flex-shrink: 0; }

@media (max-width: 768px) {
  .stats-row { gap: 8px; }
  .stat-card { min-width: 100px; padding: 12px; }
  .stat-value { font-size: 18px; }
}
</style>
