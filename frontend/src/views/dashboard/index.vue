<template>
  <div class="dashboard">
    <!-- Page header bar (Koho style) -->
    <div class="page-header-bar">
      <div>
        <h3>仪表盘</h3>
        <small>系统概览与运行状态</small>
      </div>
      <div class="breadcrumb">
        <a href="#/dashboard">首页</a>
        <span class="sep">/</span>
        <span>仪表盘</span>
      </div>
    </div>

    <!-- Stat cards: Koho widget-joins -->
    <div class="widget-joins">
      <div class="widget-card" v-for="card in statCards" :key="card.title">
        <div class="widget-icon">
          <el-icon :size="24" :color="card.color"><component :is="card.icon" /></el-icon>
        </div>
        <div class="widget-body">
          <div class="widget-title">{{ card.title }}</div>
          <h5 class="widget-value">{{ card.value }}</h5>
        </div>
        <div class="icon-bg"><el-icon :size="64"><component :is="card.icon" /></el-icon></div>
      </div>
    </div>

    <!-- Main content -->
    <el-row :gutter="16" class="content-row">
      <el-col :span="14">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <span class="panel-title">系统架构</span>
          </template>
          <div class="arch-item" v-for="layer in archLayers" :key="layer.name">
            <el-tag :type="layer.tag" size="small" class="arch-tag">{{ layer.name }}</el-tag>
            <span class="arch-desc">{{ layer.desc }}</span>
          </div>
        </el-card>
      </el-col>

      <el-col :span="10">
        <el-card shadow="never" class="panel-card">
          <template #header>
            <span class="panel-title">MCP 工具</span>
            <el-button size="small" type="primary" link @click="loadMcpTools">刷新</el-button>
          </template>
          <el-table :data="mcpTools" size="small" v-loading="mcpLoading">
            <el-table-column prop="name" label="工具名" width="160" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getMcpTools } from '@/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const statCards = ref([
  { title: '用户数', value: '—', icon: 'User' },
  { title: '角色数', value: '—', icon: 'UserFilled' },
  { title: '菜单数', value: '—', icon: 'Menu' },
  { title: 'MCP 工具', value: '—', icon: 'Tools' },
])

const archLayers = [
  { name: '接入层', desc: 'REST API + MCP 端点', tag: 'primary' },
  { name: '应用层', desc: 'API 路由 → 依赖注入 → 编排', tag: 'success' },
  { name: '领域层', desc: 'CRUD 引擎 / 插件系统 / MCP 体系', tag: 'warning' },
  { name: '基础设施', desc: 'SQLAlchemy 2.0 / Redis / Alembic', tag: 'info' },
]

const mcpTools = ref<any[]>([])
const mcpLoading = ref(false)

async function loadMcpTools() {
  mcpLoading.value = true
  try {
const data: any = await getMcpTools()
    mcpTools.value = data || []
    statCards.value[3].value = String(mcpTools.value.length)
  } catch {
    mcpTools.value = []
  } finally {
    mcpLoading.value = false
  }
}

onMounted(() => {
  loadMcpTools()
  if (userStore.username) {
    statCards.value[0].value = '已登录'
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}
.content-row {
  margin-top: 4px;
}
.panel-title {
  font-weight: 600;
  color: #303133;
}
.arch-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}
.arch-item:last-child {
  border-bottom: none;
}
.arch-tag {
  width: 86px;
  text-align: center;
}
.arch-desc {
  color: #606266;
  font-size: 13px;
}
</style>