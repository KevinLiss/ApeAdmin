<template>
  <el-dialog
    v-model="visible"
    :title="t('common.versionUpdate.title')"
    width="520px"
    :close-on-click-modal="false"
    :close-on-press-escape="!uploading"
    :show-close="!uploading"
    append-to-body
    class="version-update-dialog"
  >
    <!-- Current version info -->
    <div v-loading="loading" class="version-info">
      <!-- Update-available banner -->
      <el-alert
        v-if="updateInfo?.has_update"
        type="warning"
        :closable="false"
        show-icon
        class="update-banner"
      >
        <template #title>
          <span>{{ t('common.versionUpdate.availableBanner', { version: updateInfo.latest_version }) }}</span>
          <el-button
            type="primary"
            size="small"
            :loading="downloading"
            :disabled="uploading"
            class="one-click-btn"
            @click="handleOneClickUpdate"
          >
            {{ downloading ? t('common.versionUpdate.downloading') : t('common.versionUpdate.oneClickUpdate') }}
          </el-button>
        </template>
      </el-alert>
      <div class="version-row">
        <span class="version-label">{{ t('common.versionUpdate.currentVersion') }}</span>
        <span class="version-value">{{ versionData?.current_version || '--' }}</span>
      </div>
      <div class="version-row">
        <span class="version-label">{{ t('common.versionUpdate.appName') }}</span>
        <span class="version-value">{{ versionData?.app_name || '--' }}</span>
      </div>
      <div class="version-row">
        <span class="version-label">{{ t('common.versionUpdate.runtimeType') }}</span>
        <span class="version-value">{{ runtimeLabel }}</span>
      </div>
      <div class="version-row">
        <span class="version-label">Python</span>
        <span class="version-value">{{ versionData?.python_version || '--' }}</span>
      </div>
    </div>

    <!-- Upload area -->
    <el-upload
      ref="uploadRef"
      class="version-upload"
      drag
      :auto-upload="false"
      :limit="1"
      :on-change="handleFileChange"
      :on-exceed="handleExceed"
      accept=".tar.gz,.tgz,.zip"
      :disabled="uploading"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        {{ t('common.versionUpdate.dragFileHere') }}<em>{{ t('common.versionUpdate.clickToSelect') }}</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          {{ t('common.versionUpdate.uploadTip') }}
        </div>
      </template>
    </el-upload>

    <!-- Progress bar -->
    <div v-if="uploading" class="upload-progress">
      <el-progress :percentage="progress" :status="progressStatus" />
      <p class="progress-text">{{ progressText }}</p>
    </div>

    <!-- Error message -->
    <el-alert
      v-if="errorMsg"
      :title="errorMsg"
      type="error"
      :closable="false"
      show-icon
      class="upload-error"
    />

    <!-- Success message -->
    <el-alert
      v-if="successMsg"
      :title="successMsg"
      type="success"
      :closable="false"
      show-icon
      class="upload-success"
    />

    <!-- Actions -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="uploading">{{ t('common.action.close') }}</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="!selectedFile || !!successMsg"
          @click="handleUpload"
        >
          {{ uploading ? t('common.versionUpdate.uploading') : t('common.versionUpdate.startUpdate') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import type { UploadFile, UploadFiles, UploadRawFile } from 'element-plus'
import { getSystemVersion, checkSystemUpdate, uploadSystemUpdate } from '@/api'
import { pollBackendHealth } from '@/utils/restart'

// 轻量 MD5 实现（自包含，无第三方依赖）：一键更新包完整性校验用
async function md5Hex(blob: Blob): Promise<string> {
  const data = new Uint8Array(await blob.arrayBuffer())
  // --- MD5 算法（RFC 1321）---
  const S = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]
  const K = new Int32Array(64)
  for (let i = 0; i < 64; i++) K[i] = Math.floor(Math.abs(Math.sin(i + 1)) * 4294967296)
  const rotl = (x: number, c: number) => (x << c) | (x >>> (32 - c))
  let a = 0x67452301, b = 0xefcdab89, c = 0x98badcfe, d = 0x10325476
  const padLen = ((data.length + 8) >> 6) + 1
  const total = padLen << 6
  const buf = new Uint8Array(total)
  buf.set(data)
  buf[data.length] = 0x80
  const bitLen = data.length * 8
  const dv = new DataView(buf.buffer)
  dv.setUint32(total - 8, bitLen >>> 0, true)
  dv.setUint32(total - 4, Math.floor(bitLen / 4294967296), true)
  for (let off = 0; off < total; off += 64) {
    const M = new Int32Array(16)
    for (let i = 0; i < 16; i++) M[i] = dv.getInt32(off + i * 4, true)
    let A = a, B = b, C = c, D = d
    for (let i = 0; i < 64; i++) {
      let F: number, g: number
      if (i < 16) { F = (B & C) | (~B & D); g = i }
      else if (i < 32) { F = (D & B) | (~D & C); g = (5 * i + 1) & 15 }
      else if (i < 48) { F = B ^ C ^ D; g = (3 * i + 5) & 15 }
      else { F = C ^ (B | ~D); g = (7 * i) & 15 }
      F = (F + A + K[i] + M[g]) | 0
      A = D; D = C; C = B
      B = (B + rotl(F, S[i])) | 0
    }
    a = (a + A) | 0; b = (b + B) | 0; c = (c + C) | 0; d = (d + D) | 0
  }
  const out = new Uint8Array(16)
  new DataView(out.buffer).setUint32(0, a >>> 0, true)
  new DataView(out.buffer).setUint32(4, b >>> 0, true)
  new DataView(out.buffer).setUint32(8, c >>> 0, true)
  new DataView(out.buffer).setUint32(12, d >>> 0, true)
  return Array.from(out).map(x => x.toString(16).padStart(2, '0')).join('')
}

const props = defineProps<{
  modelValue: boolean
}>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const { t } = useI18n()

const visible = ref(props.modelValue)
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    fetchVersion()
  }
})
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// ---- Version info ----
const loading = ref(false)
const versionData = ref<any>(null)

