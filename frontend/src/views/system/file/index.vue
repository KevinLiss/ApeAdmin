<template>
  <el-card shadow="never" class="page-card file-page">
    <div class="toolbar">
      <el-input v-model="keyword" clearable placeholder="搜索当前文件夹" style="width: 240px" @keyup.enter="loadFiles" />
      <el-button type="primary" @click="loadFiles"><el-icon><Search /></el-icon>查询</el-button>
      <div class="toolbar-right">
        <el-button @click="folderDialog = true"><el-icon><FolderAdd /></el-icon>新建文件夹</el-button>
        <el-upload :show-file-list="false" :http-request="handleUpload" :disabled="uploading">
          <el-button type="success" :loading="uploading"><el-icon><Upload /></el-icon>上传文件</el-button>
        </el-upload>
      </div>
    </div>
    <div class="file-layout" v-loading="loading">
      <aside class="folder-panel">
        <div class="panel-title">文件夹</div>
        <el-tree :data="folders" node-key="id" :props="{ label: 'name', children: 'children' }" default-expand-all @node-click="selectFolder" />
      </aside>
      <main class="content-panel">
        <div class="breadcrumb">当前位置：{{ currentFolderName }}</div>
        <el-table :data="files" stripe empty-text="当前文件夹暂无文件">
          <el-table-column label="名称" min-width="260"><template #default="{ row }"><div class="file-name"><el-icon><Document /></el-icon>{{ row.name }}</div></template></el-table-column>
          <el-table-column prop="mime_type" label="类型" width="180" />
          <el-table-column label="大小" width="120"><template #default="{ row }">{{ formatSize(row.size) }}</template></el-table-column>
          <el-table-column prop="created_at" label="上传时间" width="180" />
          <el-table-column label="操作" width="150" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="download(row)">下载</el-button><el-button link type="danger" @click="removeFile(row)">删除</el-button></template></el-table-column>
        </el-table>
        <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="total, prev, pager, next" @change="loadFiles" />
      </main>
    </div>
  </el-card>
  <el-dialog v-model="folderDialog" title="新建文件夹" width="420px">
    <el-input v-model="folderName" maxlength="120" placeholder="请输入文件夹名称" @keyup.enter="createFolder" />
    <template #footer><el-button @click="folderDialog = false">取消</el-button><el-button type="primary" @click="createFolder">创建</el-button></template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, FolderAdd, Upload, Document } from '@element-plus/icons-vue'
import { createFileFolder, deleteSystemFile, getFileFolders, getFiles, uploadSystemFile, downloadSystemFileUrl } from '@/api'

const loading = ref(false); const uploading = ref(false); const folders = ref<any[]>([]); const files = ref<any[]>([])
const folderId = ref(0); const keyword = ref(''); const page = ref(1); const pageSize = ref(20); const total = ref(0)
const folderDialog = ref(false); const folderName = ref('')
const currentFolderName = computed(() => findName(folders.value, folderId.value) || '全部文件')
function findName(nodes: any[], id: number): string { for (const node of nodes) { if (node.id === id) return node.name; const name = findName(node.children || [], id); if (name) return name } return '' }
async function loadFolders() { const data: any = await getFileFolders(); folders.value = data || [] }
async function loadFiles() { loading.value = true; try { const data: any = await getFiles({ folder_id: folderId.value, keyword: keyword.value, page: page.value, page_size: pageSize.value }); files.value = data.items || []; total.value = data.total || 0 } finally { loading.value = false } }
function selectFolder(node: any) { folderId.value = node.id; page.value = 1; loadFiles() }
async function createFolder() { if (!folderName.value.trim()) return ElMessage.warning('请输入文件夹名称'); await createFileFolder({ name: folderName.value, parent_id: folderId.value }); ElMessage.success('创建成功'); folderDialog.value = false; folderName.value = ''; await loadFolders() }
async function handleUpload(options: any) { uploading.value = true; try { await uploadSystemFile(options.file, folderId.value); ElMessage.success('上传成功'); await loadFiles() } finally { uploading.value = false } }
async function download(row: any) { const token = localStorage.getItem('apeadmin_token'); const response = await fetch(downloadSystemFileUrl(row.id), { headers: token ? { Authorization: `Bearer ${token}` } : {} }); if (!response.ok) return ElMessage.error('下载失败'); const blob = await response.blob(); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = row.name; link.click(); URL.revokeObjectURL(link.href) }
async function removeFile(row: any) { await ElMessageBox.confirm(`确认删除「${row.name}」吗？`, '删除确认'); await deleteSystemFile(row.id); ElMessage.success('已删除'); await loadFiles() }
function formatSize(size: number) { if (size < 1024) return `${size} B`; if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`; return `${(size / 1024 / 1024).toFixed(1)} MB` }
onMounted(async () => { await loadFolders(); await loadFiles() })
</script>

<style scoped>
.file-layout { display: flex; min-height: 520px; border-top: 1px solid #ebeef5; }.folder-panel { width: 240px; padding: 18px 12px; border-right: 1px solid #ebeef5; }.panel-title { font-weight: 600; margin-bottom: 12px; }.content-panel { flex: 1; padding: 18px 20px; }.breadcrumb { margin-bottom: 16px; color: #606266; }.file-name { display: flex; align-items: center; gap: 8px; }.toolbar-right { display: flex; gap: 12px; margin-left: auto; }.pagination { margin-top: 18px; justify-content: flex-end; }
</style>
