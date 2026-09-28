<template>
  <section class="file-page">
    <header class="page-heading">
      <div><p class="eyebrow">SYSTEM STORAGE</p><h1>{{ t('system.file.title') }}</h1><p class="heading-copy">{{ t('system.file.subtitle') }}</p></div>
      <div class="heading-stats"><span><strong>{{ total }}</strong> {{ t('system.file.fileUnit') }}</span><i></i><span><strong>{{ folderCount }}</strong> {{ t('system.file.folderUnit') }}</span></div>
    </header>
    <div class="toolbar">
      <div class="search-box"><el-icon><Search /></el-icon><el-input v-model="keyword" clearable :placeholder="t('system.file.searchPlaceholder')" @keyup.enter="loadFiles" /><el-button type="primary" @click="loadFiles">{{ t('common.action.query') }}</el-button></div>
      <div class="toolbar-right"><el-button @click="folderDialog = true"><el-icon><FolderAdd /></el-icon>{{ t('system.file.createFolder') }}</el-button><el-upload :show-file-list="false" :http-request="handleUpload" :disabled="uploading"><el-button type="primary" :loading="uploading"><el-icon><Upload /></el-icon>{{ t('system.file.upload') }}</el-button></el-upload></div>
    </div>
    <div class="file-layout" v-loading="loading">
      <aside class="folder-panel">
        <div class="panel-title"><span>{{ t('system.file.directory') }}</span><el-tag size="small" type="info">{{ folderCount }}</el-tag></div>
        <el-tree :data="folders" node-key="id" :props="{ label: 'name', children: 'children' }" default-expand-all>
          <template #default="{ data }">
            <span class="tree-node">
              <span class="tree-label" @click="selectFolder(data)">{{ data.name }}</span>
              <span class="tree-actions">
                <el-button v-if="data.id !== (folders[0]?.id || 0)" link size="small" class="tree-btn" :title="t('system.file.moveFolderTitle')" @click.stop="openMoveFolder(data)"><el-icon><Rank /></el-icon></el-button>
                <el-button v-if="data.id !== (folders[0]?.id || 0)" link size="small" type="danger" class="tree-btn" :title="t('system.file.deleteFolderTitle')" @click.stop="removeFolder(data)"><el-icon><Delete /></el-icon></el-button>
              </span>
            </span>
          </template>
        </el-tree>
        <div class="panel-title asset-title"><span>{{ t('system.file.assetStorage') }}</span><el-tag size="small" type="warning">{{ assetGroups.length }}</el-tag></div>
        <div class="asset-list">
          <div v-for="g in assetGroups" :key="g.key" class="asset-node" :class="{ active: assetMode && currentGroup === g.key }" @click="selectAssetGroup(g)">
            <el-icon><Picture /></el-icon>
            <span class="asset-name">{{ g.name }}</span>
            <el-tooltip v-if="g.risk === 'high'" :content="t('system.file.riskTooltip')"><el-tag size="small" type="danger" effect="plain">{{ t('system.file.risk') }}</el-tag></el-tooltip>
            <span class="asset-count">{{ g.file_count }}</span>
          </div>
        </div>
      </aside>
      <main class="content-panel">
        <template v-if="!assetMode">
          <div class="content-heading"><div><span class="muted">{{ t('system.file.currentLocation') }}</span><h2>{{ currentFolderName }}</h2></div><el-button text @click="loadFiles"><el-icon><Refresh /></el-icon>{{ t('common.action.refresh') }}</el-button></div>
          <el-table :data="files" class="file-table" :empty-text="t('system.file.noFiles')">
            <el-table-column :label="t('common.action.name')" min-width="300"><template #default="{ row }"><div class="file-name"><span class="file-icon"><el-icon><Document /></el-icon></span><span>{{ row.name }}</span></div></template></el-table-column>
            <el-table-column prop="mime_type" :label="t('system.file.fileType')" width="180" />
            <el-table-column :label="t('system.file.fileSize')" width="120"><template #default="{ row }">{{ formatSize(row.size) }}</template></el-table-column>
            <el-table-column prop="created_at" :label="t('system.file.uploadTime')" width="180" />
            <el-table-column :label="t('common.action.actions')" width="260" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="previewFile(row)">{{ t('system.file.preview') }}</el-button><el-button link type="primary" @click="download(row)">{{ t('common.action.download') }}</el-button><el-button link type="primary" @click="openMoveFile(row)">{{ t('common.action.move') }}</el-button><el-button link type="danger" @click="removeFile(row)">{{ t('common.action.delete') }}</el-button></template></el-table-column>
          </el-table>
          <div class="table-footer"><span class="result-count">{{ t('system.file.totalFiles', { count: total }) }}</span><el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total" layout="prev, pager, next" @change="loadFiles" /></div>
        </template>
        <template v-else>
          <div class="content-heading">
            <div>
              <span class="muted">{{ t('system.file.assetStorage') }} / {{ currentGroupInfo?.name }}</span>
              <h2 class="asset-path">{{ currentAssetPathLabel }}<el-button v-if="currentAssetPath" link size="small" @click="upAssetDir"><el-icon><Back /></el-icon>{{ t('system.file.upLevel') }}</el-button></h2>
            </div>
            <el-button text @click="loadAssets"><el-icon><Refresh /></el-icon>{{ t('common.action.refresh') }}</el-button>
          </div>
          <el-alert v-if="currentGroupInfo" :type="currentGroupInfo.risk === 'high' ? 'warning' : 'info'" :title="currentGroupInfo.note" :closable="false" class="asset-alert" />
          <el-table :data="assetDirs" class="file-table" :empty-text="t('system.file.dirEmpty')">
            <el-table-column :label="t('system.file.folderColumn')" min-width="300"><template #default="{ row }"><div class="file-name folder" @click="enterAssetDir(row.path)"><span class="file-icon"><el-icon><Folder /></el-icon></span><span>{{ row.name }}</span></div></template></el-table-column>
            <el-table-column :label="t('common.action.actions')" width="80"><template #default="{ row }"><el-button link type="primary" @click="enterAssetDir(row.path)">{{ t('system.file.enter') }}</el-button></template></el-table-column>
          </el-table>
          <el-table :data="assetFiles" class="file-table">
            <el-table-column :label="t('system.file.fileName')" min-width="300"><template #default="{ row }"><div class="file-name"><span class="file-icon"><el-icon><Document /></el-icon></span><span>{{ row.name }}</span></div></template></el-table-column>
            <el-table-column :label="t('system.file.path')" min-width="220" show-overflow-tooltip><template #default="{ row }"><span class="muted">{{ row.path }}</span></template></el-table-column>
            <el-table-column :label="t('system.file.fileSize')" width="120"><template #default="{ row }">{{ formatSize(row.size) }}</template></el-table-column>
            <el-table-column :label="t('system.file.modifyTime')" width="180"><template #default="{ row }">{{ formatTime(row.modified_at) }}</template></el-table-column>
            <el-table-column :label="t('common.action.actions')" width="200" fixed="right"><template #default="{ row }"><el-button link type="primary" @click="previewAsset(row)">{{ t('system.file.preview') }}</el-button><el-button link type="primary" @click="downloadAsset(row)">{{ t('common.action.download') }}</el-button><el-button link type="danger" @click="removeAsset(row)">{{ t('common.action.delete') }}</el-button></template></el-table-column>
          </el-table>
          <div class="table-footer"><span class="result-count">{{ t('system.file.dirsAndFiles', { dirCount: assetDirs.length, fileCount: assetFiles.length }) }}</span></div>
        </template>
      </main>
    </div>
  </section>
  <el-dialog v-model="folderDialog" :title="t('system.file.createFolder')" width="420px">
    <el-input v-model="folderName" maxlength="120" :placeholder="t('system.file.folderNamePlaceholder')" @keyup.enter="createFolder" />
    <template #footer><el-button @click="folderDialog = false">{{ t('common.action.cancel') }}</el-button><el-button type="primary" @click="createFolder">{{ t('system.file.createBtn') }}</el-button></template>
  </el-dialog>
  <el-dialog v-model="moveDialog" :title="moveType === 'folder' ? t('system.file.moveFolderTitle') : t('system.file.moveFileTitle')" width="480px">
    <p class="move-tip">{{ t('system.file.moveToTip', { name: moveName }) }}</p>
    <el-tree-select
      v-model="moveTargetId"
      :data="moveTreeData"
      node-key="id"
      :props="{ label: 'name', children: 'children' }"
      :render-after-expand="false"
      check-strictly
      default-expand-all
      style="width: 100%"
      :placeholder="t('system.file.selectTargetFolder')"
    />
    <template #footer><el-button @click="moveDialog = false">{{ t('common.action.cancel') }}</el-button><el-button type="primary" @click="confirmMove">{{ t('common.action.move') }}</el-button></template>
  </el-dialog>
  <el-dialog v-model="previewDialog" :title="previewName" width="860px" top="6vh" class="preview-dialog">
    <div v-loading="previewLoading" class="preview-body">
      <template v-if="previewType === 'image'">
        <img :src="previewSrc" :alt="previewName" class="preview-image" @load="previewLoading = false" @error="previewError" />
      </template>
      <template v-else-if="previewType === 'pdf'">
        <iframe :src="previewSrc" class="preview-iframe" @load="previewLoading = false"></iframe>
      </template>
      <template v-else-if="previewType === 'text'">
        <pre class="preview-text" @load="previewLoading = false">{{ previewText }}</pre>
      </template>
      <template v-else>
        <el-empty :description="t('system.file.unsupportedPreview')" />
      </template>
    </div>
    <template #footer><el-button @click="previewDialog = false">{{ t('common.action.close') }}</el-button></template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, FolderAdd, Upload, Document, Refresh, Picture, Folder, Back, Rank, Delete } from '@element-plus/icons-vue'
