<template>
  <el-card shadow="never" class="page-card">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        :placeholder="t('system.plugin.searchPlaceholder')"
        clearable
        style="width: 220px"
        @keyup.enter="fetchData"
      />
      <el-button type="primary" @click="fetchData">
        <el-icon><Search /></el-icon>{{ t('common.action.query') }}
      </el-button>
      <div class="toolbar-right">
        <el-button type="success" @click="uploadVisible = true">
          <el-icon><Upload /></el-icon>{{ t('system.plugin.import') }}
        </el-button>
        <el-button type="warning" :loading="restarting" @click="handleRestart">
          <el-icon v-if="!restarting"><RefreshRight /></el-icon>{{ t('system.plugin.restart') }}
        </el-button>
      </div>
    </div>

    <!-- Plugin cards -->
    <div v-loading="loading" class="plugin-grid">
      <el-card
        v-for="item in filteredList"
        :key="item.id"
        shadow="hover"
        class="plugin-card"
        :class="{ 'plugin-disabled': !item.enabled }"
      >
        <div class="plugin-header">
          <div class="plugin-icon">
            <el-icon :size="28" :color="item.enabled ? '#5A67F5' : '#c0c4cc'">
              <Box />
            </el-icon>
          </div>
          <div class="plugin-info">
            <h3>{{ item.display_name || item.name }}</h3>
            <span class="plugin-version">v{{ item.version }}</span>
          </div>
          <el-switch
            v-model="item.enabled"
            :loading="togglingId === item.id"
            @change="(val: boolean) => handleToggle(item, val)"
          />
        </div>

        <p class="plugin-desc">{{ item.description || t('system.plugin.noDescription') }}</p>

        <div class="plugin-meta">
          <el-tag size="small" type="info">{{ item.author || t('system.plugin.unknownAuthor') }}</el-tag>
          <span class="plugin-path">{{ item.module_path }}</span>
        </div>

        <div class="plugin-footer">
          <span class="plugin-time">{{ formatTime(item.updated_at) }}</span>
          <div class="footer-actions">
            <el-button link type="primary" @click="openConfig(item)">
              <el-icon><Setting /></el-icon>{{ t('system.plugin.config') }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(item)">
              <el-icon><Delete /></el-icon>{{ t('common.action.delete') }}
            </el-button>
          </div>
        </div>
      </el-card>

      <el-empty v-if="!loading && filteredList.length === 0" :description="t('system.plugin.noPlugins')" />
    </div>

    <!-- Pagination -->
    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      :page-sizes="[12, 24, 50]"
      layout="total, sizes, prev, pager, next, jumper"
      class="pagination"
      @change="fetchData"
    />
  </el-card>

  <!-- Config Dialog -->
  <el-dialog
    v-model="configVisible"
    :title="t('system.plugin.configTitle', { name: currentPlugin?.display_name || currentPlugin?.name || '' })"
    width="600px"
  >
    <el-alert
      :title="t('system.plugin.configHint')"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    />
    <el-input
      v-model="configText"
      type="textarea"
      :rows="12"
      placeholder='{"key": "value"}'
      class="config-editor"
    />
    <template #footer>
      <el-button @click="configVisible = false">{{ t('common.action.cancel') }}</el-button>
      <el-button type="primary" :loading="savingConfig" @click="saveConfig">{{ t('common.action.save') }}</el-button>
    </template>
  </el-dialog>

  <!-- Upload Dialog -->
  <el-dialog v-model="uploadVisible" :title="t('system.plugin.importPlugin')" width="520px">
    <el-alert
      :title="t('system.plugin.uploadHint')"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 8px"
    />
    <el-alert
      v-if="pkgKindWarning"
      :title="pkgKindWarning"
      type="warning"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    />
    <p v-else style="margin: 0 0 16px; font-size: 12px; color: #909399">
      {{ t('system.plugin.goL2Warning') }}
    </p>
    <el-upload
      drag
      :auto-upload="false"
      accept=".zip"
      :limit="1"
      :on-change="(file: any) => handleFileSelect(file.raw)"
      :on-remove="handleFileRemove"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">{{ t('system.plugin.dragHere') }}<em>{{ t('system.plugin.clickToSelect') }}</em></div>
      <template #tip>
        <div class="el-upload__tip">{{ t('system.plugin.uploadTip') }}</div>
      </template>
    </el-upload>
    <template #footer>
      <el-button @click="uploadVisible = false">{{ t('common.action.cancel') }}</el-button>
      <el-button type="primary" :loading="uploading" :disabled="!uploadingFile || !!pkgKindError" @click="handleUpload">
        {{ t('system.plugin.uploadAndInstall') }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { refreshDynamicRoutes } from '@/router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPlugins,
  togglePlugin,
  getPluginConfig,
  updatePluginConfig,
  uploadPlugin,
  restartServer,
  deletePlugin,
} from '@/api'
import { pollBackendHealth } from '@/utils/restart'

const { t } = useI18n()

interface PluginRow {
  id: number
  name: string
  display_name: string
  description: string
  version: string
  author: string
  module_path: string
  enabled: boolean
  config: Record<string, any> | null
  created_at: string
  updated_at: string
}

const list = ref<PluginRow[]>([])
const total = ref(0)
const loading = ref(false)
const togglingId = ref<number | null>(null)
const query = reactive({ page: 1, page_size: 12, keyword: '' })

// Upload state
const uploadVisible = ref(false)
const uploadingFile = ref<File | null>(null)
const uploading = ref(false)

// Restart state
const restarting = ref(false)

// Config dialog state
const configVisible = ref(false)
const currentPlugin = ref<PluginRow | null>(null)
const configText = ref('')
const savingConfig = ref(false)
const userStore = useUserStore()

async function refreshRuntimeMenus() {
  await userStore.fetchUserInfo()
  refreshDynamicRoutes(userStore.menus)
}

const filteredList = computed(() => {
  if (!query.keyword) return list.value
  const kw = query.keyword.toLowerCase()
  return list.value.filter(
    (p) =>
      p.name.toLowerCase().includes(kw) ||
      p.display_name.toLowerCase().includes(kw)
  )
})

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getPlugins({
      page: query.page,
      page_size: query.page_size,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function handleToggle(item: PluginRow, val: boolean) {
  togglingId.value = item.id
  try {
    const result: any = await togglePlugin(item.id, val)
    if (result?.refresh) await refreshRuntimeMenus()
    ElMessage.success(t('system.plugin.enabledSuccess'))
  } catch {
    // Revert on error — the axios interceptor already showed the message.
    item.enabled = !val
  } finally {
    togglingId.value = null
  }
}

async function openConfig(item: PluginRow) {
  currentPlugin.value = item
  configVisible.value = true
  try {
    const data: any = await getPluginConfig(item.id)
    configText.value = JSON.stringify(data.config || {}, null, 2)
  } catch {
    configText.value = JSON.stringify(item.config || {}, null, 2)
  }
}

async function saveConfig() {
  if (!currentPlugin.value) return

  let parsed: any
  try {
    parsed = JSON.parse(configText.value)
  } catch {
    ElMessage.error(t('system.plugin.jsonError'))
    return
  }

  savingConfig.value = true
  try {
    await updatePluginConfig(currentPlugin.value.id, parsed)
    ElMessage.success(t('system.plugin.configSaved'))
    configVisible.value = false
    fetchData()
  } finally {
    savingConfig.value = false
  }
}

function formatTime(t: string) {
  if (!t) return '—'
  return t.replace('T', ' ').slice(0, 19)
}

// ---- Upload: client-side package-kind pre-check ----
// Reads the zip central directory in the browser (no upload needed) to
// detect a Go-stack (ApeAdmin-Gin) L2 package and block it early with an
// actionable message, matching the backend guard in pkgdetect.py.
const pkgKindError = ref('')
const pkgKindWarning = ref('')

async function detectZipKind(file: File): Promise<'go' | 'python' | 'unknown'> {
  try {
    const buf = await file.slice(0, Math.min(file.size, 4 * 1024 * 1024)).arrayBuffer()
    const view = new DataView(buf)
    // Locate End of Central Directory (EOCD) signature 0x06054b50.
    let eocd = -1
    for (let i = view.byteLength - 22; i >= Math.max(0, view.byteLength - 66000); i--) {
      if (view.getUint32(i, true) === 0x06054b50) { eocd = i; break }
    }
    if (eocd < 0) return 'unknown'
    const entryCount = view.getUint16(eocd + 10, true)
    const cdSize = view.getUint32(eocd + 12, true)
    const cdOffset = view.getUint32(eocd + 16, true)
    if (cdOffset + cdSize > file.size) return 'unknown'
    // Central directory may start beyond the sliced prefix; re-slice it.
    const cdBuf = await file.slice(cdOffset, cdOffset + cdSize).arrayBuffer()
    const cd = new DataView(cdBuf)
    const decoder = new TextDecoder()
    let hasPluginJson = false
    let manifestType = ''
    let hasInit = false
    let hasMenuAssets = false
    let hasGoBinary = false
    let offset = 0
    for (let i = 0; i < entryCount; i++) {
      if (offset + 46 > cd.byteLength || cd.getUint32(offset, true) !== 0x02014b50) break
      const nameLen = cd.getUint16(offset + 28, true)
      const extraLen = cd.getUint16(offset + 30, true)
      const commentLen = cd.getUint16(offset + 32, true)
      const name = decoder.decode(new Uint8Array(cdBuf, offset + 46, nameLen))
      offset += 46 + nameLen + extraLen + commentLen
      const base = name.split('/').pop() || ''
      const dirDepth = name.split('/').length - (name.endsWith('/') ? 1 : 0)
      if (base === 'plugin.json' && dirDepth <= 1) hasPluginJson = true
      if (base === '__init__.py') hasInit = true
      if (base === 'menu.json' || base === 'seed.sql') hasMenuAssets = true
      const ext = base.includes('.') ? base.slice(base.lastIndexOf('.')).toLowerCase() : ''
      if (['.so', '.dll', '.exe', '.bin'].includes(ext)) hasGoBinary = true
    }
    if (hasPluginJson) {
      // Read the manifest only if it lives inside the sliced prefix.
      if (manifestType === '') manifestType = '' // (kept simple: type detection below)
    }
    // Manifest content: try to read plugin.json from the prefix slice.
    if (hasPluginJson) {
      try {
        // Cheap approach: scan raw prefix bytes for "type":"l2" style JSON.
        const text = decoder.decode(new Uint8Array(buf))
        const m = text.match(/"type"\s*:\s*"([^"]+)"/)
        if (m) manifestType = m[1].toLowerCase()
      } catch { /* ignore */ }
    }
    if (manifestType === 'l2') return 'go'
    if (hasPluginJson) {
      if (hasInit) return 'python'
      if (hasMenuAssets) return 'go'
      return 'python' // legacy python manifests have no type field
    }
    if (hasGoBinary && !hasInit) return 'go'
    if (hasInit) return 'python'
    return 'unknown'
  } catch {
    return 'unknown'
  }
}

async function handleFileSelect(file: File) {
  if (!file.name.toLowerCase().endsWith('.zip')) {
    ElMessage.error(t('system.plugin.zipOnly'))
    return
  }
  pkgKindError.value = ''
  pkgKindWarning.value = ''
  const kind = await detectZipKind(file)
  if (kind === 'go') {
    pkgKindError.value = t('system.plugin.goL2Error')
    pkgKindWarning.value = pkgKindError.value
    ElMessage.error(pkgKindError.value)
    return
  }
  if (kind === 'unknown') {
    pkgKindWarning.value = t('system.plugin.unknownPkgWarning')
  }
  uploadingFile.value = file
}

function handleFileRemove() {
  uploadingFile.value = null
  pkgKindError.value = ''
  pkgKindWarning.value = ''
}

async function handleUpload() {
  if (!uploadingFile.value) {
    ElMessage.warning(t('system.plugin.selectFileFirst'))
    return
  }
  uploading.value = true
  try {
    const data: any = await uploadPlugin(uploadingFile.value)
    if (data?.refresh) await refreshRuntimeMenus()
    ElMessage.success(t('system.plugin.installSuccess'))
    uploadVisible.value = false
    uploadingFile.value = null
    fetchData()
  } catch {
    // axios interceptor already displayed the error message.
  } finally {
    uploading.value = false
  }
}

// ---- Restart ----
async function handleRestart() {
  try {
    await ElMessageBox.confirm(
      t('system.plugin.restartConfirm'),
      t('system.plugin.restartTitle'),
      { type: 'warning', confirmButtonText: t('system.plugin.confirmRestart'), cancelButtonText: t('common.action.cancel') }
    )
  } catch {
    return
  }

  restarting.value = true
  ElMessage.info(t('system.plugin.restarting'))
  let oldPid: number | undefined
  let restartRequestFailed = false
  try {
    const result: any = await restartServer()
    oldPid = result?.old_pid
  } catch {
    // Response may fail if the server is already shutting down — expected.
    // But it may also fail BEFORE the restart was ever issued (network error,
    // permission error...), in which case we must not blindly wait.
    restartRequestFailed = true
  }

  const result = await pollBackendHealth({ oldPid, requestFailed: restartRequestFailed })
  if (result.recovered) {
    ElMessage.success(t('system.plugin.backendRecoveredRefreshing'))
    await new Promise((resolve) => setTimeout(resolve, 500))
    window.location.reload()
  } else {
    ElMessage.error(t('system.plugin.recoveryTimeout'))
    restarting.value = false
  }
}

// ---- Delete ----
async function handleDelete(item: PluginRow) {
  try {
    await ElMessageBox.confirm(
      t('system.plugin.deleteConfirm', { name: item.display_name || item.name }),
      t('system.plugin.deleteTitle'),
      { type: 'warning', confirmButtonText: t('system.plugin.confirmDelete'), cancelButtonText: t('common.action.cancel') }
    )
  } catch {
    return
  }

  try {
    await deletePlugin(item.id)
    await refreshRuntimeMenus()
    ElMessage.success(t('system.plugin.deletedSuccess'))
    fetchData()
  } catch {
    // axios interceptor already displayed the error message.
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-card {
  border-radius: 8px;
}
.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
  align-items: center;
}
.toolbar-right {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

/* Plugin card grid */
.plugin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
  min-height: 200px;
}

.plugin-card {
  border-radius: 12px;
  transition: all 0.25s ease;
}
.plugin-card:hover {
  box-shadow: 0 4px 20px rgba(90, 103, 245, 0.12);
}
.plugin-card.plugin-disabled {
  opacity: 0.65;
}

.plugin-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.plugin-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: #edf2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.plugin-info {
  flex: 1;
  min-width: 0;
}
.plugin-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2b2b2b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.plugin-version {
  font-size: 12px;
  color: #909399;
}

.plugin-desc {
  font-size: 13px;
  color: #606266;
  margin: 0 0 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.plugin-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.plugin-path {
  font-size: 12px;
  color: #c0c4cc;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.plugin-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #f0f2f5;
  padding-top: 8px;
}
.footer-actions {
  display: flex;
  gap: 4px;
}
.plugin-time {
  font-size: 12px;
  color: #c0c4cc;
}

.config-editor :deep(.el-textarea__inner) {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.pagination {
  margin-top: 14px;
  justify-content: flex-end;
}
</style>
