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
      <el-table-column label="金额" width="100">
        <template #default="{ row }">¥{{ row.amount?.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="方式" width="80">
        <template #default="{ row }">{{ row.method === 'alipay' ? '支付宝' : '银行卡' }}</template>
      </el-table-column>
      <el-table-column prop="account" label="账号" min-width="160" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      <el-table-column prop="created_at" label="申请时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" type="success" @click="handle(row, 'approve')">通过</el-button>
            <el-button size="small" type="danger" @click="handle(row, 'reject')">驳回</el-button>
            <el-button size="small" type="primary" @click="handle(row, 'done')">打款</el-button>
          </template>
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
    <el-dialog v-model="remarkDialogVisible" title="处理备注" width="480px">
      <el-input v-model="remarkText" type="textarea" :rows="2" placeholder="备注（可选）" />
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
const pendingRow = ref<any>(null)
const pendingAction = ref('')

const statusLabel = (s: string) => ({ pending: '待处理', approved: '已通过', rejected: '已驳回', done: '已完成' }[s] || s)
const statusType = (s: string) => ({ pending: 'warning', approved: 'success', rejected: 'danger', done: 'info' } as any)

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
  remarkDialogVisible.value = true
}

const confirmHandle = async () => {
  if (!pendingRow.value) return
  const actionLabel = { approve: '通过', reject: '驳回', done: '打款' }[pendingAction.value]
  await handleWithdrawal(pendingRow.value.id, pendingAction.value, remarkText.value)
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
