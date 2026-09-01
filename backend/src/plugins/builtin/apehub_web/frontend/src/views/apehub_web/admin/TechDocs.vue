<template>
  <el-card shadow="never">
  <template #header>
    <div class="card-header">
      <span>技术文档管理</span>
      <el-button type="primary" size="small" @click="openPreview">访问文档门户</el-button>
    </div>
  </template>

  <div class="tech-docs-layout">
    <!-- 左侧文件列表 -->
    <div class="file-sidebar">
      <el-input v-model="searchKey" placeholder="搜索文件名" clearable size="small" style="margin-bottom: 12px" />
      <div v-for="cat in filteredCategories" :key="cat.name" style="margin-bottom: 16px">
        <div class="cat-title">{{ cat.name }}</div>
        <div
          v-for="f in cat.files"
          :key="f.path"
          class="file-item"
          :class="{ active: currentFile === f.path }"
          @click="loadFile(f.path)"
        >
          <el-icon><Document /></el-icon>
          <span>{{ f.name }}</span>
        </div>
      </div>
    </div>

    <!-- 右侧编辑器 -->
    <div class="editor-area">
      <template v-if="currentFile">
        <div class="editor-header">
          <span class="file-path">{{ currentFile }}</span>
          <el-button type="primary" size="small" :loading="saving" @click="handleSave">保存</el-button>
        </div>
        <el-input
          v-model="fileContent"
          type="textarea"
          :rows="28"
          placeholder="Markdown 内容"
          class="md-editor"
          resize="none"
        />
      </template>
      <div v-else class="empty-hint">
        <el-icon :size="48" color="#c0c4cc"><Document /></el-icon>
        <p>从左侧选择一个 Markdown 文件进行编辑</p>
      </div>
    </div>
  </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { getTechDocs, readTechDoc, saveTechDoc } from '@/api/apehub_web'

interface TechDocFile {
  path: string
  name: string
  category: string
  size: number
  modified: string
}

const fileList = ref<TechDocFile[]>([])
const searchKey = ref('')
const currentFile = ref('')
const fileContent = ref('')
const loading = ref(false)
const saving = ref(false)

const categories = computed(() => {
  const groups: Record<string, TechDocFile[]> = {}
  for (const f of fileList.value) {
    if (!groups[f.category]) groups[f.category] = []
    groups[f.category].push(f)
  }
  return Object.entries(groups).map(([name, files]) => ({ name, files }))
})

const filteredCategories = computed(() => {
  if (!searchKey.value) return categories.value
  const key = searchKey.value.toLowerCase()
  return categories.value
    .map(c => ({ ...c, files: c.files.filter(f => f.name.toLowerCase().includes(key) || f.path.toLowerCase().includes(key)) }))
    .filter(c => c.files.length > 0)
})

const loadList = async () => {
  loading.value = true
  try {
    fileList.value = await getTechDocs()
  } finally { loading.value = false }
}

const loadFile = async (path: string) => {
  try {
    const data = await readTechDoc(path)
    currentFile.value = path
    fileContent.value = data.content
  } catch { /* */ }
}

const handleSave = async () => {
  saving.value = true
  try {
    await saveTechDoc(currentFile.value, { content: fileContent.value })
    ElMessage.success('保存成功')
  } finally { saving.value = false }
}

const openPreview = () => {
  window.open('/apehub-web/docs-portal/', '_blank')
}

onMounted(loadList)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.tech-docs-layout { display: flex; gap: 16px; min-height: 600px; }
.file-sidebar { width: 220px; border-right: 1px solid var(--el-border-color-lighter); padding-right: 12px; flex-shrink: 0; }
.cat-title { font-size: 13px; font-weight: 600; color: var(--el-text-color-secondary); margin-bottom: 6px; text-transform: uppercase; }
.file-item { display: flex; align-items: center; gap: 6px; padding: 6px 10px; cursor: pointer; border-radius: 4px; font-size: 13px; }
.file-item:hover { background: var(--el-fill-color-light); }
.file-item.active { background: var(--el-color-primary-light-9); color: var(--el-color-primary); }
.editor-area { flex: 1; display: flex; flex-direction: column; }
.editor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.file-path { font-size: 13px; color: var(--el-text-color-secondary); font-family: monospace; }
.md-editor :deep(.el-textarea__inner) { font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace; font-size: 13px; line-height: 1.6; }
.empty-hint { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--el-text-color-placeholder); }
</style>
