<template>
  <section class="file-page">
    <header class="page-heading">
      <div><p class="eyebrow">SYSTEM STORAGE</p><h1>文件管理</h1><p class="heading-copy">集中管理系统上传文件与目录</p></div>
      <div class="heading-stats"><span><strong>{{ total }}</strong> 个文件</span><i></i><span><strong>{{ folderCount }}</strong> 个文件夹</span></div>
    </header>
    <div class="toolbar">
      <div class="search-box"><el-icon><Search /></el-icon><el-input v-model="keyword" clearable placeholder="搜索当前文件夹" @keyup.enter="loadFiles" /><el-button type="primary" @click="loadFiles">查询</el-button></div>
      <div class="toolbar-right"><el-button @click="folderDialog = true"><el-icon><FolderAdd /></el-icon>新建文件夹</el-button><el-upload :show-file-list="false" :http-request="handleUpload" :disabled="uploading"><el-button type="primary" :loading="uploading"><el-icon><Upload /></el-icon>上传文件</el-button></el-upload></div>
    </div>
    <div class="file-layout" v-loading="loading">
      <aside class="folder-panel">
        <div class="panel-title"><span>目录</span><el-tag size="small" type="info">{{ folderCount }}</el-tag></div>
        <el-tree :data="folders" node-key="id" :props="{ label: 'name', children: 'children' }" default-expand-all @node-click="selectFolder" />
        <div class="panel-title asset-title"><span>素材存储</span><el-tag size="small" type="warning">{{ assetGroups.length }}</el-tag></div>
        <div class="asset-list">
          <div v-for="g in assetGroups" :key="g.key" class="asset-node" :class="{ active: assetMode && currentGroup === g.key }" @click="selectAssetGroup(g)">
            <el-icon><Picture /></el-icon>
            <span class="asset-name">{{ g.name }}</span>
            <el-tooltip v-if="g.risk === 'high'" content="业务文件，删除会影响下载，请谨慎操作"><el-tag size="small" type="danger" effect="plain">风险</el-tag></el-tooltip>
            <span class="asset-count">{{ g.file_count }}</span>
          </div>
        </div>
      </aside>
      <main class="content-panel">
        <template v-if="!assetMode">
          <div class="content-heading"><div><span class="muted">当前位置</span><h2>{{ currentFolderName }}</h2></div><el-button text @click="loadFiles"><el-icon><Refresh /></el-icon>刷新</el-button></div>
          <el-table :data="files" class="file-table" empty-text="当前文件夹暂无文件">
            <el-table-column label="名称" min-width="300"><template #default="{ row }"><div class="file-name"><span class="file-icon"><el-icon><Document /></el-icon></span><span>{{ row.name }}</span></div></template></el-table-column>
            <el-table-column prop="mime_type" label="类型" width="180" />
            <el-table-column label="大小" width="120"><template #default="{ row }">{{ formatSize(row.size) }}</template></el-table-column>
            <el-table-column prop="created_at" label="上传时间" width="180" />
            <el-table-column label="操作" width="150" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="download(row)">下载</el-button><el-button link type="danger" @click="removeFile(row)">删除</el-button></template></el-table-column>
          </el-table>
          <div class="table-footer"><span class="result-count">共 {{ total }} 个文件</span><el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="prev, pager, next" @change="loadFiles" /></div>
        </template>
        <template v-else>
          <div class="content-heading">
            <div>
              <span class="muted">素材存储 / {{ currentGroupInfo?.name }}</span>
              <h2 class="asset-path">{{ currentAssetPathLabel }}<el-button v-if="currentAssetPath" link size="small" @click="upAssetDir"><el-icon><Back /></el-icon>上一级</el-button></h2>
            </div>
            <el-button text @click="loadAssets"><el-icon><Refresh /></el-icon>刷新</el-button>
          </div>
          <el-alert v-if="currentGroupInfo" :type="currentGroupInfo.risk === 'high' ? 'warning' : 'info'" :title="currentGroupInfo.note" :closable="false" class="asset-alert" />
          <el-table :data="assetDirs" class="file-table" empty-text="该目录为空">
            <el-table-column label="文件夹" min-width="300"><template #default="{ row }"><div class="file-name folder" @click="enterAssetDir(row.path)"><span class="file-icon"><el-icon><Folder /></el-icon></span><span>{{ row.name }}</span></div></template></el-table-column>
            <el-table-column label="操作" width="80"><template #default="{ row }"><el-button link type="primary" @click="enterAssetDir(row.path)">进入</el-button></template></el-table-column>
          </el-table>
          <el-table :data="assetFiles" class="file-table">
            <el-table-column label="文件名" min-width="300"><template #default="{ row }"><div class="file-name"><span class="file-icon"><el-icon><Document /></el-icon></span><span>{{ row.name }}</span></div></template></el-table-column>
            <el-table-column label="路径" min-width="220" show-overflow-tooltip><template #default="{ row }"><span class="muted">{{ row.path }}</span></template></el-table-column>
            <el-table-column label="大小" width="120"><template #default="{ row }">{{ formatSize(row.size) }}</template></el-table-column>
            <el-table-column label="修改时间" width="180"><template #default="{ row }">{{ formatTime(row.modified_at) }}</template></el-table-column>
            <el-table-column label="操作" width="150" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="downloadAsset(row)">下载</el-button><el-button link type="danger" @click="removeAsset(row)">删除</el-button></template></el-table-column>
          </el-table>
          <div class="table-footer"><span class="result-count">共 {{ assetDirs.length }} 个目录、{{ assetFiles.length }} 个文件</span></div>
        </template>
      </main>
    </div>
  </section>
  <el-dialog v-model="folderDialog" title="新建文件夹" width="420px">
    <el-input v-model="folderName" maxlength="120" placeholder="请输入文件夹名称" @keyup.enter="createFolder" />
    <template #footer><el-button @click="folderDialog = false">取消</el-button><el-button type="primary" @click="createFolder">创建</el-button></template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, FolderAdd, Upload, Document, Refresh, Picture, Folder, Back } from '@element-plus/icons-vue'
