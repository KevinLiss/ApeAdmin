<template>
  <div>
    <PageHeader title="书签管理" :breadcrumb="['APEUI库', '应用中心', '书签管理']">
      <template #actions>
        <el-button type="primary" :icon="Plus" @click="openAdd">新增书签</el-button>
      </template>
    </PageHeader>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="filter-tabs">
        <el-button
          v-for="cat in categories"
          :key="cat.value"
          :type="activeCategory === cat.value ? 'primary' : ''"
          size="small"
          @click="activeCategory = cat.value"
        >
          {{ cat.label }}
          <span class="cat-count">{{ cat.count }}</span>
        </el-button>
      </div>
    </div>

    <!-- 书签卡片网格 -->
    <el-row :gutter="30">
      <el-col :span="6" v-for="bm in filteredBookmarks" :key="bm.id">
        <div class="bookmark-card" @click="openEdit(bm)">
          <div class="bm-card-header">
            <div class="bm-icon" :style="{ background: bm.color }">
              {{ bm.icon }}
            </div>
            <div class="bm-fav" @click.stop="toggleFav(bm)">
              <el-icon :class="{ 'is-fav': bm.favorited }"><Star /></el-icon>
            </div>
          </div>
          <div class="bm-title">{{ bm.title }}</div>
          <div class="bm-url">{{ bm.url }}</div>
          <div class="bm-desc">{{ bm.description }}</div>
          <div class="bm-footer">
            <el-tag :type="categoryTagType(bm.category)" size="small" effect="light">
              {{ bm.category }}
            </el-tag>
            <div class="bm-actions">
              <el-button :icon="Edit" size="small" circle @click.stop="openEdit(bm)" />
              <el-button :icon="Delete" size="small" type="danger" circle @click.stop="removeBookmark(bm.id)" />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑书签' : '新增书签'" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" placeholder="网站标题" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="editForm.url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="2" placeholder="简短描述" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="editForm.category" style="width: 100%">
            <el-option label="Work" value="Work" />
            <el-option label="Personal" value="Personal" />
            <el-option label="Social" value="Social" />
            <el-option label="Tools" value="Tools" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标字母">
          <el-input v-model="editForm.icon" maxlength="2" style="width: 80px" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBookmark">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Plus, Edit, Delete, Star } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'

interface Bookmark {
  id: number
  title: string
  url: string
  description: string
  category: string
  icon: string
  color: string
  favorited: boolean
}

const bookmarks = ref<Bookmark[]>([
  { id: 1, title: 'GitHub', url: 'https://github.com', description: '全球最大的代码托管平台，协作与版本管理', category: 'Work', icon: 'GH', color: '#24292e', favorited: true },
  { id: 2, title: 'Stack Overflow', url: 'https://stackoverflow.com', description: '开发者问答社区，解决编程疑难杂症', category: 'Work', icon: 'SO', color: '#f48024', favorited: false },
  { id: 3, title: 'Vue.js 官网', url: 'https://vuejs.org', description: 'Vue3 渐进式 JavaScript 框架官方文档', category: 'Tools', icon: 'V', color: '#42b883', favorited: true },
  { id: 4, title: 'Figma', url: 'https://figma.com', description: '在线协作设计工具，原型与界面设计', category: 'Tools', icon: 'Fi', color: '#a259ff', favorited: true },
  { id: 5, title: 'Notion', url: 'https://notion.so', description: '一体化笔记与知识库管理工具', category: 'Personal', icon: 'No', color: '#000000', favorited: false },
  { id: 6, title: 'Twitter / X', url: 'https://twitter.com', description: '社交媒体平台，关注技术动态与社区', category: 'Social', icon: 'X', color: '#1d9bf0', favorited: false },
  { id: 7, title: 'MDN Web Docs', url: 'https://developer.mozilla.org', description: 'Web 开发权威文档，HTML/CSS/JS 参考', category: 'Work', icon: 'MD', color: '#005ca9', favorited: true },
  { id: 8, title: 'Element Plus', url: 'https://element-plus.org', description: 'Vue3 UI 组件库，企业级后台组件', category: 'Tools', icon: 'EP', color: '#5A67F5', favorited: true },
])

const activeCategory = ref('All')

const categories = computed(() => {
  const cats = ['All', 'Work', 'Personal', 'Social', 'Tools']
  return cats.map((c) => ({
    label: c,
    value: c,
    count: c === 'All' ? bookmarks.value.length : bookmarks.value.filter((b) => b.category === c).length,
  }))
})

const filteredBookmarks = computed(() => {
  if (activeCategory.value === 'All') return bookmarks.value
  return bookmarks.value.filter((b) => b.category === activeCategory.value)
})

const categoryTagType = (cat: string) => {
  const map: Record<string, string> = {
    Work: 'primary',
    Personal: 'success',
    Social: 'warning',
    Tools: 'info',
  }
  return map[cat] || 'info'
}

const toggleFav = (bm: Bookmark) => {
  bm.favorited = !bm.favorited
}

const removeBookmark = (id: number) => {
  bookmarks.value = bookmarks.value.filter((b) => b.id !== id)
}

// 编辑/新增
const dialogVisible = ref(false)
const editingId = ref(0)
const editForm = reactive({
  title: '',
  url: '',
  description: '',
  category: 'Work',
  icon: '',
})
let nextId = 9

const openAdd = () => {
  editingId.value = 0
  editForm.title = ''
  editForm.url = ''
  editForm.description = ''
  editForm.category = 'Work'
  editForm.icon = ''
  dialogVisible.value = true
}

const openEdit = (bm: Bookmark) => {
  editingId.value = bm.id
  editForm.title = bm.title
  editForm.url = bm.url
  editForm.description = bm.description
  editForm.category = bm.category
  editForm.icon = bm.icon
  dialogVisible.value = true
}

const saveBookmark = () => {
  if (!editForm.title || !editForm.url) return
  if (editingId.value) {
    const idx = bookmarks.value.findIndex((b) => b.id === editingId.value)
    if (idx > -1) {
      bookmarks.value[idx] = {
        ...bookmarks.value[idx],
        title: editForm.title,
        url: editForm.url,
        description: editForm.description,
        category: editForm.category,
        icon: editForm.icon || editForm.title.substring(0, 2).toUpperCase(),
      }
    }
  } else {
    bookmarks.value.push({
      id: nextId++,
      title: editForm.title,
      url: editForm.url,
      description: editForm.description,
      category: editForm.category,
      icon: editForm.icon || editForm.title.substring(0, 2).toUpperCase(),
      color: '#5A67F5',
      favorited: false,
    })
  }
  dialogVisible.value = false
}
</script>

<style scoped>
.toolbar {
  margin-bottom: 20px;
}

.filter-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.cat-count {
  margin-left: 6px;
  font-size: 12px;
  opacity: 0.7;
}

.bookmark-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 30px;
  cursor: pointer;
  transition: box-shadow 0.25s, transform 0.25s;
}

.bookmark-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.bm-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.bm-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
}

.bm-fav {
  cursor: pointer;
  font-size: 22px;
}

.bm-fav .el-icon {
  color: #ccc;
  transition: color 0.2s;
}

.bm-fav .el-icon.is-fav {
  color: #e56809;
}

.bm-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.bm-url {
  font-size: 13px;
  color: #5A67F5;
  margin-bottom: 8px;
  word-break: break-all;
}

.bm-desc {
  font-size: 13px;
  color: #888;
  line-height: 1.5;
  margin-bottom: 14px;
  min-height: 40px;
}

.bm-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.bm-actions {
  display: flex;
  gap: 8px;
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
