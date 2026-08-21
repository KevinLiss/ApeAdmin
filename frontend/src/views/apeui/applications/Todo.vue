<template>
  <div>
    <PageHeader title="待办事项" :breadcrumb="['APEUI库', '应用中心', '待办事项']" />

    <el-row :gutter="30">
      <!-- 左侧分类 -->
      <el-col :span="6">
        <el-card>
          <template #header>
            <span class="card-title">分类</span>
          </template>
          <div
            v-for="cat in categories"
            :key="cat.key"
            class="cat-item"
            :class="{ active: activeCat === cat.key }"
            @click="activeCat = cat.key"
          >
            <div class="cat-left">
              <el-icon v-if="cat.icon"><component :is="cat.icon" /></el-icon>
              <span>{{ cat.label }}</span>
            </div>
            <el-badge :value="cat.count()" type="primary" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧待办列表 -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <span class="card-title">{{ activeCatLabel }}</span>
          </template>

          <!-- 添加待办 -->
          <div class="add-bar">
            <el-input
              v-model="newTodo"
              placeholder="添加待办事项..."
              style="flex: 1"
              @keyup.enter="addTodo"
            />
            <el-select v-model="newPriority" placeholder="优先级" style="width: 120px">
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
            </el-select>
            <el-button type="primary" :icon="Plus" @click="addTodo">添加</el-button>
          </div>

          <!-- 待办列表 -->
          <div class="todo-list">
            <div v-for="item in filteredTodos" :key="item.id" class="todo-item">
              <el-checkbox
                v-model="item.done"
                :class="{ 'done-text': item.done }"
                size="large"
              >
                <span class="todo-name" :class="{ 'done-text': item.done }">{{ item.name }}</span>
              </el-checkbox>
              <div class="todo-meta">
                <el-tag :type="priorityType(item.priority)" size="small" effect="light">
                  {{ item.priority }}
                </el-tag>
                <span class="todo-date">{{ item.date }}</span>
                <el-button
                  type="danger"
                  :icon="Delete"
                  size="small"
                  circle
                  @click="removeTodo(item.id)"
                />
              </div>
            </div>
            <el-empty v-if="filteredTodos.length === 0" description="暂无待办事项" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Delete, Files, Calendar, Star, CircleCheck } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface TodoItem {
  id: number
  name: string
  priority: string
  date: string
  done: boolean
  important: boolean
}

const todos = ref<TodoItem[]>([
  { id: 1, name: '完成首页 V3 UI 重构', priority: '高', date: '2026-08-25', done: false, important: true },
  { id: 2, name: '审阅用户管理模块代码', priority: '中', date: '2026-08-24', done: false, important: false },
  { id: 3, name: '编写权限系统设计文档', priority: '高', date: '2026-08-26', done: false, important: true },
  { id: 4, name: '部署测试环境', priority: '中', date: '2026-08-23', done: true, important: false },
  { id: 5, name: '回复客户邮件', priority: '低', date: '2026-08-21', done: false, important: false },
  { id: 6, name: '整理本周会议纪要', priority: '低', date: '2026-08-22', done: true, important: false },
  { id: 7, name: '安排下周技术分享会', priority: '中', date: '2026-08-27', done: false, important: false },
  { id: 8, name: '更新项目进度看板', priority: '高', date: '2026-08-23', done: false, important: true },
])

const activeCat = ref('all')
const newTodo = ref('')
const newPriority = ref('中')
let nextId = 9

const todayStr = new Date().toISOString().slice(0, 10)

const categories = computed(() => [
  { key: 'all', label: '全部', icon: Files, count: () => todos.value.length },
  { key: 'today', label: '今日', icon: Calendar, count: () => todos.value.filter((t) => t.date === todayStr).length },
  { key: 'important', label: '重要', icon: Star, count: () => todos.value.filter((t) => t.important).length },
  { key: 'done', label: '已完成', icon: CircleCheck, count: () => todos.value.filter((t) => t.done).length },
])

const activeCatLabel = computed(() => {
  const c = categories.value.find((c) => c.key === activeCat.value)
  return c ? c.label + ' 待办' : '全部待办'
})

const filteredTodos = computed(() => {
  switch (activeCat.value) {
    case 'today':
      return todos.value.filter((t) => t.date === todayStr)
    case 'important':
      return todos.value.filter((t) => t.important)
    case 'done':
      return todos.value.filter((t) => t.done)
    default:
      return todos.value
  }
})

const addTodo = () => {
  if (!newTodo.value.trim()) return
  todos.value.unshift({
    id: nextId++,
    name: newTodo.value,
    priority: newPriority.value,
    date: todayStr,
    done: false,
    important: false,
  })
  newTodo.value = ''
  newPriority.value = '中'
}

const removeTodo = (id: number) => {
  todos.value = todos.value.filter((t) => t.id !== id)
}

const priorityType = (p: string) => {
  const map: Record<string, string> = { 高: 'danger', 中: 'warning', 低: 'info' }
  return map[p] || 'info'
}
</script>

<style scoped>
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #5A67F5;
}

.cat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.cat-item:hover {
  background: #f5f3f9;
}

.cat-item.active {
  background: #edeaf4;
  color: #5A67F5;
  font-weight: 600;
}

.cat-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.todo-list {
  max-height: 500px;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 8px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.2s;
}

.todo-item:hover {
  background: #fafafa;
}

.todo-name {
  font-size: 14px;
  color: #333;
}

.done-text {
  text-decoration: line-through;
  color: #bbb !important;
}

.todo-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.todo-date {
  font-size: 13px;
  color: #999;
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
