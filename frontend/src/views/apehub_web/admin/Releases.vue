<template>
  <div class="releases-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card total">
        <div class="stat-icon"><el-icon><Box /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ list.length }}</div>
          <div class="stat-label">版本总数</div>
        </div>
      </div>
      <div class="stat-card latest">
        <div class="stat-icon"><el-icon><Star /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ latestVersion || '暂无' }}</div>
          <div class="stat-label">最新版本</div>
        </div>
      </div>
      <div class="stat-card downloads">
        <div class="stat-icon"><el-icon><Download /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ totalDownloads }}</div>
          <div class="stat-label">累计下载</div>
        </div>
      </div>
      <div class="stat-card online">
        <div class="stat-icon"><el-icon><CircleCheck /></el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ onlineCount }}</div>
          <div class="stat-label">上架中</div>
        </div>
      </div>
    </div>

    <!-- 主卡片 -->
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>安装下载版本管理</span>
          <span class="header-note">发布 ApeAdmin 版本 · 上传 ZIP 安装包 · 官网「安装下载」页展示</span>
          <el-button type="primary" :icon="Plus" @click="openCreate">新增版本</el-button>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="版本" width="110">
          <template #default="{ row }">
            <div class="version-cell">
              <el-tag type="primary" effect="dark" round>v{{ row.version }}</el-tag>
              <el-tag v-if="row.is_latest" type="danger" size="small" effect="plain" round class="latest-tag">最新</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="安装包" width="200">
          <template #default="{ row }">
            <div v-if="row.file_name" class="file-cell">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ row.file_name }}</span>
              <small>{{ formatSize(row.file_size) }}</small>
            </div>
            <el-tag v-else type="info" size="small">未上传</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="下载" width="90" align="center">
          <template #default="{ row }">{{ row.download_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" effect="light" round>
              {{ row.enabled ? '上架中' : '已下线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="150">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openUpload(row)">上传包</el-button>
            <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.enabled" text type="warning" @click="toggleEnabled(row, false)">下线</el-button>
            <el-button v-else text type="success" @click="toggleEnabled(row, true)">上架</el-button>
            <el-button text type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无版本，点击右上角「新增版本」创建" /></template>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="editVisible" :title="form.id ? '编辑发布版本' : '新增发布版本'" width="560px" destroy-on-close>
      <el-form :model="form" label-width="90px">
        <el-form-item label="版本号" required>
          <el-input v-model="form.version" placeholder="如 1.7.0" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="如 ApeAdmin 1.7.0 正式版" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="一句话介绍该版本" />
        </el-form-item>
        <el-form-item label="更新日志">
          <el-input v-model="form.changelog" type="textarea" :rows="6" placeholder="支持换行，每行一条更新内容" />
        </el-form-item>
        <el-form-item label="标记最新">
          <el-switch v-model="form.is_latest" />
          <span class="form-tip">勾选后官网下载区将标注「最新」</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- 上传安装包弹窗 -->
    <el-dialog v-model="uploadVisible" :title="`上传安装包 - v${uploadTarget?.version || ''}`" width="480px" destroy-on-close>
      <el-upload
        drag
        :auto-upload="false"
        :limit="1"
        accept=".zip"
        :on-change="onFileChange"
        :on-remove="onFileRemove"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将 ZIP 安装包拖到此处，或 <em>点击选择</em></div>
        <template #tip>
          <div class="el-upload__tip">仅支持 ZIP 格式，最大 200MB</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" :disabled="!selectedFile" @click="doUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Box, Star, Download, CircleCheck, Plus, Document, UploadFilled } from '@element-plus/icons-vue'
import {
  getAdminReleases, createAdminRelease, updateAdminRelease, deleteAdminRelease, uploadAdminReleasePackage,
} from '@/api/apehub_web'

const list = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)

// 统计
const latestVersion = computed(() => {
  const l = list.value.find((r) => r.is_latest)
  return l ? `v${l.version}` : (list.value[0] ? `v${list.value[0].version}` : '暂无')
})
const totalDownloads = computed(() => list.value.reduce((s, r) => s + (Number(r.download_count) || 0), 0))
const onlineCount = computed(() => list.value.filter((r) => r.enabled).length)

