<template>
  <div>
    <PageHeader title="看板视图" :breadcrumb="['APEUI库', '应用中心', '看板视图']">
      <template #actions>
        <el-button type="primary" :icon="Plus" @click="dialogVisible = true">新建任务</el-button>
      </template>
    </PageHeader>

    <el-row :gutter="30">
      <el-col :span="8" v-for="(col, ci) in columns" :key="col.key">
        <div class="kanban-col" :class="col.cls">
          <div class="kanban-col-header">
            <span class="col-title">{{ col.title }}</span>
            <el-badge :value="col.tasks.length" type="primary" />
          </div>
          <draggable
            v-model="col.tasks"
            group="tasks"
            item-key="id"
            handle=".kanban-card"
            class="kanban-list"
            ghost-class="kanban-ghost"
            chosen-class="kanban-chosen"
            drag-class="kanban-dragging"
          >
            <template #item="{ element }">
              <div class="kanban-card">
                <div class="card-top">
                  <el-tag :type="priorityType(element.priority)" size="small" effect="light">
                    {{ element.priority }}
                  </el-tag>
                  <span class="card-date">{{ element.date }}</span>
                </div>
                <div class="card-body">{{ element.title }}</div>
                <div class="card-footer">
                  <el-avatar :size="24" :src="element.avatar" />
                  <span class="card-owner">{{ element.owner }}</span>
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </el-col>
    </el-row>

    <!-- 新建任务对话框 -->
    <el-dialog v-model="dialogVisible" title="新建任务" width="480px">
      <el-form :model="newTask" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="newTask.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-input v-model="newTask.owner" placeholder="请输入负责人姓名" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="newTask.priority" placeholder="请选择优先级" style="width: 100%">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="newTask.date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="所属列">
          <el-select v-model="newTask.column" placeholder="请选择列" style="width: 100%">
            <el-option label="To Do" value="todo" />
            <el-option label="In Progress" value="inProgress" />
            <el-option label="Done" value="done" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addTask">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import PageHeader from '../components/PageHeader.vue'

interface Task {
  id: number
  title: string
  priority: string
  owner: string
  avatar: string
  date: string
}

const avatarBase = 'https://api.dicebear.com/7.x/avataaars/svg?seed='

const columns = reactive([
  {
    key: 'todo',
    title: 'To Do',
    cls: 'col-todo',
    tasks: [
      { id: 1, title: '设计登录页', priority: '高', owner: '张伟', avatar: avatarBase + 'zhangwei', date: '2026-08-25' },
      { id: 2, title: 'API 文档编写', priority: '中', owner: '李娜', avatar: avatarBase + 'lina', date: '2026-08-28' },
      { id: 3, title: '数据库优化', priority: '低', owner: '王强', avatar: avatarBase + 'wangqiang', date: '2026-09-02' },
    ] as Task[],
  },
  {
    key: 'inProgress',
    title: 'In Progress',
    cls: 'col-progress',
    tasks: [
      { id: 4, title: '用户管理模块', priority: '高', owner: '陈晨', avatar: avatarBase + 'chenchen', date: '2026-08-22' },
      { id: 5, title: '权限系统重构', priority: '中', owner: '赵敏', avatar: avatarBase + 'zhaomin', date: '2026-08-30' },
    ] as Task[],
  },
  {
    key: 'done',
    title: 'Done',
    cls: 'col-done',
    tasks: [
      { id: 6, title: '项目初始化', priority: '高', owner: '刘洋', avatar: avatarBase + 'liuyang', date: '2026-08-10' },
      { id: 7, title: '需求分析', priority: '中', owner: '孙莉', avatar: avatarBase + 'sunli', date: '2026-08-15' },
    ] as Task[],
  },
])

const dialogVisible = ref(false)
const newTask = reactive({
  title: '',
  owner: '',
  priority: '中',
  date: '',
  column: 'todo',
})

let nextId = 8

const addTask = () => {
  if (!newTask.title || !newTask.owner) return
  const col = columns.find((c) => c.key === newTask.column)
  if (!col) return
  col.tasks.push({
    id: nextId++,
    title: newTask.title,
    priority: newTask.priority,
    owner: newTask.owner,
    avatar: avatarBase + newTask.owner,
    date: newTask.date || new Date().toISOString().slice(0, 10),
  })
  newTask.title = ''
  newTask.owner = ''
  newTask.priority = '中'
  newTask.date = ''
  newTask.column = 'todo'
  dialogVisible.value = false
}

const priorityType = (p: string) => {
  const map: Record<string, string> = { 高: 'danger', 中: 'warning', 低: 'info' }
  return map[p] || 'info'
}
</script>

<style scoped>
.kanban-col {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #ebeef5;
  border-top: 4px solid #ddd;
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

.col-todo {
  border-top-color: #5A67F5;
}
.col-progress {
  border-top-color: #e56809;
}
.col-done {
  border-top-color: #67c100;
}

.kanban-col-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.col-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.kanban-list {
  flex: 1;
  padding: 12px;
  min-height: 200px;
}

.kanban-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 12px;
  cursor: grab;
  transition: box-shadow 0.2s;
}

.kanban-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.kanban-card:active {
  cursor: grabbing;
}

.kanban-ghost {
  opacity: 0.4;
  border: 2px dashed #5A67F5 !important;
}

.kanban-chosen {
  box-shadow: 0 4px 16px rgba(90, 103, 245, 0.2);
}

.kanban-dragging {
  opacity: 0.9;
  transform: rotate(2deg);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.card-date {
  font-size: 12px;
  color: #999;
}

.card-body {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  margin-bottom: 12px;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-owner {
  font-size: 13px;
  color: #666;
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
</style>