import { createFileFolder, deleteFileFolder, deleteSystemFile, getFileFolders, getFiles, uploadSystemFile, downloadSystemFileUrl, previewSystemFileUrl, moveSystemFile, moveSystemFolder, getAssetGroups, getAssetList, deleteAsset, assetDownloadUrl, assetPreviewUrl } from '@/api'
const { t } = useI18n()

const loading = ref(false); const uploading = ref(false); const folders = ref<any[]>([]); const files = ref<any[]>([])
const folderId = ref(0); const keyword = ref(''); const page = ref(1); const pageSize = ref(20); const total = ref(0)
const folderDialog = ref(false); const folderName = ref('')
const folderCount = computed(() => countFolders(folders.value))
function countFolders(nodes: any[]): number { return nodes.reduce((sum, node) => sum + (node.id === 0 ? 0 : 1) + countFolders(node.children || []), 0) }
const currentFolderName = computed(() => findName(folders.value, folderId.value) || t('system.file.allFiles'))
function findName(nodes: any[], id: number): string { for (const node of nodes) { if (node.id === id) return node.name; const name = findName(node.children || [], id); if (name) return name } return '' }
async function loadFolders() { const data: any = await getFileFolders(); folders.value = data || [] }
async function loadFiles() { loading.value = true; try { const data: any = await getFiles({ folder_id: folderId.value, keyword: keyword.value, page: page.value, page_size: pageSize.value }); files.value = data.items || []; total.value = data.total || 0 } finally { loading.value = false } }
function selectFolder(node: any) { assetMode.value = false; folderId.value = node.id; page.value = 1; loadFiles() }
async function createFolder() { if (!folderName.value.trim()) return ElMessage.warning(t('system.file.inputFolderName')); await createFileFolder({ name: folderName.value, parent_id: folderId.value }); ElMessage.success(t('system.file.folderCreated')); folderDialog.value = false; folderName.value = ''; await loadFolders() }
async function handleUpload(options: any) { uploading.value = true; try { await uploadSystemFile(options.file, folderId.value); ElMessage.success(t('system.file.uploadSuccess')); await loadFiles() } finally { uploading.value = false } }
async function download(row: any) { const token = localStorage.getItem('apeadmin_token'); const link = document.createElement('a'); link.href = `${downloadSystemFileUrl(row.id)}?token=${encodeURIComponent(token || '')}`; link.download = row.name; document.body.appendChild(link); link.click(); link.remove() }
async function removeFile(row: any) { await ElMessageBox.confirm(t('system.file.deleteConfirm', { name: row.name }), t('system.file.deleteConfirmTitle'), { type: 'warning' }); await deleteSystemFile(row.id); ElMessage.success(t('system.file.deleted')); await loadFiles() }
async function removeFolder(data: any) {
  // 级联删除：整个文件夹树及其下所有文件
  const tip = t('system.file.deleteFolderConfirm', { name: data.name }) + '\n\n' + t('system.file.deleteFolderAndContents')
  await ElMessageBox.confirm(tip, t('system.file.deleteFolderConfirmTitle'), { type: 'warning', confirmButtonText: t('system.file.deleteFolderAndContents'), cancelButtonText: t('common.action.cancel') })
  await deleteFileFolder(data.id)
  ElMessage.success(t('system.file.deleted'))
  // 若当前正浏览被删文件夹，退回根目录
  if (folderId.value === data.id) { folderId.value = 0 }
  await Promise.all([loadFolders(), loadFiles()])
}

