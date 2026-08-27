<template>
  <el-card shadow="never" class="page-card">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-select v-model="query.method" placeholder="请求方法" clearable style="width: 130px" @change="fetchData">
        <el-option label="GET" value="GET" />
        <el-option label="POST" value="POST" />
        <el-option label="PUT" value="PUT" />
        <el-option label="DELETE" value="DELETE" />
      </el-select>
      <el-input
        v-model="query.path"
        placeholder="搜索路径"
        clearable
        style="width: 220px"
        @keyup.enter="fetchData"
      />
      <el-select v-model="query.status_code" placeholder="状态码" clearable style="width: 130px" @change="fetchData">
        <el-option label="2xx 成功" :value="200" />
        <el-option label="4xx 客户端错误" :value="400" />
        <el-option label="5xx 服务器错误" :value="500" />
      </el-select>
      <el-button type="primary" @click="fetchData">
        <el-icon><Search /></el-icon>查询
      </el-button>
      <el-button type="danger" @click="handleClear" v-if="hasDeletePerm">
        <el-icon><Delete /></el-icon>清空日志
      </el-button>
    </div>

    <!-- Table -->
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="用户" min-width="100">
        <template #default="{ row }">{{ row.username || '-' }}</template>
      </el-table-column>
      <el-table-column label="方法" width="80">
        <template #default="{ row }">
          <el-tag :type="methodTagType(row.method)" size="small">{{ row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态码" width="90">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status_code)" size="small">{{ row.status_code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="耗时" width="90">
        <template #default="{ row }">{{ row.duration_ms }}ms</template>
      </el-table-column>
      <el-table-column prop="ip" label="IP" width="130" />
      <el-table-column label="时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next, jumper"
      class="pagination"
      @change="fetchData"
    />
  </el-card>

  <!-- Detail Dialog -->
  <el-dialog v-model="detailVisible" title="日志详情" width="640px">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="ID">{{ detail.id }}</el-descriptions-item>
      <el-descriptions-item label="用户">{{ detail.username || '-' }}</el-descriptions-item>
      <el-descriptions-item label="用户ID">{{ detail.user_id || '-' }}</el-descriptions-item>
      <el-descriptions-item label="请求方法">{{ detail.method }}</el-descriptions-item>
      <el-descriptions-item label="路径" :span="2">{{ detail.path }}</el-descriptions-item>
      <el-descriptions-item label="状态码">{{ detail.status_code }}</el-descriptions-item>
      <el-descriptions-item label="耗时">{{ detail.duration_ms }}ms</el-descriptions-item>
      <el-descriptions-item label="IP">{{ detail.ip || '-' }}</el-descriptions-item>
      <el-descriptions-item label="时间">{{ formatTime(detail.created_at) }}</el-descriptions-item>
      <el-descriptions-item label="参数" :span="2">
        <pre class="log-pre">{{ detail.params || '-' }}</pre>
      </el-descriptions-item>
      <el-descriptions-item label="User-Agent" :span="2">{{ detail.user_agent || '-' }}</el-descriptions-item>
      <el-descriptions-item label="错误" :span="2">
        <span v-if="detail.error" class="log-error">{{ detail.error }}</span>
        <span v-else>-</span>
      </el-descriptions-item>
    </el-descriptions>
    <template #footer>
      <el-button v-if="hasDeletePerm" type="danger" @click="handleDeleteOne(detail)">删除此条</el-button>
      <el-button @click="detailVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLogs, getLogDetail, deleteLog, clearLogs } from '@/api'
import { useUserStore } from '@/stores/user'

interface LogRow {
  id: number
  user_id: number | null
  username: string | null
  method: string
  path: string
  params: string | null
  status_code: number
  duration_ms: number
  ip: string | null
  user_agent: string | null
  error: string | null
  created_at: string | null
}

const list = ref<LogRow[]>([])
const total = ref(0)
const loading = ref(false)
const detailVisible = ref(false)
const detail = ref<Partial<LogRow>>({})

const query = reactive({
  page: 1,
  page_size: 20,
  method: '',
  path: '',
  status_code: undefined as number | undefined,
})

// Check delete permission via userStore
const userStore = useUserStore()
const hasDeletePerm = computed(() => userStore.hasPermission('system:log:delete'))

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: query.page, page_size: query.page_size }
    if (query.method) params.method = query.method
    if (query.path) params.path = query.path
    if (query.status_code) params.status_code = query.status_code
    const data: any = await getLogs(params)
    list.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function methodTagType(method: string) {
  const map: Record<string, string> = { GET: 'info', POST: 'success', PUT: 'warning', DELETE: 'danger' }
  return map[method] || ''
}

function statusTagType(code: number) {
  if (code >= 200 && code < 300) return 'success'
  if (code >= 400 && code < 500) return 'warning'
  if (code >= 500) return 'danger'
  return 'info'
}

function formatTime(iso: string | null | undefined) {
  if (!iso) return '-'
  const d = new Date(iso)
  return d.toLocaleString('zh-CN', { hour12: false })
}

async function openDetail(row: LogRow) {
  const data: any = await getLogDetail(row.id)
  detail.value = data
  detailVisible.value = true
}

async function handleDeleteOne(row: Partial<LogRow>) {
  if (!row.id) return
  await ElMessageBox.confirm('确定删除这条日志吗？', '提示', { type: 'warning' })
  await deleteLog(row.id)
  ElMessage.success('删除成功')
  detailVisible.value = false
  fetchData()
}

async function handleClear() {
  await ElMessageBox.confirm('确定清空所有日志吗？此操作不可恢复！', '警告', { type: 'warning' })
  await clearLogs()
  ElMessage.success('已清空所有日志')
  fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
.page-card {
  border-radius: 8px;
}
.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}
.pagination {
  margin-top: 14px;
  justify-content: flex-end;
}
.log-pre {
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  font-size: 13px;
  max-height: 120px;
  overflow-y: auto;
}
.log-error {
  color: #f56c6c;
}
</style>
