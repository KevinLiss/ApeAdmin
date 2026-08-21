<template>
  <div>
    <PageHeader title="项目列表" :breadcrumb="['APEUI库', '应用中心', '项目列表']" />

    <el-card>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
        <el-input
          v-model="search"
          placeholder="搜索项目名称..."
          style="width: 300px"
          clearable
        />
        <el-button type="primary" :icon="Plus">新增项目</el-button>
      </div>

      <el-table :data="filteredData" border stripe>
        <el-table-column prop="name" label="项目名称" min-width="160" />
        <el-table-column prop="client" label="客户" min-width="120" />
        <el-table-column prop="startDate" label="开始日期" min-width="120" />
        <el-table-column prop="endDate" label="结束日期" min-width="120" />
        <el-table-column label="状态" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="team" label="团队" min-width="100" align="center" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface Project {
  name: string
  client: string
  startDate: string
  endDate: string
  status: string
  team: number
}

const search = ref('')

const tableData: Project[] = [
  { name: '网站重设计', client: 'Acme Corp', startDate: '2025-01-15', endDate: '2025-04-30', status: '进行中', team: 5 },
  { name: '移动应用开发', client: 'TechStart', startDate: '2025-02-01', endDate: '2025-08-15', status: '进行中', team: 8 },
  { name: '云迁移', client: 'GlobalSoft', startDate: '2024-11-10', endDate: '2025-03-20', status: '已完成', team: 6 },
  { name: '数据分析平台', client: 'DataFlow Ltd', startDate: '2025-03-01', endDate: '2025-09-01', status: '待处理', team: 4 },
  { name: '电商集成', client: 'ShopHub', startDate: '2025-01-20', endDate: '2025-06-30', status: '已暂停', team: 7 },
]

const filteredData = computed(() => {
  if (!search.value) return tableData
  return tableData.filter((item) =>
    item.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

const statusType = (status: string) => {
  const map: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '待处理': 'warning',
    '已暂停': 'info',
  }
  return map[status] || 'info'
}

const statusLabel = (status: string) => status
</script>

<style scoped>
:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}
</style>
