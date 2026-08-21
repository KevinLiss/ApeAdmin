<template>
  <div class="search-result">
    <PageHeader title="搜索结果" :breadcrumb="['APEUI库', '应用中心', '搜索结果']" />

    <!-- Search Bar -->
    <div class="koho-card search-card">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索任意内容..."
          :prefix-icon="Search"
          size="large"
          clearable
          class="search-input"
        />
        <el-button type="primary" size="large" :icon="Search" @click="onSearch">搜索</el-button>
      </div>
      <!-- Filter Tabs -->
      <div class="filter-tabs">
        <el-radio-group v-model="activeFilter" @change="onFilterChange">
          <el-radio-button label="all">全部 ({{ totalResults }})</el-radio-button>
          <el-radio-button label="posts">文章 ({{ typeCounts.posts }})</el-radio-button>
          <el-radio-button label="users">用户 ({{ typeCounts.users }})</el-radio-button>
          <el-radio-button label="images">图片 ({{ typeCounts.images }})</el-radio-button>
          <el-radio-button label="files">文件 ({{ typeCounts.files }})</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-row :gutter="30">
      <!-- Left: Filter Panel -->
      <el-col :xs="24" :sm="6">
        <div class="koho-card">
          <div class="card-title">
            <el-icon><Filter /></el-icon>
            <span>筛选条件</span>
          </div>

          <!-- Time Range -->
          <div class="filter-group">
            <div class="filter-label">时间范围</div>
            <el-select v-model="filters.timeRange" placeholder="任意时间" style="width: 100%">
              <el-option label="任意时间" value="any" />
              <el-option label="过去 24 小时" value="24h" />
              <el-option label="过去一周" value="week" />
              <el-option label="过去一个月" value="month" />
              <el-option label="过去一年" value="year" />
            </el-select>
          </div>

          <!-- Type -->
          <div class="filter-group">
            <div class="filter-label">类型</div>
            <el-select v-model="filters.type" placeholder="全部类型" style="width: 100%">
              <el-option label="全部类型" value="" />
              <el-option label="文章" value="posts" />
              <el-option label="用户" value="users" />
              <el-option label="图片" value="images" />
              <el-option label="文件" value="files" />
            </el-select>
          </div>

          <!-- Sort -->
          <div class="filter-group">
            <div class="filter-label">排序方式</div>
            <el-select v-model="filters.sort" placeholder="相关度" style="width: 100%">
              <el-option label="相关度" value="relevance" />
              <el-option label="最新优先" value="newest" />
              <el-option label="最早优先" value="oldest" />
              <el-option label="最多浏览" value="views" />
            </el-select>
          </div>

          <el-button type="primary" plain style="width: 100%; margin-top: 8px" @click="onResetFilters">重置筛选</el-button>
        </div>
      </el-col>

      <!-- Center: Results -->
      <el-col :xs="24" :sm="12">
        <div class="results-container">
          <div class="results-count">
            共找到 {{ totalResults }} 条关于 "<span class="highlight">{{ searchQuery || '全部' }}</span>" 的结果
          </div>
          <div v-for="result in filteredResults" :key="result.id" class="result-item" @click="onResultClick(result)">
            <div class="result-header">
              <el-tag :type="result.tagType" size="small" round>{{ result.typeLabel }}</el-tag>
              <a class="result-url" href="javascript:void(0)">{{ result.url }}</a>
            </div>
            <h3 class="result-title">{{ result.title }}</h3>
            <p class="result-summary">{{ result.summary }}</p>
            <div class="result-tags">
              <el-tag v-for="tag in result.tags" :key="tag" size="small" effect="plain">{{ tag }}</el-tag>
            </div>
          </div>
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="8"
            :total="totalResults"
            layout="prev, pager, next"
            background
            class="results-pagination"
          />
        </div>
      </el-col>

      <!-- Right: Statistics -->
      <el-col :xs="24" :sm="6">
        <div class="koho-card">
          <div class="card-title">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据统计</span>
          </div>
          <div class="stat-total">
            <div class="stat-number">{{ totalResults }}</div>
            <div class="stat-label">结果总数</div>
          </div>
          <div class="stat-breakdown">
            <div v-for="item in breakdown" :key="item.label" class="stat-row">
              <div class="stat-row-label">
                <el-icon :size="16" :style="{ color: item.color }"><component :is="item.icon" /></el-icon>
                <span>{{ item.label }}</span>
              </div>
              <div class="stat-row-bar">
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: item.percent + '%', background: item.color }"></div>
                </div>
              </div>
              <div class="stat-row-value">{{ item.count }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Search, Filter, DataAnalysis, Document, User, Picture, Files,
} from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

