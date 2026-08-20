<template>
  <div class="dashboard">
    <!-- Stat cards -->
    <el-row :gutter="16" class="stats">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <el-icon :size="36" :color="card.color"><component :is="card.icon" /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-title">{{ card.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main content -->
    <el-row :gutter="16" class="content-row">
      <el-col :span="14">
        <el-card shadow="never" class="panel">
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
        <el-card shadow="never" class="panel">
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
.stats {
  margin-bottom: 16px;
}
.stat-card {
  border-radius: 8px;
}
.stat-content {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 4px;
}
.stat-value {
  font-size: 26px;
  font-weight: 600;
  color: #303133;
}
.stat-title {
  font-size: 13px;
  color: #909399;
}
.panel {
  border-radius: 8px;
}
.panel-title {
  font-weight: 600;
  color: #303133;
}
.arch-layout {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.arch-layout:last-child {
  border-bottom: none;
}
.arch-tag {
  width: 76px;
  text-align: center;
}
.arch-desc {
  color: #606266;
  font-size: 13px;
}
</style>