import { createFileFolder, deleteSystemFile, getFileFolders, getFiles, uploadSystemFile, downloadSystemFileUrl, getAssetGroups, getAssetList, deleteAsset, assetDownloadUrl } from '@/api'

const loading = ref(false); const uploading = ref(false); const folders = ref<any[]>([]); const files = ref<any[]>([])
const folderId = ref(0); const keyword = ref(''); const page = ref(1); const pageSize = ref(20); const total = ref(0)
const folderDialog = ref(false); const folderName = ref('')
const folderCount = computed(() => countFolders(folders.value))
function countFolders(nodes: any[]): number { return nodes.reduce((sum, node) => sum + (node.id === 0 ? 0 : 1) + countFolders(node.children || []), 0) }
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

// ---- 素材存储浏览 ----
const assetGroups = ref<any[]>([])
const assetMode = ref(false)
const currentGroup = ref('')
const currentAssetPath = ref('')
const assetDirs = ref<any[]>([])
const assetFiles = ref<any[]>([])
const currentGroupInfo = computed(() => assetGroups.value.find((g) => g.key === currentGroup.value))
const currentAssetPathLabel = computed(() => (currentAssetPath.value ? currentAssetPath.value + '/' : '根目录'))

async function loadAssetGroups() { const data: any = await getAssetGroups(); assetGroups.value = data || [] }
async function loadAssets() {
  loading.value = true
  try {
    const data: any = await getAssetList({ group: currentGroup.value, path: currentAssetPath.value })
    assetDirs.value = data.dirs || []
    assetFiles.value = data.files || []
  } finally { loading.value = false }
}
function selectAssetGroup(group: any) {
  assetMode.value = true
  currentGroup.value = group.key
  currentAssetPath.value = ''
  loadAssets()
}
function enterAssetDir(path: string) { currentAssetPath.value = currentAssetPath.value ? `${currentAssetPath.value}/${path}` : path; loadAssets() }
function upAssetDir() {
  if (!currentAssetPath.value) return
  const parts = currentAssetPath.value.split('/')
  parts.pop()
  currentAssetPath.value = parts.join('/')
  loadAssets()
}
async function downloadAsset(row: any) {
  const token = localStorage.getItem('apeadmin_token')
  const response = await fetch(assetDownloadUrl(currentGroup.value, row.path), { headers: token ? { Authorization: `Bearer ${token}` } : {} })
  if (!response.ok) return ElMessage.error('下载失败')
  const blob = await response.blob()
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = row.name
  link.click()
  URL.revokeObjectURL(link.href)
}
async function removeAsset(row: any) {
  const highRisk = currentGroupInfo.value?.risk === 'high'
  const tip = highRisk
    ? `该文件属于业务安装包，删除后对应插件/版本将无法下载，且不可恢复！\n\n文件：${row.path}`
    : `确认删除「${row.path}」吗？删除后不可恢复。`
  const action = await ElMessageBox.confirm(tip, highRisk ? '高风险删除确认' : '删除确认', { type: highRisk ? 'warning' : 'warning', confirmButtonText: highRisk ? '我已知晓风险，删除' : '删除' }).catch(() => null)
  if (!action) return
  if (highRisk) {
    await ElMessageBox.prompt(`请输入文件名「${row.name}」以确认删除`, '二次确认', { confirmButtonText: '确认删除', cancelButtonText: '取消', inputPattern: new RegExp(`^${row.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`), inputErrorMessage: '文件名不匹配' })
  }
  await deleteAsset(currentGroup.value, row.path)
  ElMessage.success('已删除')
  await Promise.all([loadAssets(), loadAssetGroups()])
}
function formatTime(iso: string) { return iso ? iso.replace('T', ' ').slice(0, 16) : '-' }

