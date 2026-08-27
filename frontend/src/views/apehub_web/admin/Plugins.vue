<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>插件审核</span>
      </div>
    </template>

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-select v-model="query.status" placeholder="按状态筛选" clearable style="width: 140px" @change="loadList">
        <el-option label="待审核" value="pending" />
        <el-option label="已上架" value="approved" />
        <el-option label="已驳回" value="rejected" />
        <el-option label="已下架" value="offline" />
      </el-select>
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table :data="pluginList" v-loading="loading" stripe>
      <el-table-column prop="display_name" label="名称" min-width="160" />
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="version" label="版本" width="80" />
      <el-table-column label="价格" width="80">
        <template #default="{ row }">{{ row.price > 0 ? '¥' + row.price : '免费' }}</template>
      </el-table-column>
      <el-table-column prop="developer.username" label="开发者" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="download_count" label="下载" width="80" />
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <template v-if="row.status === 'pending'">
            <el-button size="small" type="success" @click="handleReview(row, 'approve')">通过</el-button>
            <el-button size="small" type="danger" @click="handleReview(row, 'reject')">驳回</el-button>
          </template>
          <template v-else-if="row.status === 'approved'">
            <el-button size="small" type="warning" @click="handleOffline(row)">下架</el-button>
          </template>
          <template v-else-if="row.status === 'offline' || row.status === 'rejected'">
            <el-button size="small" type="success" @click="handleOnline(row)">上架</el-button>
          </template>
        </template>
      </el-table-column>
      <template #empty><div style="padding: 24px">暂无插件</div></template>
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

    <!-- 驳回弹窗 -->
    <el-dialog v-model="rejectDialogVisible" title="驳回原因" width="480px">
      <el-input v-model="rejectReason" type="textarea" :rows="3" placeholder="请填写驳回原因" />
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminPlugins, reviewPlugin, offlinePlugin, onlinePlugin } from '@/api/apehub_web'

const pluginList = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const query = ref({ status: '', page: 1, page_size: 20 })

const rejectDialogVisible = ref(false)
const rejectReason = ref('')
const rejectingRow = ref<any>(null)

const statusLabel = (s: string) => ({ pending: '待审核', approved: '已上架', rejected: '已驳回', offline: '已下架' }[s] || s)
const statusType = (s: string) => ({ pending: 'warning', approved: 'success', rejected: 'danger', offline: 'info' } as any)

const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminPlugins({ status: query.value.status || undefined, page: query.value.page, page_size: query.value.page_size })
    pluginList.value = data.items || []
    total.value = data.total || 0
  } finally { loading.value = false }
}

const handleReview = (row: any, action: string) => {
  if (action === 'reject') {
    rejectingRow.value = row
    rejectReason.value = ''
    rejectDialogVisible.value = true
    return
  }
  doReview(row, 'approve', '')
}

const confirmReject = async () => {
  if (rejectingRow.value) {
    await doReview(rejectingRow.value, 'reject', rejectReason.value)
    rejectDialogVisible.value = false
  }
}

const doReview = async (row: any, action: string, reason: string) => {
  await reviewPlugin(row.id, { action, reason })
  ElMessage.success(action === 'approve' ? '已通过审核' : '已驳回')
  loadList()
}

const handleOffline = async (row: any) => {
  await ElMessageBox.confirm(`确认下架「${row.display_name}」？`, '提示', { type: 'warning' })
  await offlinePlugin(row.id)
  ElMessage.success('已下架')
  loadList()
}

const handleOnline = async (row: any) => {
  await ElMessageBox.confirm(`确认重新上架「${row.display_name}」？`, '提示', { type: 'warning' })
  await onlinePlugin(row.id)
  ElMessage.success('已上架')
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }
</style>
