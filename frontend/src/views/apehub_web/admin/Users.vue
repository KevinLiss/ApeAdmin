<template>
  <div class="users-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card total">
        <div class="stat-icon">👥</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总用户</div>
        </div>
      </div>
      <div class="stat-card dev">
        <div class="stat-icon">🛠️</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.developers }}</div>
          <div class="stat-label">开发者</div>
        </div>
      </div>
      <div class="stat-card balance">
        <div class="stat-icon">💼</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.totalBalance }} <small>USDT</small></div>
          <div class="stat-label">用户余额合计</div>
        </div>
      </div>
    </div>

    <!-- 主卡片 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <span class="header-note">注册用户 · 开发者身份 · 余额</span>
        </div>
      </template>

      <div class="toolbar">
        <el-input v-model="query.keyword" placeholder="搜索用户名 / 昵称 / 邮箱" clearable style="width: 280px" @keyup.enter="search">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="search">查询</el-button>
      </div>

      <el-table :data="userList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="130" />
        <el-table-column prop="nickname" label="昵称" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="开发者" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_developer" type="success" size="small" effect="light" round>开发者</el-tag>
            <span v-else class="text-muted">普通用户</span>
          </template>
        </el-table-column>
        <el-table-column label="余额" width="120">
          <template #default="{ row }">
            <span class="balance-text">{{ row.balance }} USDT</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small" effect="light" round>{{ row.status === 1 ? '正常' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="160">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <template #empty><el-empty description="暂无用户" /></template>
      </el-table>

      <div class="pager" v-if="total > query.page_size">
        <el-pagination v-model:current-page="query.page" :page-size="query.page_size" :total="total" layout="prev, pager, next" @current-change="loadList" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getAdminUsers } from '@/api/apehub_web'

const userList = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const query = ref({ keyword: '', page: 1, page_size: 20 })
const stats = ref({ total: 0, developers: 0, totalBalance: 0 })

const formatDate = (d: string) => d ? d.replace('T', ' ').slice(0, 16) : '-'

const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminUsers({ keyword: query.value.keyword || undefined, page: query.value.page, page_size: query.value.page_size })
    userList.value = data.items || []
    total.value = data.total || 0
    // 统计
    const s = { total: data.total || 0, developers: 0, totalBalance: 0 }
    for (const u of userList.value) {
      if (u.is_developer) s.developers++
      s.totalBalance += Number(u.balance || 0)
    }
    stats.value = s
  } finally { loading.value = false }
}
const search = () => { query.value.page = 1; loadList() }

onMounted(loadList)
</script>

<style scoped>
.stats-row { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-card {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 24px; border-radius: 12px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-lighter);
  min-width: 160px; flex: 1; transition: all 0.2s;
}
.stat-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.stat-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.stat-card.total .stat-icon { background: #e6f0ff; }
.stat-card.dev .stat-icon { background: #e8f5e9; }
.stat-card.balance .stat-icon { background: #e6e6fa; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-value small { font-size: 12px; font-weight: 400; color: var(--el-text-color-secondary); }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-note { color: var(--el-text-color-secondary); font-size: 12px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }

.balance-text { font-weight: 600; color: #6366f1; }
.text-muted { color: var(--el-text-color-secondary); font-size: 13px; }

@media (max-width: 768px) {
  .stats-row { gap: 8px; }
  .stat-card { min-width: 100px; padding: 12px; }
  .stat-value { font-size: 18px; }
}
</style>