const searchQuery = ref('Vue3 组件')
const activeFilter = ref('all')
const currentPage = ref(1)

const filters = ref({
  timeRange: 'any',
  type: '',
  sort: 'relevance',
})

const typeCounts = { posts: 18, users: 6, images: 9, files: 5 }
const totalResults = 38

const breakdown = [
  { label: '文章', count: 18, percent: 75, color: '#5A67F5', icon: Document },
  { label: '图片', count: 9, percent: 38, color: '#3EBCB9', icon: Picture },
  { label: '用户', count: 6, percent: 25, color: '#67C100', icon: User },
  { label: '文件', count: 5, percent: 21, color: '#E56809', icon: Files },
]

const results = ref([
  {
    id: 1, type: 'posts', typeLabel: '文章', tagType: 'primary' as const,
    title: 'Vue 3 可复用组件构建完整指南',
    url: 'https://vuejs.org/guide/components',
    summary: '学习如何使用 Composition API、defineModel 以及 provide/inject 模式在 Vue 3 中构建可复用、易维护的组件。本指南涵盖 props、emits、插槽及最佳实践。',
    tags: ['Vue3', '组件', '组合式 API'],
  },
  {
    id: 2, type: 'posts', typeLabel: '文章', tagType: 'primary' as const,
    title: 'Element Plus 对比 Ant Design Vue：2025 年如何选择 UI 组件库？',
    url: 'https://element-plus.org/blog',
    summary: '对 Vue 3 两大主流 UI 组件库的详细对比，涵盖包体积、无障碍支持、组件覆盖面和开发体验。',
    tags: ['Element Plus', 'Ant Design', '对比'],
  },
  {
    id: 3, type: 'users', typeLabel: '用户', tagType: 'success' as const,
    title: '尤雨溪 — Vue.js 创始人',
    url: 'https://github.com/yyx990803',
    summary: '尤雨溪是 Vue.js 与 Vite 的创始人，自 2013 年起一直从事开源 JavaScript 框架与工具的开发。',
    tags: ['JavaScript', '开源', 'Vue'],
  },
  {
    id: 4, type: 'posts', typeLabel: '文章', tagType: 'primary' as const,
    title: 'Vue 3 状态管理：Pinia 与 Vuex 5 对比',
    url: 'https://pinia.vuejs.org',
    summary: 'Pinia 是 Vue 官方状态管理方案，提供更简洁的 API 与更好的 TypeScript 支持，并彻底移除了 mutations 概念。',
    tags: ['Pinia', 'Vuex', '状态管理'],
  },
  {
    id: 5, type: 'images', typeLabel: '图片', tagType: 'info' as const,
    title: 'Vue 3 组件架构示意图',
    url: 'https://figma.com/vue3-architecture',
    summary: 'Vue 3 组件生命周期、响应式系统与渲染管线的可视化示意，便于新开发者快速上手。',
    tags: ['示意图', '架构', '可视化'],
  },
  {
    id: 6, type: 'files', typeLabel: '文件', tagType: 'warning' as const,
    title: 'vue3-starter-template.zip — 生产级启动模板',
    url: 'https://github.com/vue3/starter',
    summary: '基于 Vite、Pinia、Vue Router、Element Plus 的生产级 Vue 3 启动模板，并预配置 ESLint 与 Prettier。',
    tags: ['模板', 'Vite', '启动套件'],
  },
  {
    id: 7, type: 'posts', typeLabel: '文章', tagType: 'primary' as const,
    title: '组合式 API 深入解析：ref、reactive、computed 与 watch',
    url: 'https://vuejs.org/guide/reactivity',
    summary: '通过实际示例掌握 Vue 3 组合式 API。理解 ref 与 reactive 的使用场景、computed 缓存机制以及 watch 策略。',
    tags: ['组合式 API', '响应式', '教程'],
  },
  {
    id: 8, type: 'users', typeLabel: '用户', tagType: 'success' as const,
    title: 'Sarah Drasner — Vue 核心团队成员',
    url: 'https://github.com/sdras',
    summary: 'Sarah Drasner 是 Vue 核心团队成员、《SVG Animations》作者，也是前端社区知名演讲者。',
    tags: ['Vue 核心', 'SVG', '动画'],
  },
])

