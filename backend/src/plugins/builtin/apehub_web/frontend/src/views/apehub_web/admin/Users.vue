<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>用户管理</span>
      </div>
    </template>

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-input v-model="query.keyword" placeholder="搜索用户名/昵称/邮箱" clearable style="width: 240px" @keyup.enter="loadList" />
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table :data="userList" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="140" />
      <el-table-column prop="nickname" label="昵称" width="140" />
      <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column label="开发者" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_developer" type="success" size="small">是</el-tag>
          <span v-else class="text-muted">否</span>
        </template>
      </el-table-column>
      <el-table-column label="余额" width="100">
        <template #default="{ row }">{{ row.balance }} USDT</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80" />
      <el-table-column prop="created_at" label="注册时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <template #empty><div style="padding: 24px">暂无用户</div></template>
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
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAdminUsers } from '@/api/apehub_web'

const userList = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const query = ref({ keyword: '', page: 1, page_size: 20 })

const formatDate = (d: string) => d ? d.replace('T', ' ').slice(0, 16) : '-'

const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminUsers({ keyword: query.value.keyword || undefined, page: query.value.page, page_size: query.value.page_size })
    userList.value = data.items || []
    total.value = data.total || 0
  } finally { loading.value = false }
}

onMounted(loadList)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }
.text-muted { color: #909399; font-size: 13px; }
</style>
