<template>
  <el-card shadow="never" class="page-card">
    <div class="toolbar">
      <el-select v-model="filterType" placeholder="全部类型" clearable style="width: 140px" @change="fetchData">
        <el-option label="工具调用" value="tool" />
        <el-option label="资源读取" value="resource" />
        <el-option label="提示词渲染" value="prompt" />
      </el-select>
      <el-input
        v-model="keyword"
        placeholder="搜索工具名/用户名"
        clearable
        style="width: 220px"
        @keyup.enter="fetchData"
        @clear="fetchData"
      />
      <el-button type="primary" @click="fetchData">
        <el-icon><Search /></el-icon>查询
      </el-button>
      <el-button @click="resetQuery">
        <el-icon><Refresh /></el-icon>重置
      </el-button>
    </div>

    <el-table :data="logs" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="typeTag(row.action_type)" size="small">{{ typeLabel(row.action_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target_name" label="目标" min-width="180">
        <template #default="{ row }">
          <code class="target-code">{{ row.target_name }}</code>
        </template>
      </el-table-column>
      <el-table-column label="参数" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="muted">{{ row.arguments || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="操作用户" width="120" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
            {{ row.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="170" />
      <el-table-column label="结果预览" min-width="200">
        <template #default="{ row }">
          <span class="muted">{{ (row.result_preview || '').slice(0, 80) }}</span>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchData"
        @size-change="fetchData"
      />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMcpAuditLogs } from '@/api'

const logs = ref<any[]>([])
const loading = ref(false)
const filterType = ref('')
const keyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

function typeLabel(t: string) {
  return { tool: '工具调用', resource: '资源读取', prompt: '提示词渲染' }[t] || t
}

function typeTag(t: string) {
  return { tool: 'primary', resource: 'success', prompt: 'warning' }[t] || 'info'
}

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getMcpAuditLogs({
      page: page.value,
      page_size: pageSize.value,
      action_type: filterType.value || undefined,
      keyword: keyword.value || undefined,
    })
    logs.value = data?.items || []
    total.value = data?.total || 0
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  filterType.value = ''
  keyword.value = ''
  page.value = 1
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
  flex-wrap: wrap;
}
.target-code {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  color: #5A67F5;
}
.muted {
  color: #909399;
  font-size: 12px;
}
.result {
  color: #606266;
  font-size: 12px;
}
.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
</style>