<template>
  <div class="withdrawals-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card pending">
        <div class="stat-icon">⏳</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待处理</div>
        </div>
      </div>
      <div class="stat-card approved">
        <div class="stat-icon">✅</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">待打款</div>
        </div>
      </div>
      <div class="stat-card done">
        <div class="stat-icon">💰</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.done }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card amount">
        <div class="stat-icon">📥</div>
        <div class="stat-body">
          <div class="stat-value">{{ fmtMoney(stats.totalAmount) }} <small>USDT</small></div>
          <div class="stat-label">待处理总额</div>
        </div>
      </div>
    </div>

    <!-- 主卡片 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>提现审核</span>
          <span class="header-note">待处理 → 通过 → 确认打款 → 完成</span>
        </div>
      </template>

      <div class="toolbar">
        <el-select v-model="query.status" placeholder="按状态筛选" clearable style="width: 140px" @change="search">
          <el-option label="待处理" value="pending" />
          <el-option label="待打款" value="approved" />
          <el-option label="已驳回" value="rejected" />
          <el-option label="已完成" value="done" />
        </el-select>
        <el-button type="primary" @click="search">查询</el-button>
      </div>

      <el-table :data="withdrawalList" v-loading="loading" stripe>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column label="申请金额" width="120">
          <template #default="{ row }">
            <span class="amount-text">{{ fmtMoney(row.amount) }} USDT</span>
          </template>
        </el-table-column>
        <el-table-column label="手续费 / 到账" width="160">
          <template #default="{ row }">
            <div class="fee-cell">
              <span class="fee-text">{{ fmtMoney(row.fee) }} USDT</span>
              <small>到账 {{ fmtMoney(row.net_amount) }} USDT</small>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="网络" width="80">
          <template #default="{ row }">{{ row.network || 'TRC20' }}</template>
        </el-table-column>
        <el-table-column prop="account" label="收款地址" min-width="230" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="addr-text">{{ row.account }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="light" round>{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tx_hash" label="交易哈希" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.tx_hash" class="tx-hash">{{ row.tx_hash }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="申请时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" @click="openDialog(row, 'approve')">通过</el-button>
              <el-button size="small" type="danger" plain @click="openDialog(row, 'reject')">驳回</el-button>
            </template>
            <el-button v-if="row.status === 'approved'" size="small" type="primary" @click="openDialog(row, 'done')">
              确认打款
            </el-button>
            <el-tag v-if="row.status === 'done'" type="success" size="small" effect="dark">已完成</el-tag>
            <el-tag v-if="row.status === 'rejected'" type="danger" size="small" effect="dark">已驳回</el-tag>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无提现申请" /></template>
      </el-table>

      <div class="pager" v-if="total > query.page_size">
        <el-pagination
          v-model:current-page="query.page"
          :page-size="query.page_size"
          :total="total"
          layout="prev, pager, next"
          @current-change="loadList"
        />
      </div>
    </el-card>

    <!-- 操作弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" destroy-on-close>
      <div class="dialog-body">
        <!-- 申请人信息 -->
        <div class="withdrawal-info">
          <div class="info-row">
            <span class="info-label">用户</span>
            <span class="info-val">{{ pendingRow?.username }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">申请金额</span>
            <span class="info-val amount">{{ fmtMoney(pendingRow?.amount) }} USDT</span>
          </div>
          <div class="info-row">
            <span class="info-label">手续费</span>
            <span class="info-val">{{ fmtMoney(pendingRow?.fee) }} USDT</span>
          </div>
          <div class="info-row">
            <span class="info-label">实际到账</span>
            <span class="info-val amount">{{ fmtMoney(pendingRow?.net_amount) }} USDT</span>
          </div>
          <div class="info-row">
            <span class="info-label">收款地址</span>
            <span class="info-val addr">{{ pendingRow?.account }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">网络</span>
            <span class="info-val">{{ pendingRow?.network || 'TRC20' }}</span>
          </div>
        </div>

        <!-- 确认打款提示 -->
        <div v-if="pendingAction === 'done'" class="dialog-hint warn">
          <el-icon><WarningFilled /></el-icon>
          <span>请确认已在 TRC20 网络完成 USDT 转账，并填写链上交易哈希。完成后用户余额将正式扣减。</span>
        </div>
        <div v-if="pendingAction === 'approve'" class="dialog-hint">
          <el-icon><InfoFilled /></el-icon>
          <span>通过后进入"待打款"状态，您需要在链上完成转账后点击"确认打款"。</span>
        </div>
        <div v-if="pendingAction === 'reject'" class="dialog-hint warn">
          <el-icon><WarningFilled /></el-icon>
          <span>驳回后申请金额将退回用户可用余额。请填写驳回原因。</span>
        </div>

        <!-- 表单 -->
        <el-input
          v-if="pendingAction === 'done'"
          v-model="txHash"
          style="margin-top: 12px"
          placeholder="TRC20 链上交易哈希（必填，如：0x1a2b3c...）"
        >
          <template #prefix><el-icon><Link /></el-icon></template>
        </el-input>
        <el-input
          v-model="remarkText"
          type="textarea"
          :rows="2"
          style="margin-top: 12px"
          :placeholder="pendingAction === 'reject' ? '驳回原因（建议填写）' : '备注（可选）'"
        />
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          :type="pendingAction === 'reject' ? 'danger' : pendingAction === 'approve' ? 'success' : 'primary'"
          :loading="actionLoading"
          @click="confirmHandle"
        >
          {{ actionButtonLabel }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled, InfoFilled, Link } from '@element-plus/icons-vue'
import { getAdminWithdrawals, handleWithdrawal } from '@/api/apehub_web'

const withdrawalList = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const actionLoading = ref(false)
const query = ref({ status: '', page: 1, page_size: 20 })

const dialogVisible = ref(false)
const remarkText = ref('')
const txHash = ref('')
const pendingRow = ref<any>(null)
const pendingAction = ref('')

const stats = ref({ pending: 0, approved: 0, done: 0, totalAmount: 0 })

const statusLabel = (s: string) =>
  ({ pending: '待处理', approved: '待打款', rejected: '已驳回', done: '已完成' }[s] || s)
const statusType = (s: string) =>
  ({ pending: 'warning', approved: 'success', rejected: 'danger', done: 'info' } as any)[s] || 'info'

const formatDate = (d: string) => d ? d.replace('T', ' ').slice(0, 16) : '-'

// 金额格式化：最多 2 位小数，去除多余尾零
const fmtMoney = (v: any) => {
  const n = Number(v || 0)
  if (!isFinite(n)) return '0'
  return n.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

const dialogTitle = computed(() => {
  const titles: Record<string, string> = {
    approve: '通过提现申请',
    reject: '驳回提现申请',
    done: '确认 TRC20 打款',
  }
  return titles[pendingAction.value] || '处理提现'
})
const actionButtonLabel = computed(() => {
  const labels: Record<string, string> = {
    approve: '确认通过',
    reject: '确认驳回',
    done: '确认已打款',
  }
  return labels[pendingAction.value] || '确认'
})

const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminWithdrawals({
      status: query.value.status || undefined,
      page: query.value.page,
      page_size: query.value.page_size,
    })
    withdrawalList.value = data.items || []
    total.value = data.total || 0
    // 计算统计
    const s = { pending: 0, approved: 0, done: 0, totalAmount: 0 }
    for (const w of withdrawalList.value) {
      if (w.status === 'pending') { s.pending++; s.totalAmount += Number(w.amount) }
      if (w.status === 'approved') { s.approved++; s.totalAmount += Number(w.amount) }
      if (w.status === 'done') s.done++
    }
    stats.value = s
  } finally { loading.value = false }
}
const search = () => { query.value.page = 1; loadList() }

const openDialog = (row: any, action: string) => {
  pendingRow.value = row
  pendingAction.value = action
  remarkText.value = ''
  txHash.value = ''
  dialogVisible.value = true
}

const confirmHandle = async () => {
  if (!pendingRow.value) return
  if (pendingAction.value === 'done' && !txHash.value.trim())
    return ElMessage.warning('请填写 TRC20 交易哈希')
  actionLoading.value = true
  try {
    await handleWithdrawal(pendingRow.value.id, {
      action: pendingAction.value,
      remark: remarkText.value,
      tx_hash: txHash.value.trim(),
    })
    ElMessage.success(`已${actionButtonLabel.value.replace('确认', '')}`)
    dialogVisible.value = false
    await loadList()
  } finally { actionLoading.value = false }
}

onMounted(loadList)
</script>

<style scoped>
/* 统计卡片 */
.stats-row {
  display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap;
}
.stat-card {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 24px; border-radius: 12px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-lighter);
  min-width: 140px; flex: 1; transition: all 0.2s;
}
.stat-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.stat-icon {
  width: 42px; height: 42px;
  border-radius: 10px; display: flex; align-items: center; justify-content: center;
  font-size: 20px;
}
.stat-card.pending .stat-icon { background: #fef3e2; }
.stat-card.approved .stat-icon { background: #e8f5e9; }
.stat-card.done .stat-icon { background: #e6e6fa; }
.stat-card.amount .stat-icon { background: #e6f0ff; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-value small { font-size: 12px; font-weight: 400; color: var(--el-text-color-secondary); }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }

/* 主卡片 */
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-note { color: var(--el-text-color-secondary); font-size: 12px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }

/* 表格 */
.amount-text { font-weight: 600; color: #e6a23c; }
.fee-cell { display: flex; flex-direction: column; }
.fee-text { color: var(--el-text-color-secondary); font-size: 13px; }
.fee-cell small { font-size: 11px; color: #67c23a; }
.addr-text { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; }
.tx-hash { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; color: var(--el-color-primary); }

/* 弹窗 */
.dialog-body { padding: 4px 0; }
.withdrawal-info {
  display: flex; flex-direction: column; gap: 10px;
  padding: 16px; margin-bottom: 16px;
  background: var(--el-fill-color-lighter);
  border-radius: 10px;
}
.info-row { display: flex; justify-content: space-between; align-items: center; }
.info-label { font-size: 13px; color: var(--el-text-color-secondary); }
.info-val { font-size: 14px; font-weight: 500; color: var(--el-text-color-primary); }
.info-val.amount { color: #e6a23c; font-weight: 700; }
.info-val.addr { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; word-break: break-all; max-width: 280px; }
.dialog-hint {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 14px; border-radius: 8px;
  font-size: 13px;
}
.dialog-hint { background: #e6f4ec; color: #2e7d32; }
.dialog-hint.warn { background: #fef3e2; color: #e65100; }
.dialog-hint .el-icon { margin-top: 1px; flex-shrink: 0; }

/* 响应式 */
@media (max-width: 768px) {
  .stats-row { gap: 8px; }
  .stat-card { min-width: 100px; padding: 12px; }
  .stat-value { font-size: 18px; }
}
</style>