onMounted(async () => { await Promise.all([loadFolders(), loadFiles(), loadAssetGroups()]) })
</script>

<style scoped>
.file-page { background: #fff; border: 1px solid #e8edf5; border-radius: 8px; overflow: hidden; }.page-heading { display: flex; align-items: center; justify-content: space-between; padding: 28px 32px 24px; border-bottom: 1px solid #edf1f6; }.eyebrow { margin: 0 0 7px; color: #7c8aa5; font-size: 11px; font-weight: 700; letter-spacing: 1.4px; }.page-heading h1 { margin: 0; color: #1d2939; font-size: 25px; line-height: 1.2; }.heading-copy { margin: 8px 0 0; color: #8491a7; font-size: 13px; }.heading-stats { display: flex; align-items: center; gap: 18px; color: #8491a7; font-size: 13px; }.heading-stats strong { margin-right: 4px; color: #344054; font-size: 18px; }.heading-stats i { width: 1px; height: 22px; background: #e4e9f0; }.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 18px; padding: 18px 32px; background: #fbfcfe; border-bottom: 1px solid #edf1f6; }.search-box { display: flex; align-items: center; width: min(520px, 60%); height: 38px; padding-left: 12px; border: 1px solid #dfe5ee; border-radius: 6px; background: #fff; }.search-box .el-icon { color: #98a2b3; }.search-box :deep(.el-input__wrapper) { box-shadow: none; }.search-box .el-button { height: 38px; margin-right: -1px; border-radius: 0 5px 5px 0; }.toolbar-right { display: flex; align-items: center; gap: 10px; }.file-layout { display: flex; min-height: 530px; }.folder-panel { width: 250px; flex: 0 0 250px; padding: 22px 14px; border-right: 1px solid #edf1f6; background: #fcfdff; }.panel-title { display: flex; align-items: center; justify-content: space-between; padding: 0 10px 14px; color: #344054; font-size: 14px; font-weight: 700; }.folder-panel :deep(.el-tree) { background: transparent; }.folder-panel :deep(.el-tree-node__content) { height: 38px; margin: 2px 0; border-radius: 5px; color: #667085; }.folder-panel :deep(.el-tree-node__content:hover) { background: #f0f4ff; }.folder-panel :deep(.is-current > .el-tree-node__content) { color: #4f63e8; background: #eef2ff; font-weight: 600; }.content-panel { flex: 1; min-width: 0; padding: 24px 28px 18px; }.content-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }.content-heading h2 { margin: 5px 0 0; color: #1d2939; font-size: 19px; }.muted { color: #98a2b3; font-size: 12px; }.file-table :deep(th.el-table__cell) { height: 42px; color: #8491a7; background: #fbfcfe; font-size: 12px; font-weight: 600; }.file-table :deep(td.el-table__cell) { height: 58px; color: #475467; }.file-name { display: flex; align-items: center; gap: 10px; color: #344054; font-weight: 500; }.file-icon { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 6px; color: #5b6ee1; background: #eef2ff; }.table-footer { display: flex; align-items: center; justify-content: space-between; padding-top: 20px; }.result-count { color: #98a2b3; font-size: 12px; }
@media (max-width: 760px) { .page-heading, .toolbar { align-items: flex-start; flex-direction: column; }.heading-stats, .search-box { width: 100%; }.search-box { max-width: none; }.toolbar-right { width: 100%; }.file-layout { display: block; }.folder-panel { width: auto; border-right: 0; border-bottom: 1px solid #edf1f6; }.content-panel { padding: 20px 14px; } }
/* 素材存储分组 */
.asset-title { margin-top: 18px; padding-top: 16px; border-top: 1px dashed #e4e9f0; }
.asset-list { display: flex; flex-direction: column; gap: 2px; }
.asset-node { display: flex; align-items: center; gap: 8px; height: 38px; padding: 0 10px; border-radius: 5px; color: #667085; font-size: 14px; cursor: pointer; }
.asset-node:hover { background: #f0f4ff; }
.asset-node.active { color: #4f63e8; background: #eef2ff; font-weight: 600; }
.asset-node .el-icon { color: #98a2b3; flex: 0 0 auto; }
.asset-node.active .el-icon { color: #4f63e8; }
.asset-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.asset-count { color: #98a2b3; font-size: 12px; }
.asset-alert { margin-bottom: 14px; }
.asset-path { display: flex; align-items: center; gap: 8px; }
.file-name.folder { cursor: pointer; }
.file-name.folder:hover span:last-child { color: #4f63e8; }
</style>