// ---- 移动文件 / 文件夹 ----
const moveDialog = ref(false); const moveType = ref<'file' | 'folder'>('file'); const moveName = ref(''); const moveTargetId = ref(0)
const moveFileId = ref(0); const moveFolderId = ref(0)
const moveTreeData = computed(() => {
  // 移动文件夹时排除自身及其子树
  if (moveType.value === 'folder' && moveFolderId.value) {
    return pruneTree(folders.value, moveFolderId.value)
  }
  return folders.value
})
function pruneTree(nodes: any[], excludeId: number): any[] {
  return nodes.filter((n) => n.id !== excludeId).map((n) => ({ ...n, children: n.children ? pruneTree(n.children, excludeId) : [] }))
}
function openMoveFile(row: any) { moveType.value = 'file'; moveFileId.value = row.id; moveName.value = row.name; moveTargetId.value = folderId.value; moveDialog.value = true }
function openMoveFolder(data: any) { moveType.value = 'folder'; moveFolderId.value = data.id; moveName.value = data.name; moveTargetId.value = folderId.value; moveDialog.value = true }
async function confirmMove() {
  if (!moveTargetId.value) return ElMessage.warning(t('system.file.selectTargetFolder'))
  try {
    if (moveType.value === 'file') { await moveSystemFile(moveFileId.value, moveTargetId.value) } else { await moveSystemFolder(moveFolderId.value, moveTargetId.value) }
    ElMessage.success(t('system.file.moved')); moveDialog.value = false; await Promise.all([loadFolders(), loadFiles()])
  } catch (e: any) { ElMessage.error(e?.message || t('system.file.moveFailed')) }
}
async function reloadFiles() { await Promise.all([loadFiles(), loadFolders()]) }
function formatSize(size: number) { if (size < 1024) return `${size} B`; if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`; return `${(size / 1024 / 1024).toFixed(1)} MB` }

// ---- 文件预览 ----
const previewDialog = ref(false)
const previewLoading = ref(false)
const previewName = ref('')
const previewType = ref<'image' | 'pdf' | 'text' | 'unsupported'>('unsupported')
const previewSrc = ref('')
const previewText = ref('')

function previewTokenQuery() {
  const token = localStorage.getItem('apeadmin_token')
  return token ? `&token=${encodeURIComponent(token)}` : ''
}
const PREVIEW_IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico']
const PREVIEW_TEXT_EXTS = ['txt', 'md', 'csv', 'json', 'log', 'xml', 'yml', 'yaml', 'ini', 'conf', 'cfg']

function classifyPreview(name: string): 'image' | 'pdf' | 'text' | 'unsupported' {
  const ext = (name.split('.').pop() || '').toLowerCase()
  if (PREVIEW_IMAGE_EXTS.includes(ext)) return 'image'
  if (ext === 'pdf') return 'pdf'
  if (PREVIEW_TEXT_EXTS.includes(ext)) return 'text'
  return 'unsupported'
}
function openPreview(name: string, url: string) {
  previewName.value = name
  previewLoading.value = true
  const type = classifyPreview(name)
  previewType.value = type
  if (type === 'text') {
    fetch(url).then((r) => r.text()).then((t) => { previewText.value = t; previewLoading.value = false }).catch(() => { previewLoading.value = false; ElMessage.error('预览失败') })
  } else if (type === 'image' || type === 'pdf') {
    previewSrc.value = url
  } else {
    previewLoading.value = false
  }
  previewDialog.value = true
}
function previewFile(row: any) {
  openPreview(row.name, `${previewSystemFileUrl(row.id)}${previewTokenQuery()}`)
}
function previewAsset(row: any) {
  openPreview(row.name, `${assetPreviewUrl(currentGroup.value, row.path)}${previewTokenQuery()}`)
}
function previewError() { previewLoading.value = false; ElMessage.error(t('system.file.previewLoadFailed')) }

// ---- 素材存储浏览 ----
const assetGroups = ref<any[]>([])
const assetMode = ref(false)
const currentGroup = ref('')
const currentAssetPath = ref('')
const assetDirs = ref<any[]>([])
const assetFiles = ref<any[]>([])
const currentGroupInfo = computed(() => assetGroups.value.find((g) => g.key === currentGroup.value))
const currentAssetPathLabel = computed(() => (currentAssetPath.value ? currentAssetPath.value + '/' : t('system.file.rootDir')))

async function loadAssetGroups() { const data: any = await getAssetGroups(); assetGroups.value = data || [] }
async function loadAssets() {
  loading.value = true
  try {
    const data: any = await getAssetList({ group: currentGroup.value, path: currentAssetPath.value })
    assetDirs.value = data.dirs || []
    assetFiles.value = data.files || []
  } catch {
    // 目录不存在（可能已被删除）：清空列表并自动回退到分组根目录，避免停留在失效路径连环报错
    assetDirs.value = []
    assetFiles.value = []
    if (currentAssetPath.value) {
      currentAssetPath.value = ''
      try {
        const data: any = await getAssetList({ group: currentGroup.value, path: '' })
        assetDirs.value = data.dirs || []
        assetFiles.value = data.files || []
      } catch { /* 根目录也失败则保持空列表；错误提示由全局拦截器统一弹出 */ }
    }
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
  if (!response.ok) return ElMessage.error(t('system.file.downloadFailed'))
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
    ? t('system.file.highRiskDeleteTip', { path: row.path })
    : t('system.file.deleteConfirm', { name: row.path })
  const action = await ElMessageBox.confirm(tip, highRisk ? t('system.file.highRiskDeleteTitle') : t('system.file.deleteConfirmTitle'), { type: highRisk ? 'warning' : 'warning', confirmButtonText: highRisk ? t('system.file.confirmRiskDelete') : t('common.action.delete') }).catch(() => null)
  if (!action) return
  if (highRisk) {
    await ElMessageBox.prompt(t('system.file.inputNameToDelete', { name: row.name }), t('system.file.secondConfirm'), { confirmButtonText: t('system.file.confirmDelete'), cancelButtonText: t('common.action.cancel'), inputPattern: new RegExp(`^${row.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`), inputErrorMessage: t('system.file.nameMismatch') })
  }
  await deleteAsset(currentGroup.value, row.path)
  ElMessage.success(t('system.file.deleted'))
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
.tree-node { display: flex; align-items: center; justify-content: space-between; flex: 1; padding-right: 6px; }
.tree-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; }
.tree-actions { display: flex; align-items: center; gap: 2px; visibility: hidden; }
.tree-node:hover .tree-actions { visibility: visible; }
.tree-btn { padding: 2px; }
.move-tip { margin: 0 0 12px; color: #667085; font-size: 14px; }
/* 文件预览 */
.preview-body { min-height: 320px; max-height: 68vh; display: flex; align-items: center; justify-content: center; overflow: auto; background: #f8fafc; border-radius: 6px; }
.preview-image { max-width: 100%; max-height: 66vh; object-fit: contain; border-radius: 4px; }
.preview-iframe { width: 100%; height: 66vh; border: 0; border-radius: 4px; background: #fff; }
.preview-text { width: 100%; max-height: 66vh; margin: 0; padding: 16px 20px; overflow: auto; background: #fff; border: 1px solid #e8edf5; border-radius: 4px; color: #344054; font-size: 13px; line-height: 1.7; white-space: pre-wrap; word-break: break-all; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.preview-dialog :deep(.el-dialog__body) { padding-top: 16px; }
</style>
