<template>
  <div class="hermes-profiles">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button :icon="Refresh" :loading="loading" @click="refreshAll">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建 Profile</el-button>
      </div>
      <el-tag v-if="activeName" type="success" effect="light">当前活跃：{{ activeName }}</el-tag>
    </div>

    <!-- Profile 表格 -->
    <div class="table-card">
      <el-table :data="profiles" v-loading="loading" border stripe>
        <el-table-column label="名称" min-width="180">
          <template #default="{ row }">
            <div class="name-cell">
              <span class="name-text">{{ row.name }}</span>
              <el-tag v-if="row.is_active || row.name === activeName" type="success" size="small" effect="dark">当前</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <span :class="{ 'desc-empty': !row.description }">{{ row.description || '暂无描述' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active || row.name === activeName ? 'success' : 'info'" size="small" effect="plain">
              {{ row.is_active || row.name === activeName ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.model" class="model-text">{{ row.model }}</span>
            <span v-else class="desc-empty">—</span>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170" :formatter="formatTime" />
        <el-table-column label="操作" width="130" fixed="right" align="center">
          <template #default="{ row }">
<el-button
              v-if="!(row.is_active || row.name === activeName)"
              size="small"
              type="success"
              :icon="Check"
              :loading="actingId === row.name"
              @click="switchActive(row)"
            >
              设为活跃
            </el-button>
            <el-tag v-else type="success" size="small" effect="dark">当前活跃</el-tag>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无 Profile" :image-size="80" />
        </template>
      </el-table>
    </div>

    <!-- 新建 Profile 弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建 Profile"
      width="480px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="Profile 名称" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="Profile 描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="createProfile">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElTag,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElMessageBox,
  ElRadioGroup,
  ElRadio,
} from 'element-plus'
import { Refresh, Plus, Check } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

// ── 类型 ──────────────────────────────────────────
interface Profile {
  name?: string
  description?: string
  is_active?: boolean
  model?: string
  created_at?: string
  [key: string]: any
}

// ── 状态 ──────────────────────────────────────────
const loading = ref(false)
const saving = ref(false)
const profiles = ref<Profile[]>([])
const activeName = ref('')
const dialogVisible = ref(false)
const actingId = ref('')

const form = ref({
  name: '',
  description: '',
})

// ── 数据加载 ──────────────────────────────────────
async function fetchProfiles() {
  loading.value = true
  try {
    const res: any = await hermes.getProfiles()
    profiles.value = res?.profiles ?? res ?? []
  } catch (e: any) {
    ElMessage.error(`加载 Profile 失败: ${e.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
}

async function fetchActiveProfile() {
  try {
    const res: any = await hermes.getActiveProfile()
    activeName.value = res?.name ?? ''
    if (activeName.value) {
      const found = profiles.value.find((p) => p.name === activeName.value)
      if (found) found.is_active = true
    }
  } catch {
    // 无活跃 Profile 时静默
  }
}

async function refreshAll() {
  await fetchProfiles()
  await fetchActiveProfile()
}

// ── 新建 ──────────────────────────────────────────
function openCreate() {
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

async function createProfile() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入 Profile 名称')
    return
  }
  saving.value = true
  try {
    await hermes.createProfile({
      name: form.value.name.trim(),
      description: form.value.description.trim(),
    })
    ElMessage.success('已创建')
    dialogVisible.value = false
    refreshAll()
  } catch (e: any) {
    ElMessage.error(`创建失败: ${e.message || '未知错误'}`)
  } finally {
    saving.value = false
  }
}

// ── 切换活跃 Profile ──────────────────────────────
async function switchActive(row: Profile) {
  try {
    await ElMessageBox.confirm(
      `确定将「${row.name}」设为当前活跃 Profile 吗？`,
      '切换确认',
      {
        type: 'warning',
        confirmButtonText: '设为活跃',
        cancelButtonText: '取消',
      },
    )
  } catch {
    return
  }
  actingId.value = row.name ?? ''
  try {
    await hermes.setActiveProfile(row.name ?? '')
    activeName.value = row.name ?? ''
    profiles.value.forEach((p) => {
      p.is_active = p.name === row.name
    })
    ElMessage.success(`已切换到「${row.name}」`)
  } catch (e: any) {
    ElMessage.error(`切换失败: ${e.message || '未知错误'}`)
  } finally {
    actingId.value = ''
  }
}

// ── 工具 ──────────────────────────────────────────
function formatTime(_row: any, _col: any, val: any): string {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d.getTime())) return String(val)
  return d.toLocaleString('zh-CN', { hour12: false })
}

// ── 生命周期 ──────────────────────────────────────
onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.hermes-profiles {
  padding: 4px 0 20px;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.toolbar-left {
  display: flex;
  gap: 8px;
}
.table-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 8px;
}
.name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.name-text {
  font-weight: 500;
  color: var(--el-text-color-primary);
}
.model-text {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
}
.desc-empty {
  color: var(--el-text-color-placeholder);
}
</style>