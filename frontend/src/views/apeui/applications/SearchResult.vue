<template>
  <div class="search-result">
    <PageHeader title="Search Result" :breadcrumb="['APEUI库', 'Applications', 'Search Result']" />

    <!-- Search Bar -->
    <div class="koho-card search-card">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="Search anything..."
          :prefix-icon="Search"
          size="large"
          clearable
          class="search-input"
        />
        <el-button type="primary" size="large" :icon="Search" @click="onSearch">Search</el-button>
      </div>
      <!-- Filter Tabs -->
      <div class="filter-tabs">
        <el-radio-group v-model="activeFilter" @change="onFilterChange">
          <el-radio-button label="all">All ({{ totalResults }})</el-radio-button>
          <el-radio-button label="posts">Posts ({{ typeCounts.posts }})</el-radio-button>
          <el-radio-button label="users">Users ({{ typeCounts.users }})</el-radio-button>
          <el-radio-button label="images">Images ({{ typeCounts.images }})</el-radio-button>
          <el-radio-button label="files">Files ({{ typeCounts.files }})</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-row :gutter="30">
      <!-- Left: Filter Panel -->
      <el-col :xs="24" :sm="6">
        <div class="koho-card">
          <div class="card-title">
            <el-icon><Filter /></el-icon>
            <span>Filters</span>
          </div>

          <!-- Time Range -->
          <div class="filter-group">
            <div class="filter-label">Time Range</div>
            <el-select v-model="filters.timeRange" placeholder="Any time" style="width: 100%">
              <el-option label="Any time" value="any" />
              <el-option label="Past 24 hours" value="24h" />
              <el-option label="Past week" value="week" />
              <el-option label="Past month" value="month" />
              <el-option label="Past year" value="year" />
            </el-select>
          </div>

          <!-- Type -->
          <div class="filter-group">
            <div class="filter-label">Type</div>
            <el-select v-model="filters.type" placeholder="All types" style="width: 100%">
              <el-option label="All types" value="" />
              <el-option label="Post" value="posts" />
              <el-option label="User" value="users" />
              <el-option label="Image" value="images" />
              <el-option label="File" value="files" />
            </el-select>
          </div>

          <!-- Sort -->
          <div class="filter-group">
            <div class="filter-label">Sort By</div>
            <el-select v-model="filters.sort" placeholder="Relevance" style="width: 100%">
              <el-option label="Relevance" value="relevance" />
              <el-option label="Newest first" value="newest" />
              <el-option label="Oldest first" value="oldest" />
              <el-option label="Most viewed" value="views" />
            </el-select>
          </div>

          <el-button type="primary" plain style="width: 100%; margin-top: 8px" @click="onResetFilters">Reset Filters</el-button>
        </div>
      </el-col>

      <!-- Center: Results -->
      <el-col :xs="24" :sm="12">
        <div class="results-container">
          <div class="results-count">
            About {{ totalResults }} results for "<span class="highlight">{{ searchQuery || 'all' }}</span>"
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
            <span>Statistics</span>
          </div>
          <div class="stat-total">
            <div class="stat-number">{{ totalResults }}</div>
            <div class="stat-label">Total Results</div>
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

const searchQuery = ref('Vue3 components')
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
  { label: 'Posts', count: 18, percent: 75, color: '#534686', icon: Document },
  { label: 'Images', count: 9, percent: 38, color: '#3EBCB9', icon: Picture },
  { label: 'Users', count: 6, percent: 25, color: '#67C100', icon: User },
  { label: 'Files', count: 5, percent: 21, color: '#E56809', icon: Files },
]