const formatSize = (size: number) =>
  size >= 1024 * 1024 ? `${(size / 1024 / 1024).toFixed(2)} MB` : `${Math.ceil((size || 0) / 1024)} KB`

const formatDate = (d: string) => (d ? d.replace('T', ' ').slice(0, 16) : '-')

// 弹窗表单
const editVisible = ref(false)
const form = ref<any>({ id: 0, version: '', title: '', description: '', changelog: '', is_latest: false })
const openCreate = () => {
  form.value = { id: 0, version: '', title: '', description: '', changelog: '', is_latest: true }
  editVisible.value = true
}
const openEdit = (row: any) => {
  form.value = {
    id: row.id, version: row.version, title: row.title || '', description: row.description || '',
    changelog: row.changelog || '', is_latest: !!row.is_latest,
  }
  editVisible.value = true
}

const save = async () => {
  if (!form.value.version.trim()) return ElMessage.warning('请填写版本号')
  saving.value = true
  try {
    if (form.value.id) {
      await updateAdminRelease(form.value.id, {
        version: form.value.version, title: form.value.title, description: form.value.description,
        changelog: form.value.changelog, is_latest: form.value.is_latest,
      })
      ElMessage.success('版本已更新')
    } else {
      await createAdminRelease({
        version: form.value.version, title: form.value.title, description: form.value.description,
        changelog: form.value.changelog, is_latest: form.value.is_latest,
      })
      ElMessage.success('版本已创建，请上传安装包')
    }
    editVisible.value = false
    await loadList()
  } finally { saving.value = false }
}

// 上传
const uploadVisible = ref(false)
const uploadTarget = ref<any>(null)
const selectedFile = ref<File | null>(null)
const openUpload = (row: any) => {
  uploadTarget.value = row
  selectedFile.value = null
  uploadVisible.value = true
}
const onFileChange = (file: any) => {
  selectedFile.value = file.raw
  if (!file.name.endsWith('.zip')) {
    ElMessage.warning('仅支持 ZIP 安装包')
    selectedFile.value = null
  }
}
const onFileRemove = () => { selectedFile.value = null }
const doUpload = async () => {
  if (!selectedFile.value || !uploadTarget.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    await uploadAdminReleasePackage(uploadTarget.value.id, fd)
    ElMessage.success('安装包上传成功')
    uploadVisible.value = false
    await loadList()
  } finally { uploading.value = false }
}

// 上下架
const toggleEnabled = async (row: any, enabled: boolean) => {
  await updateAdminRelease(row.id, { enabled })
  ElMessage.success(enabled ? '已上架' : '已下线')
  await loadList()
}

// 删除
const remove = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除 v${row.version} 发布版本吗？安装包文件将一并删除，不可恢复。`, '删除确认', { type: 'warning' })
  } catch { return }
  await deleteAdminRelease(row.id)
  ElMessage.success('已删除')
  await loadList()
}

// 加载列表
const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminReleases()
    list.value = data.items || []
  } finally { loading.value = false }
}

onMounted(loadList)
</script>

<style scoped>
.releases-admin {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff;
}
.stat-card.latest .stat-icon { background: linear-gradient(135deg, #f59e0b, #ef4444); }
.stat-card.downloads .stat-icon { background: linear-gradient(135deg, #4f46e5, #7c3aed); }
.stat-card.online .stat-icon { background: linear-gradient(135deg, #10b981, #059669); }
.stat-card:first-child .stat-icon { background: linear-gradient(135deg, #6366f1, #4f46e5); }
.stat-body { display: flex; flex-direction: column; }
.stat-value { font-size: 22px; font-weight: 700; line-height: 1.2; }
.stat-label { font-size: 12px; color: var(--el-text-color-secondary); }

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.card-header .header-note {
  flex: 1;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.version-cell { display: flex; align-items: center; gap: 6px; }
.latest-tag { margin-left: 2px; }
.file-cell { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.file-cell .file-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 110px; }
.file-cell small { color: var(--el-text-color-secondary); }
.form-tip { margin-left: 8px; font-size: 12px; color: var(--el-text-color-secondary); }
</style>