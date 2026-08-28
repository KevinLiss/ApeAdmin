<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>提现审核</span>
      </div>
    </template>

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-select v-model="query.status" placeholder="按状态筛选" clearable style="width: 140px" @change="loadList">
        <el-option label="待处理" value="pending" />
        <el-option label="已通过" value="approved" />
        <el-option label="已驳回" value="rejected" />
        <el-option label="已完成" value="done" />
      </el-select>
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table :data="withdrawalList" v-loading="loading" stripe>
      <el-table-column prop="username" label="用户" width="120" />
      <el-table-column label="申请金额" width="130">
        <template #default="{ row }">{{ row.amount }} USDT</template>
      </el-table-column>
      <el-table-column label="手续费 / 到账" width="160"><template #default="{ row }">{{ row.fee }} / {{ row.net_amount }} USDT</template></el-table-column>
      <el-table-column label="网络" width="90"><template #default="{ row }">{{ row.network || 'TRC20' }}</template></el-table-column>
      <el-table-column prop="account" label="收款地址" min-width="230" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      <el-table-column prop="tx_hash" label="交易哈希" min-width="180" show-overflow-tooltip />
      <el-table-column prop="created_at" label="申请时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" type="success" @click="handle(row, 'approve')">通过</el-button>
            <el-button size="small" type="danger" @click="handle(row, 'reject')">驳回</el-button>
          </template>
          <el-button v-if="row.status === 'approved'" size="small" type="primary" @click="handle(row, 'done')">确认已打款</el-button>
        </template>
      </el-table-column>
      <template #empty><div style="padding: 24px">暂无提现申请</div></template>
    </el-table>

    <!-- 分页 -->
    <div class="pager" v-if="total > query.page_size">
      <el-pagination
        v-model:current-page="query.page"
        :page-size="query.page_size"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadList"
      />
    </div>

    <!-- 备注弹窗 -->
    <el-dialog v-model="remarkDialogVisible" :title="pendingAction === 'done' ? '确认 TRC20 打款' : '处理提现申请'" width="520px">
      <el-input v-model="remarkText" type="textarea" :rows="2" placeholder="备注（可选）" />
      <el-input v-if="pendingAction === 'done'" v-model="txHash" style="margin-top:12px" placeholder="TRC20 链上交易哈希（必填）" />
      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmHandle">确认</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminWithdrawals, handleWithdrawal } from '@/api/apehub_web'

const withdrawalList = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const query = ref({ status: '', page: 1, page_size: 20 })

const remarkDialogVisible = ref(false)
const remarkText = ref('')
const txHash = ref('')
const pendingRow = ref<any>(null)
const pendingAction = ref('')

const statusLabel = (s: string) => ({ pending: '待处理', approved: '已通过', rejected: '已驳回', done: '已完成' }[s] || s)
const statusType = (s: string) => ({ pending: 'warning', approved: 'success', rejected: 'danger', done: 'info' } as any)[s] || 'info'

const formatDate = (d: string) => d ? d.replace('T', ' ').slice(0, 16) : '-'

const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminWithdrawals({ status: query.value.status || undefined, page: query.value.page, page_size: query.value.page_size })
    withdrawalList.value = data.items || []
    total.value = data.total || 0
  } finally { loading.value = false }
}

const handle = (row: any, action: string) => {
  pendingRow.value = row
  pendingAction.value = action
  remarkText.value = ''
  txHash.value = ''
  remarkDialogVisible.value = true
}

const confirmHandle = async () => {
  if (!pendingRow.value) return
  if (pendingAction.value === 'done' && !txHash.value.trim()) return ElMessage.warning('请填写 TRC20 交易哈希')
  const actionLabel = { approve: '通过', reject: '驳回', done: '打款' }[pendingAction.value]
  await handleWithdrawal(pendingRow.value.id, { action: pendingAction.value, remark: remarkText.value, tx_hash: txHash.value.trim() })
  ElMessage.success(`已${actionLabel}`)
  remarkDialogVisible.value = false
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }
</style>
