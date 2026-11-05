<template>
  <div class="hermes-files-page">
    <!-- 面包屑 -->
    <div class="page-bar">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="(c, i) in crumbItems" :key="i">
          <a
            v-if="i < crumbItems.length - 1"
            class="crumb-link"
            href="javascript:void(0)"
            @click.prevent="jumpTo(c.path)"
          >{{ c.label }}</a>
          <span v-else class="crumb-current">{{ c.label }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
      <span class="path-hint">{{ currentPath || '根目录' }}</span>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button :icon="ArrowLeft" :disabled="!currentPath" @click="goUp">返回上级</el-button>
        <el-button :icon="FolderAdd" @click="mkdirDialog = true">新建文件夹</el-button>
      </div>
      <div class="toolbar-right">
        <el-upload :show-file-list="false" :http-request="handleUpload" :disabled="uploading" multiple>
          <el-button type="primary" :icon="Upload" :loading="uploading">上传文件</el-button>
        </el-upload>
        <el-button :icon="Refresh" @click="loadFiles">刷新</el-button>
      </div>
    </div>

    <!-- 文件表格 -->
    <el-table
      ref="tableRef"
      :data="files"
      v-loading="loading"
      class="file-table"
      empty-text="当前目录为空"
      @expand-change="onExpandChange"
      @row-click="onRowClick"
      @row-dblclick="onRowDblclick"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div v-if="row.is_dir" class="expand-tip">双击文件夹进入子目录</div>
          <div v-else v-loading="row._loading" class="expand-body">
            <pre v-if="row._content !== undefined" class="file-content">{{ row._content }}</pre>
            <el-empty v-else-if="!row._loading" description="暂无内容" :image-size="40" />
          </div>
        </template>
      </el-table-column>
      <el-table-column label="名称" min-width="320">
        <template #default="{ row }">
          <div class="file-name" :class="{ 'is-dir': row.is_dir }">
            <el-icon class="file-icon"><Folder v-if="row.is_dir" /><Document v-else /></el-icon>
            <span>{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_dir ? 'warning' : 'info'" size="small" effect="plain">
            {{ row.is_dir ? '文件夹' : '文件' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="大小" width="120">
        <template #default="{ row }">{{ row.is_dir ? '-' : formatSize(row.size) }}</template>
      </el-table-column>
      <el-table-column label="修改时间" width="180">
        <template #default="{ row }">{{ formatTime(row.modified) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click.stop="removeEntry(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建文件夹弹窗 -->
    <el-dialog v-model="mkdirDialog" title="新建文件夹" width="420px">
      <el-input
        v-model="newDirName"
        maxlength="120"
        placeholder="请输入文件夹名称"
        @keyup.enter="confirmMkdir"
      />
      <template #footer>
        <el-button @click="mkdirDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmMkdir">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElTag,
  ElBreadcrumb,
  ElBreadcrumbItem,
  ElUpload,
  ElDialog,
  ElInput,
  ElMessage,
  ElMessageBox,
} from 'element-plus'
import {
  Folder,
  Document,
  Refresh,
  Upload,
  FolderAdd,
  Delete,
  ArrowLeft,
} from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

const loading = ref(false)
const uploading = ref(false)
const files = ref<any[]>([])
const currentPath = ref('')
const tableRef = ref<{ toggleRowExpansion: (row: any, expanded?: boolean) => void } | null>(null)

const mkdirDialog = ref(false)
const newDirName = ref('')

// ── 路径工具 ──────────────────────────────────────
function joinPath(parent: string, name: string): string {
  const p = parent.replace(/\/+$/, '')
  return p ? `${p}/${name}` : name
}

function parentPath(p: string): string {
  const parts = p.split('/').filter(Boolean)
  parts.pop()
  return parts.join('/')
}

const crumbItems = computed(() => {
  const parts = currentPath.value.split('/').filter(Boolean)
  const items: { label: string; path: string }[] = [{ label: '根目录', path: '' }]
  let acc = ''
  for (const p of parts) {
    acc = acc ? `${acc}/${p}` : p
    items.push({ label: p, path: acc })
  }
  return items
})

function jumpTo(path: string) {
  if (path === currentPath.value) return
  currentPath.value = path
  loadFiles()
}

function goUp() {
  if (!currentPath.value) return
  currentPath.value = parentPath(currentPath.value)
  loadFiles()
}

// ── 文件加载 ──────────────────────────────────────
async function loadFiles() {
  loading.value = true
  try {
    const res: any = await hermes.listFiles(currentPath.value || undefined)
    const list = res?.entries ?? res?.files ?? (Array.isArray(res) ? res : [])
    files.value = (list || []).map((f: any) => ({
      ...f,
      name: f.name ?? String(f.path ?? '').split('/').pop() ?? '',
      is_dir: f.is_dir ?? f.type === 'folder',
      size: f.size ?? f.is_dir ?? false ? (f.size ?? null) : null,
      modified: f.modified ?? f.mtime ?? f.modified_at ?? null,
    }))
  } catch (e: any) {
    ElMessage.error(`加载失败: ${e.message || e}`)
  } finally {
    loading.value = false
  }
}

// ── 新建文件夹 ────────────────────────────────────
async function confirmMkdir() {
  const name = newDirName.value.trim()
  if (!name) {
    ElMessage.warning('请输入文件夹名称')
    return
  }
  try {
    await hermes.createDir(joinPath(currentPath.value, name))
    ElMessage.success('文件夹创建成功')
    mkdirDialog.value = false
    newDirName.value = ''
    loadFiles()
  } catch (e: any) {
    ElMessage.error(`创建失败: ${e.message || e}`)
  }
}

// ── 上传文件 ──────────────────────────────────────
async function handleUpload(options: any) {
  const file: File = options?.file
  if (!file) return
  uploading.value = true
  try {
    await hermes.uploadFile(currentPath.value, file, true)
    ElMessage.success(`上传成功: ${file.name}`)
    loadFiles()
    options?.onSuccess?.(file)
  } catch (e: any) {
    ElMessage.error(`上传失败: ${e.message || e}`)
    options?.onError?.(e)
  } finally {
    uploading.value = false
  }
}

// ── 删除 ──────────────────────────────────────────
async function removeEntry(row: any) {
  const isDir = !!row.is_dir
  try {
    await ElMessageBox.confirm(
      `确定删除「${row.name}」${isDir ? '及其全部内容' : ''}吗？此操作不可恢复。`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger',
      }
    )
  } catch {
    return
  }
  try {
    await hermes.deleteFile(joinPath(currentPath.value, row.name), isDir)
    ElMessage.success('删除成功')
    loadFiles()
  } catch (e: any) {
    ElMessage.error(`删除失败: ${e.message || e}`)
  }
}

// ── 展开读取内容 ──────────────────────────────────
// el-table expand-change 事件类型为交叉签名（row+expandedRows / row+expanded），
// 用 ...args 兼容两种调用形式
function onExpandChange(...args: any[]) {
  const row: any = args[0]
  const expandedRows: any[] = Array.isArray(args[1]) ? args[1] : []
  const expanded = expandedRows.includes(row)
  if (!expanded) return
  if (row.is_dir) {
    tableRef.value?.toggleRowExpansion(row, false)
    return
  }
  if (row._content !== undefined) return
  row._loading = true
  hermes
    .readFile(joinPath(currentPath.value, row.name))
    .then((res: any) => {
      row._content = res?.content ?? JSON.stringify(res ?? {}, null, 2)
    })
    .catch((e: any) => {
      row._content = `读取失败: ${e.message || e}`
    })
    .finally(() => {
      row._loading = false
    })
}

function onRowClick(row: any) {
  if (row.is_dir) return
  const expanded = tableRef.value?.toggleRowExpansion(row)
  // 展开状态由 el-table 内部维护，懒加载内容在 onExpandChange 中处理
  void expanded
}

function onRowDblclick(row: any) {
  if (row.is_dir) {
    currentPath.value = joinPath(currentPath.value, row.name)
    loadFiles()
  }
}

// ── 格式化 ────────────────────────────────────────
function formatSize(bytes?: number | null): string {
  if (bytes == null || Number.isNaN(Number(bytes))) return '-'
  let v = Number(bytes)
  if (v < 1024) return `${v} B`
  const units = ['KB', 'MB', 'GB', 'TB']
  let i = -1
  do {
    v /= 1024
    i++
  } while (v >= 1024 && i < units.length - 1)
  return `${v.toFixed(1)} ${units[i]}`
}

function formatTime(t?: string | null): string {
  if (!t) return '-'
  const d = new Date(t)
  if (Number.isNaN(d.getTime())) return String(t)
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

onMounted(loadFiles)
</script>

<style scoped>
.hermes-files-page {
  padding: 4px 0;
}
.page-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-bottom: none;
  border-radius: 8px 8px 0 0;
}
.crumb-link {
  color: var(--el-color-primary);
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
}
.crumb-link:hover {
  opacity: 0.8;
}
.crumb-current {
  color: var(--el-text-color-primary);
  font-weight: 600;
}
.page-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
  padding: 2px 10px;
  border-radius: 10px;
  max-width: 40%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-bottom: none;
}
.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.file-table {
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}
.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.file-name.is-dir {
  font-weight: 600;
  color: var(--el-text-color-primary);
  cursor: pointer;
}
.file-icon {
  color: var(--el-color-warning);
  flex-shrink: 0;
}
.file-name:not(.is-dir) .file-icon {
  color: var(--el-text-color-secondary);
}
.expand-body {
  padding: 4px 24px 12px 56px;
}
.empty-tip {
  padding: 4px 24px 12px 56px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.file-content {
  margin: 0;
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  max-height: 360px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>