<template>
  <el-dialog
    v-model="visible"
    title="版本更新"
    width="520px"
    :close-on-click-modal="false"
    :close-on-press-escape="!uploading"
    :show-close="!uploading"
    append-to-body
    class="version-update-dialog"
  >
    <!-- Current version info -->
    <div v-loading="loading" class="version-info">
      <div class="version-row">
        <span class="version-label">当前版本</span>
        <span class="version-value">{{ versionData?.current_version || '--' }}</span>
      </div>
      <div class="version-row">
        <span class="version-label">应用名称</span>
        <span class="version-value">{{ versionData?.app_name || '--' }}</span>
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
      accept=".tar.gz,.tgz"
      :disabled="uploading"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        拖拽部署包到此处，或<em>点击选择</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          仅支持 .tar.gz 格式部署包，最大 200MB
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
        <el-button @click="handleClose" :disabled="uploading">关闭</el-button>
        <el-button
          type="primary"
          :loading="uploading"
          :disabled="!selectedFile || !!successMsg"
          @click="handleUpload"
        >
          {{ uploading ? '上传中...' : '开始更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadFiles, UploadRawFile } from 'element-plus'
import { getSystemVersion, uploadSystemUpdate } from '@/api'

const props = defineProps<{
  modelValue: boolean
}>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

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

async function fetchVersion() {
  loading.value = true
  try {
    const res = await getSystemVersion()
    versionData.value = res.data?.data || res.data
  } catch (err: any) {
    // silently fail, show -- placeholders
    console.error('Failed to fetch version:', err)
  } finally {
    loading.value = false
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
  // Validate extension
  const name = raw.name.toLowerCase()
  if (!name.endsWith('.tar.gz') && !name.endsWith('.tgz')) {
    errorMsg.value = '请选择 .tar.gz 格式的部署包'
    selectedFile.value = null
    uploadRef.value?.clearFiles()
    return
  }
  // Validate size (200MB)
  if (raw.size > 200 * 1024 * 1024) {
    errorMsg.value = '文件大小不能超过 200MB'
    selectedFile.value = null
    uploadRef.value?.clearFiles()
    return
  }
  errorMsg.value = ''
  selectedFile.value = raw
}

function handleExceed(files: File[]) {
  ElMessage.warning('只能选择一个文件，已替换为新文件')
  uploadRef.value?.clearFiles()
  const file = files[0]
  uploadRef.value?.handleStart(file)
}

async function handleUpload() {
  if (!selectedFile.value) return

  uploading.value = true
  progress.value = 0
  progressStatus.value = ''
  progressText.value = '准备上传...'
  errorMsg.value = ''
  successMsg.value = ''

  try {
    const res = await uploadSystemUpdate(selectedFile.value, (pct: number) => {
      progress.value = pct
      if (pct < 100) {
        progressText.value = `上传中... ${pct}%`
      } else {
        progressText.value = '上传完成，正在处理...'
        progressStatus.value = 'success'
      }
    })

    progress.value = 100
    progressStatus.value = 'success'
    progressText.value = '更新完成，后端正在重启...'
    successMsg.value = res.data?.message || '版本更新完成，后端正在重启，请等待约 5 秒后刷新页面'

    // Poll health check after 3 seconds
    setTimeout(() => {
      progressText.value = '等待后端重启完成...'
      pollHealth()
    }, 3000)
  } catch (err: any) {
    progressStatus.value = 'exception'
    errorMsg.value = err?.response?.data?.detail?.msg
      || err?.response?.data?.detail
      || err?.message
      || '上传失败，请重试'
    uploading.value = false
  }
}

// Poll health endpoint until backend comes back online
let pollCount = 0
const MAX_POLLS = 30 // 30 * 2s = 60s max wait

function pollHealth() {
  const check = async () => {
    pollCount++
    if (pollCount > MAX_POLLS) {
      progressText.value = '后端重启超时，请手动刷新页面'
      uploading.value = false
      return
    }
    try {
      const resp = await fetch('/api/v1/health', {
        method: 'GET',
        headers: { 'Cache-Control': 'no-cache' },
      })
      if (resp.ok) {
        progressText.value = '后端已恢复，正在刷新页面...'
        uploading.value = false
        // Auto refresh after a short delay
        setTimeout(() => {
          window.location.reload()
        }, 1000)
        return
      }
    } catch {
      // Backend still restarting
    }
    setTimeout(check, 2000)
  }
  setTimeout(check, 2000)
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
  pollCount = 0
  uploadRef.value?.clearFiles()
}

// Reset poll count when dialog opens
watch(() => props.modelValue, (val) => {
  if (val) {
    pollCount = 0
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