// Base-stack identity label: backend reports runtime="python"|"go".
const runtimeLabel = computed(() => {
  const rt = String(versionData.value?.runtime || 'python').toLowerCase()
  if (rt === 'go') return t('common.versionUpdate.runtimeGo')
  if (rt === 'python') return t('common.versionUpdate.runtimePython')
  if (rt === 'java') return t('common.versionUpdate.runtimeJava')
  return rt || '--'
})

async function fetchVersion() {
  loading.value = true
  try {
    const res: any = await getSystemVersion()
    // axios 拦截器已解包标准信封，res 就是 data 本体（含 current_version 等字段）
    versionData.value = res || null
  } catch (err: any) {
    // silently fail, show -- placeholders
    console.error('Failed to fetch version:', err)
  } finally {
    loading.value = false
  }
  // Probe ApeHub for a newer release (best-effort, never blocks the dialog)
  try {
    const probe: any = await checkSystemUpdate()
    if (probe?.reachable) updateInfo.value = probe
  } catch {
    /* offline / older backend — hide the banner */
  }
}

// ---- One-click update: confirm → download → verify MD5 → upload ----
const updateInfo = ref<any>(null)
const downloading = ref(false)

function fmtSize(bytes: number): string {
  if (!bytes || bytes <= 0) return ''
  return bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(2)} MB` : `${Math.round(bytes / 1024)} KB`
}

async function confirmOneClickUpdate(): Promise<boolean> {
  const v = updateInfo.value?.latest_version || '--'
  try {
    await ElMessageBox.confirm(t('common.versionUpdate.confirmOneClick', { version: v }), t('common.versionUpdate.confirmTitle'), {
      confirmButtonText: t('common.versionUpdate.confirmProceed'),
      cancelButtonText: t('common.versionUpdate.confirmCancel'),
      type: 'warning',
      dangerouslyUseHTMLString: false,
    })
    return true
  } catch {
    return false // 用户取消
  }
}

async function handleOneClickUpdate() {
  const url = updateInfo.value?.download_url
  if (!url) return
  // 1) 确认交互：明确告知备份/中断时长，避免误点直接触发服务重启
  if (!(await confirmOneClickUpdate())) return
  downloading.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const resp = await fetch(url, { credentials: 'omit' })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const blob = await resp.blob()
    const file = new File([blob], `apeadmin-base-${updateInfo.value.latest_version}.zip`, {
      type: 'application/zip',
    })
    if (file.size > 200 * 1024 * 1024) {
      errorMsg.value = t('common.versionUpdate.fileTooLarge')
      return
    }
    // 2) 下载后校验：大小对得上才继续；服务端提供 md5 时逐字节校验
    const expectedSize = Number(updateInfo.value?.file_size) || 0
    if (expectedSize > 0 && file.size !== expectedSize) {
      errorMsg.value = t('common.versionUpdate.downloadVerifyFailed')
      return
    }
    if (updateInfo.value?.file_md5) {
      progressText.value = t('common.versionUpdate.downloadedVerifying', { size: fmtSize(file.size) })
      const local = await md5Hex(blob)
      if (local.toLowerCase() !== String(updateInfo.value.file_md5).toLowerCase()) {
        errorMsg.value = t('common.versionUpdate.md5Mismatch')
        return
      }
    }
    selectedFile.value = file
    await handleUpload()
  } catch (err: any) {
    errorMsg.value = err?.message || t('common.versionUpdate.downloadFailed')
  } finally {
    downloading.value = false
  }
}

// ---- Upload ----
const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const progress = ref(0)
const progressStatus = ref<any>('')
const progressText = ref('')
const errorMsg = ref('')
const successMsg = ref('')

function handleFileChange(file: UploadFile, files: UploadFiles) {
  // Only keep the last file
  if (files.length > 1) {
    files.splice(0, files.length - 1)
  }
  const raw = file.raw as UploadRawFile
  // Validate extension (.tar.gz/.tgz traditional, .zip = ApeHub release format)
  const name = raw.name.toLowerCase()
  if (!name.endsWith('.tar.gz') && !name.endsWith('.tgz') && !name.endsWith('.zip')) {
    errorMsg.value = t('common.versionUpdate.invalidFileFormat')
    selectedFile.value = null
    uploadRef.value?.clearFiles()
    return
  }
  // Validate size (200MB)
  if (raw.size > 200 * 1024 * 1024) {
    errorMsg.value = t('common.versionUpdate.fileTooLarge')
    selectedFile.value = null
    uploadRef.value?.clearFiles()
    return
  }
  errorMsg.value = ''
  selectedFile.value = raw
}

function handleExceed(files: File[]) {
  ElMessage.warning(t('common.versionUpdate.fileReplaced'))
  uploadRef.value?.clearFiles()
  const file = files[0]
  uploadRef.value?.handleStart(file)
}

async function handleUpload() {
  if (!selectedFile.value) return

  // 手动上传路径同样加确认交互（与一键更新同文案体系）
  if (!(await confirmManualUpload())) return

  uploading.value = true
  progress.value = 0
  progressStatus.value = ''
  progressText.value = t('common.versionUpdate.preparing')
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const res: any = await uploadSystemUpdate(selectedFile.value, (pct: number) => {
      progress.value = pct
      if (pct < 100) {
        progressText.value = t('common.versionUpdate.uploadingPercent', { pct })
      } else {
        progressText.value = t('common.versionUpdate.uploadDoneProcessing')
        progressStatus.value = 'success'
      }
    })

    progress.value = 100
    progressStatus.value = 'success'
    progressText.value = t('common.versionUpdate.updateDoneRestarting')
    // axios 拦截器已解包标准信封：res 直接就是 data（含 old_pid / message）
    successMsg.value = res?.message || t('common.versionUpdate.successMsg')

    // Poll health: wait for the new process to come up (old PID known).
    progressText.value = t('common.versionUpdate.waitingRestart')
    const oldPid = res?.old_pid
    const pollResult = await pollBackendHealth({
      oldPid,
      maxRetries: 30,
      interval: 2000,
      onProbe: (isDown, _pid, attempt) => {
        if (isDown) {
          progressText.value = t('common.versionUpdate.waitingRestartAttempt', { attempt })
        }
      },
    })
    if (pollResult.recovered) {
      progressText.value = t('common.versionUpdate.recovered')
      uploading.value = false
      setTimeout(() => window.location.reload(), 1000)
    } else {
      progressText.value = t('common.versionUpdate.restartTimeout')
      uploading.value = false
    }
    } catch (err: any) {
    progressStatus.value = 'exception'
    // Backend returns { code, msg, data } in the standard envelope.
    errorMsg.value =
      err?.response?.data?.msg
      || err?.response?.data?.detail?.msg
      || err?.response?.data?.detail
      || err?.message
      || t('common.message.uploadFailedRetry')
    uploading.value = false
  }
}

async function confirmManualUpload(): Promise<boolean> {
  try {
    await ElMessageBox.confirm(
      `${t('common.versionUpdate.confirmUpload')}\n${t('common.versionUpdate.confirmBackupNote')}`,
      t('common.versionUpdate.confirmTitle'),
      {
        confirmButtonText: t('common.versionUpdate.confirmProceed'),
        cancelButtonText: t('common.versionUpdate.confirmCancel'),
        type: 'warning',
      },
    )
    return true
  } catch {
    return false
  }
}

function handleClose() {
  if (uploading.value) return
  visible.value = false
  // Reset state
  selectedFile.value = null
  uploading.value = false
  progress.value = 0
  progressStatus.value = ''
  progressText.value = ''
  errorMsg.value = ''
  successMsg.value = ''
  uploadRef.value?.clearFiles()
}

// Reset state when dialog opens
watch(() => props.modelValue, (val) => {
  if (val) {
    errorMsg.value = ''
    successMsg.value = ''
    progress.value = 0
    progressText.value = ''
    uploading.value = false
  }
})
</script>

<style scoped>
.version-update-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.version-info {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.version-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.version-row + .version-row {
  border-top: 1px solid #eef0f4;
}

.version-label {
  font-size: 13px;
  color: #909399;
}

.version-value {
  font-size: 14px;
  font-weight: 500;
  color: #2b2b2b;
}

.version-upload {
  width: 100%;
}

.version-upload :deep(.el-upload-dragger) {
  padding: 20px;
  border-radius: 8px;
}

.upload-progress {
  margin-top: 16px;
}

.progress-text {
  margin: 8px 0 0;
  font-size: 12px;
  color: #909399;
  text-align: center;
}

.upload-error,
.upload-success {
  margin-top: 12px;
}

.update-banner {
  margin-bottom: 12px;
}

.update-banner :deep(.el-alert__title) {
  display: flex;
  align-items: center;
  gap: 10px;
}

.one-click-btn {
  flex-shrink: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

<style>
html.dark .version-info {
  background: #2e3344;
}
html.dark .version-row + .version-row {
  border-top-color: #3a3f52;
}
html.dark .version-label {
  color: #8a90a8;
}
html.dark .version-value {
  color: #e6e8f0;
}
</style>