const filteredResults = computed(() => {
  if (activeFilter.value === 'all') return results.value
  return results.value.filter(r => r.type === activeFilter.value)
})

const onSearch = () => ElMessage.success(`正在搜索："${searchQuery.value}"`)
const onFilterChange = (val: string) => {
  currentPage.value = 1
  ElMessage.info(`筛选条件：${val}`)
}
const onResetFilters = () => {
  filters.value = { timeRange: 'any', type: '', sort: 'relevance' }
  activeFilter.value = 'all'
  ElMessage.success('筛选已重置')
}
const onResultClick = (result: any) => ElMessage.info(`打开：${result.title}`)
</script>

<style scoped>
.koho-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 0 20px rgba(8, 21, 66, 0.05);
  margin-bottom: 30px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin-bottom: 16px;
}
.card-title .el-icon { font-size: 20px; }

.search-card { margin-bottom: 24px; }
.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.search-input { flex: 1; }
.filter-tabs { margin-top: 8px; }

/* Filter Panel */
.filter-group { margin-bottom: 20px; }
.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}

/* Results */
.results-container { min-height: 400px; }
.results-count {
  font-size: 14px;
  color: #909399;
  margin-bottom: 16px;
}
.highlight { color: #5A67F5; font-weight: 600; }
.result-item {
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: padding 0.2s;
}
.result-item:hover {
  padding-left: 12px;
}
.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}
.result-url {
  font-size: 13px;
  color: #3EBCB9;
  text-decoration: none;
}
.result-url:hover { text-decoration: underline; }
.result-title {
  font-size: 18px;
  font-weight: 500;
  color: #5A67F5;
  margin: 0 0 8px 0;
  cursor: pointer;
}
.result-item:hover .result-title { text-decoration: underline; }
.result-summary {
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
  margin: 0 0 10px 0;
}
.result-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.results-pagination {
  margin-top: 24px;
  justify-content: center;
}

/* Statistics */
.stat-total {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 20px;
}
.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #5A67F5;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
.stat-breakdown { display: flex; flex-direction: column; gap: 16px; }
.stat-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.stat-row-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #2b2b2b;
  width: 70px;
}
.stat-row-bar { flex: 1; }
.bar-track {
  height: 6px;
  background: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}
.stat-row-value {
  font-size: 14px;
  font-weight: 600;
  color: #2b2b2b;
  width: 30px;
  text-align: right;
}

:deep(.el-button--primary) {
  --el-color-primary: #5A67F5;
  --el-button-bg-color: #5A67F5;
  --el-button-border-color: #5A67F5;
  --el-button-hover-bg-color: #4F58E8;
  --el-button-hover-border-color: #4F58E8;
}
:deep(.el-radio-button__inner) {
  --el-color-primary: #5A67F5;
}
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #5A67F5;
  border-color: #5A67F5;
  box-shadow: -1px 0 0 0 #5A67F5;
}
</style>
