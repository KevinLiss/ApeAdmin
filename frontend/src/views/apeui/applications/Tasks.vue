<template>
  <div>
    <PageHeader title="任务列表" :breadcrumb="['APEUI库', '应用中心', '任务列表']">
      <template #actions>
        <el-button type="primary" :icon="Plus">新建任务</el-button>
      </template>
    </PageHeader>

    <el-card>
      <!-- 搜索与筛选 -->
      <div class="toolbar">
        <el-input
          v-model="search"
          placeholder="搜索任务名..."
          style="width: 300px"
          clearable
          :prefix-icon="Search"
        />
        <el-select v-model="statusFilter" placeholder="筛选状态" clearable style="width: 160px">
          <el-option label="Pending" value="Pending" />
          <el-option label="In Progress" value="In Progress" />
          <el-option label="Completed" value="Completed" />
          <el-option label="On Hold" value="On Hold" />
        </el-select>
      </div>

      <el-table :data="pagedData" border stripe style="width: 100%">
        <el-table-column prop="name" label="任务名" min-width="180" />
        <el-table-column label="负责人" min-width="140" align="center">
          <template #default="{ row }">
            <div class="owner-cell">
              <el-avatar :size="28" :src="row.avatar" />
              <span>{{ row.owner }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="优先级" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityType(row.priority)" size="small" effect="light">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="dark">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止日期" min-width="120" align="center" />
        <el-table-column label="进度" min-width="160" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :color="progressColor(row.progress)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :icon="Edit" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="filteredData.length"
          :page-sizes="[5, 10, 20]"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editVisible" title="编辑任务" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="任务名">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="editForm.owner" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="editForm.priority" style="width: 100%">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="Pending" value="Pending" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Completed" value="Completed" />
            <el-option label="On Hold" value="On Hold" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="editForm.deadline" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="进度">
          <el-slider v-model="editForm.progress" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface Task {
  id: number
  name: string
  owner: string
  avatar: string
  priority: string
  status: string
  deadline: string
  progress: number
}

const avatarBase = 'https://api.dicebear.com/7.x/avataaars/svg?seed='

const tableData = ref<Task[]>([
  { id: 1, name: '首页 V3 UI 重构', owner: '张伟', avatar: avatarBase + 'zhangwei', priority: '高', status: 'In Progress', deadline: '2026-08-25', progress: 65 },
  { id: 2, name: '用户管理模块开发', owner: '李娜', avatar: avatarBase + 'lina', priority: '高', status: 'In Progress', deadline: '2026-08-28', progress: 40 },
  { id: 3, name: '权限系统重构', owner: '王强', avatar: avatarBase + 'wangqiang', priority: '中', status: 'Pending', deadline: '2026-09-05', progress: 10 },
  { id: 4, name: 'API 文档编写', owner: '陈晨', avatar: avatarBase + 'chenchen', priority: '低', status: 'Pending', deadline: '2026-09-10', progress: 5 },
  { id: 5, name: '项目初始化', owner: '赵敏', avatar: avatarBase + 'zhaomin', priority: '高', status: 'Completed', deadline: '2026-08-10', progress: 100 },
  { id: 6, name: '需求分析报告', owner: '刘洋', avatar: avatarBase + 'liuyang', priority: '中', status: 'Completed', deadline: '2026-08-15', progress: 100 },
  { id: 7, name: '数据库优化方案', owner: '孙莉', avatar: avatarBase + 'sunli', priority: '中', status: 'On Hold', deadline: '2026-09-15', progress: 30 },
  { id: 8, name: '单元测试覆盖', owner: '周杰', avatar: avatarBase + 'zhoujie', priority: '低', status: 'On Hold', deadline: '2026-09-20', progress: 20 },
])

const search = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(5)

const filteredData = computed(() => {
  let list = tableData.value
  if (search.value) {
    list = list.filter((t) => t.name.toLowerCase().includes(search.value.toLowerCase()))
  }
  if (statusFilter.value) {
    list = list.filter((t) => t.status === statusFilter.value)
  }
  return list
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const priorityType = (p: string) => {
  const map: Record<string, string> = { 高: 'danger', 中: 'warning', 低: 'info' }
  return map[p] || 'info'
}

const statusType = (s: string) => {
  const map: Record<string, string> = {
    Pending: 'warning',
    'In Progress': 'primary',
    Completed: 'success',
    'On Hold': 'info',
  }
  return map[s] || 'info'
}

const progressColor = (p: number) => {
  if (p >= 100) return '#67C100'
  if (p >= 50) return '#3EBCB9'
  if (p >= 20) return '#E56809'
  return '#DC0808'
}

// 编辑
const editVisible = ref(false)
const editForm = reactive<Task>({
  id: 0, name: '', owner: '', avatar: '', priority: '中', status: 'Pending', deadline: '', progress: 0,
})

const handleEdit = (row: Task) => {
  Object.assign(editForm, row)
  editVisible.value = true
}

const saveEdit = () => {
  const idx = tableData.value.findIndex((t) => t.id === editForm.id)
  if (idx > -1) {
    tableData.value[idx] = { ...editForm }
  }
  editVisible.value = false
}

const handleDelete = (row: Task) => {
  tableData.value = tableData.value.filter((t) => t.id !== row.id)
}
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
}

.owner-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
  --el-button-active-bg-color: #433a6b;
  --el-button-active-border-color: #433a6b;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #5A67F5;
}
</style>
