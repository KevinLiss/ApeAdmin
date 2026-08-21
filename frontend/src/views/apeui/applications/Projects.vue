<template>
  <div>
    <PageHeader title="Project List" :breadcrumb="['APEUI库', 'Applications', 'Project List']" />

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
        <el-table-column prop="name" label="Project Name" min-width="160" />
        <el-table-column prop="client" label="Client" min-width="120" />
        <el-table-column prop="startDate" label="Start Date" min-width="120" />
        <el-table-column prop="endDate" label="End Date" min-width="120" />
        <el-table-column label="Status" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="team" label="Team" min-width="100" align="center" />
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
  { name: 'Website Redesign', client: 'Acme Corp', startDate: '2025-01-15', endDate: '2025-04-30', status: 'Ongoing', team: 5 },
  { name: 'Mobile App Development', client: 'TechStart', startDate: '2025-02-01', endDate: '2025-08-15', status: 'Ongoing', team: 8 },
  { name: 'Cloud Migration', client: 'GlobalSoft', startDate: '2024-11-10', endDate: '2025-03-20', status: 'Completed', team: 6 },
  { name: 'Data Analytics Platform', client: 'DataFlow Ltd', startDate: '2025-03-01', endDate: '2025-09-01', status: 'Pending', team: 4 },
  { name: 'E-commerce Integration', client: 'ShopHub', startDate: '2025-01-20', endDate: '2025-06-30', status: 'On Hold', team: 7 },
]

const filteredData = computed(() => {
  if (!search.value) return tableData
  return tableData.filter((item) =>
    item.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

const statusType = (status: string) => {
  const map: Record<string, string> = {
    Ongoing: 'primary',
    Completed: 'success',
    Pending: 'warning',
    'On Hold': 'info',
  }
  return map[status] || 'info'
}
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