const results = ref([
  {
    id: 1, type: 'posts', typeLabel: 'Post', tagType: 'primary' as const,
    title: 'Building Reusable Components in Vue 3 — A Complete Guide',
    url: 'https://vuejs.org/guide/components',
    summary: 'Learn how to build reusable, maintainable components in Vue 3 using Composition API, defineModel, and provide/inject patterns. This comprehensive guide covers props, emits, slots, and best practices.',
    tags: ['Vue3', 'Components', 'Composition API'],
  },
  {
    id: 2, type: 'posts', typeLabel: 'Post', tagType: 'primary' as const,
    title: 'Element Plus vs Ant Design Vue: Which UI Library to Choose in 2025?',
    url: 'https://element-plus.org/blog',
    summary: 'A detailed comparison of the two most popular Vue 3 UI component libraries, covering bundle size, accessibility, component coverage, and developer experience.',
    tags: ['Element Plus', 'Ant Design', 'Comparison'],
  },
  {
    id: 3, type: 'users', typeLabel: 'User', tagType: 'success' as const,
    title: 'Evan You — Creator of Vue.js',
    url: 'https://github.com/yyx990803',
    summary: 'Evan You is the creator of Vue.js and Vite. He has been working on open-source JavaScript frameworks and tooling since 2013.',
    tags: ['JavaScript', 'Open Source', 'Vue'],
  },
  {
    id: 4, type: 'posts', typeLabel: 'Post', tagType: 'primary' as const,
    title: 'State Management in Vue 3: Pinia vs Vuex 5',
    url: 'https://pinia.vuejs.org',
    summary: 'Pinia is the official state management solution for Vue. It offers a simpler API, better TypeScript support, and removes mutations from the equation entirely.',
    tags: ['Pinia', 'Vuex', 'State Management'],
  },
  {
    id: 5, type: 'images', typeLabel: 'Image', tagType: 'info' as const,
    title: 'Vue 3 Component Architecture Diagram',
    url: 'https://figma.com/vue3-architecture',
    summary: 'A visual representation of Vue 3 component lifecycle, reactivity system, and rendering pipeline. Useful for onboarding new developers.',
    tags: ['Diagram', 'Architecture', 'Visualization'],
  },
  {
    id: 6, type: 'files', typeLabel: 'File', tagType: 'warning' as const,
    title: 'vue3-starter-template.zip — Production Ready Starter Kit',
    url: 'https://github.com/vue3/starter',
    summary: 'A production-ready Vue 3 starter template with Vite, Pinia, Vue Router, Element Plus, and pre-configured ESLint + Prettier.',
    tags: ['Template', 'Vite', 'Starter Kit'],
  },
  {
    id: 7, type: 'posts', typeLabel: 'Post', tagType: 'primary' as const,
    title: 'Composition API Deep Dive: ref, reactive, computed, and watch',
    url: 'https://vuejs.org/guide/reactivity',
    summary: 'Master the Vue 3 Composition API with practical examples. Understand when to use ref vs reactive, how computed caching works, and watch strategies.',
    tags: ['Composition API', 'Reactivity', 'Tutorial'],
  },
  {
    id: 8, type: 'users', typeLabel: 'User', tagType: 'success' as const,
    title: 'Sarah Drasner — Vue Core Team Member',
    url: 'https://github.com/sdras',
    summary: 'Sarah Drasner is a member of the Vue core team, author of SVG Animations, and a prominent speaker in the frontend community.',
    tags: ['Vue Core', 'SVG', 'Animation'],
  },
])

const filteredResults = computed(() => {
  if (activeFilter.value === 'all') return results.value
  return results.value.filter(r => r.type === activeFilter.value)
})

const onSearch = () => ElMessage.success(`Searching for "${searchQuery.value}"`)
const onFilterChange = (val: string) => {
  currentPage.value = 1
  ElMessage.info(`Filter: ${val}`)
}
const onResetFilters = () => {
  filters.value = { timeRange: 'any', type: '', sort: 'relevance' }
  activeFilter.value = 'all'
  ElMessage.success('Filters reset')
}
const onResultClick = (result: any) => ElMessage.info(`Opening: ${result.title}`)
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
  color: #534686;
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
.highlight { color: #534686; font-weight: 600; }
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
  color: #534686;
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
  color: #534686;
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
  --el-color-primary: #534686;
  --el-button-bg-color: #534686;
  --el-button-border-color: #534686;
  --el-button-hover-bg-color: #6b5c9e;
  --el-button-hover-border-color: #6b5c9e;
}
:deep(.el-radio-button__inner) {
  --el-color-primary: #534686;
}
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #534686;
  border-color: #534686;
  box-shadow: -1px 0 0 0 #534686;
}
</style>
