<template>
  <div class="hermes-cron">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button :icon="Refresh" :loading="loading" @click="fetchJobs">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新建任务</el-button>
      </div>
      <el-tag v-if="jobs.length" type="info" effect="plain">{{ jobs.length }} 个任务</el-tag>
    </div>

    <!-- 蓝图区 -->
    <div v-if="blueprints.length" class="card-section">
      <div class="section-head">
        <span class="section-title">蓝图模板</span>
        <span class="section-hint">点击「使用」快速创建任务</span>
      </div>
      <div class="bp-grid">
        <div v-for="bp in blueprints" :key="bp.name" class="bp-card">
          <div class="bp-name">{{ bp.name }}</div>
          <div class="bp-desc">{{ bp.description || '暂无描述' }}</div>
          <div class="bp-foot">
            <el-tag size="small" type="info" effect="plain">{{ bp.schedule }}</el-tag>
            <el-button size="small" type="primary" plain :icon="Plus" @click="useBlueprint(bp)">使用</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 交付目标区 -->
    <div v-if="targets.length" class="card-section">
      <div class="section-head">
        <span class="section-title">交付目标</span>
        <span class="section-hint">点击目标即可新建任务并预填 prompt</span>
      </div>
      <div class="target-list">
        <el-tag
          v-for="(t, i) in targets"
          :key="i"
          class="target-tag"
          effect="plain"
          @click="pickTarget(t)"
        >
          {{ targetLabel(t) }}
        </el-tag>
      </div>
    </div>

    <!-- 任务表格 -->
    <div class="card-section table-card">
      <el-table :data="jobs" v-loading="loading" border stripe>
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="schedule" label="Cron 表达式" min-width="130" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.enabled"
              :loading="row._toggling"
              @change="(v) => toggleEnabled(row, v)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="last_run" label="上次运行" min-width="170" :formatter="formatRunTime" />
        <el-table-column prop="next_run" label="下次运行" min-width="170" :formatter="formatRunTime" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :icon="Edit" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="removeJob(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无定时任务" :image-size="80" />
        </template>
      </el-table>
    </div>

    <!-- 新建 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑定时任务' : '新建定时任务'"
      width="600px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="110px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="例如：每日早报" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="Cron 表达式" required>
          <el-input v-model="form.schedule" placeholder="例如：0 8 * * *（每日 8 点）" />
        </el-form-item>
        <el-form-item label="Prompt 内容">
          <el-input v-model="form.prompt" type="textarea" :rows="4" placeholder="任务要执行的内容提示词" />
          <div v-if="targets.length" class="prompt-targets">
            <span class="prompt-targets-label">交付目标：</span>
            <el-tag
              v-for="(t, i) in targets"
              :key="i"
              size="small"
              effect="plain"
              class="mini-target"
              @click="appendTarget(t)"
            >
              + {{ targetLabel(t) }}
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="模型">
          <el-select v-model="form.model" placeholder="选择模型（可选）" clearable filterable allow-create>
            <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveJob">保存</el-button>
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
  ElSelect,
  ElOption,
  ElSwitch,
  ElMessage,
  ElMessageBox,
} from 'element-plus'
import { Refresh, Plus, Delete, Edit } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

// ── 类型 ──────────────────────────────────────────
interface CronJob {
  id?: string
  name?: string
  schedule?: string
  enabled?: boolean
  last_run?: string | null
  next_run?: string | null
  prompt?: string
  model?: string
  [key: string]: any
}

interface CronBlueprint {
  name: string
  description?: string
  schedule: string
  prompt?: string
  [key: string]: any
}

interface CronForm {
  id?: string
  name: string
  schedule: string
  prompt: string
  model?: string
  enabled: boolean
}

// ── 状态 ──────────────────────────────────────────
const loading = ref(false)
const saving = ref(false)
const jobs = ref<CronJob[]>([])
const blueprints = ref<CronBlueprint[]>([])
const targets = ref<any[]>([])
const modelOptions = ref<string[]>([])
const dialogVisible = ref(false)

const form = ref<CronForm>({
  name: '',
  schedule: '',
  prompt: '',
  model: '',
  enabled: true,
})

// ── 列表加载 ──────────────────────────────────────
async function fetchJobs() {
  loading.value = true
  try {
    const res: any = await hermes.getCronJobs()
    jobs.value = res?.jobs ?? res ?? []
  } catch (e: any) {
    ElMessage.error(`加载定时任务失败: ${e.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
}

async function fetchBlueprints() {
  try {
    const res: any = await hermes.getCronBlueprints()
    blueprints.value = res?.blueprints ?? []
  } catch {
    blueprints.value = []
  }
}

async function fetchTargets() {
  try {
    const res: any = await hermes.getCronDeliveryTargets()
    targets.value = res?.targets ?? []
  } catch {
    targets.value = []
  }
}

async function fetchModelOptions() {
  try {
    const res: any = await hermes.getModelOptions()
    const list = res?.models ?? res?.options ?? (Array.isArray(res) ? res : [])
    modelOptions.value = (list || [])
      .map((m: any) => (typeof m === 'string' ? m : m.name || m.id))
      .filter(Boolean)
  } catch {
    modelOptions.value = []
  }
}

// ── 弹窗 ──────────────────────────────────────────
function resetForm() {
  form.value = {
    name: '',
    schedule: '',
    prompt: '',
    model: '',
    enabled: true,
  }
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(row: CronJob) {
  form.value = {
    id: row.id,
    name: row.name || '',
    schedule: row.schedule || '',
    prompt: row.prompt || '',
    model: row.model || '',
    enabled: !!row.enabled,
  }
  dialogVisible.value = true
}

// ── 保存 ──────────────────────────────────────────
async function saveJob() {
  if (!form.value.name.trim()) {
    ElMessage.warning('请输入名称')
    return
  }
  if (!form.value.schedule.trim()) {
    ElMessage.warning('请输入 Cron 表达式')
    return
  }
  saving.value = true
  try {
    const payload: any = {
      name: form.value.name.trim(),
      schedule: form.value.schedule.trim(),
      prompt: form.value.prompt,
      enabled: form.value.enabled,
    }
    if (form.value.model) payload.model = form.value.model
    if (form.value.id) {
      await hermes.updateCronJob(form.value.id, payload)
      ElMessage.success('已更新')
    } else {
      await hermes.createCronJob(payload)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    fetchJobs()
  } catch (e: any) {
    ElMessage.error(`保存失败: ${e.message || '未知错误'}`)
  } finally {
    saving.value = false
  }
}

// ── 启用 / 禁用 ───────────────────────────────────
async function toggleEnabled(row: CronJob, val: any) {
  const enabled = !!val
  row._toggling = true
  try {
    await hermes.updateCronJob(row.id ?? '', { enabled })
    row.enabled = enabled
    ElMessage.success(enabled ? '已启用' : '已禁用')
  } catch (e: any) {
    row.enabled = !enabled
    ElMessage.error(`操作失败: ${e.message || '未知错误'}`)
  } finally {
    row._toggling = false
  }
}

// ── 删除 ──────────────────────────────────────────
async function removeJob(row: CronJob) {
  try {
    await ElMessageBox.confirm(`确定删除定时任务「${row.name}」吗？删除后不可恢复。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await hermes.deleteCronJob(row.id ?? '')
    ElMessage.success('已删除')
    fetchJobs()
  } catch (e: any) {
    ElMessage.error(`删除失败: ${e.message || '未知错误'}`)
  }
}

// ── 蓝图 / 交付目标 ───────────────────────────────
function useBlueprint(bp: CronBlueprint) {
  resetForm()
  form.value.name = bp.name
  form.value.schedule = bp.schedule || ''
  form.value.prompt = bp.prompt || ''
  dialogVisible.value = true
  ElMessage.info(`已载入蓝图「${bp.name}」，可调整后保存`)
}

function targetLabel(t: any): string {
  if (typeof t === 'string') return t
  return t?.name || t?.id || t?.label || JSON.stringify(t)
}

function targetPrompt(t: any): string {
  if (typeof t === 'string') return t
  const name = targetLabel(t)
  const desc = t?.description || t?.instructions || ''
  return desc ? `${name}：${desc}` : name
}

function pickTarget(t: any) {
  resetForm()
  form.value.prompt = targetPrompt(t)
  dialogVisible.value = true
  ElMessage.info('已预填交付目标，可补充任务内容后保存')
}

function appendTarget(t: any) {
  const targetText = targetPrompt(t)
  const cur = form.value.prompt
  form.value.prompt = cur ? `${cur}\n${targetText}` : targetText
}

// ── 工具 ──────────────────────────────────────────
function formatRunTime(_row: any, _col: any, val: any): string {
  if (!val) return '—'
  const d = new Date(val)
  if (isNaN(d.getTime())) return String(val)
  return d.toLocaleString('zh-CN', { hour12: false })
}

// ── 生命周期 ──────────────────────────────────────
onMounted(() => {
  fetchJobs()
  fetchBlueprints()
  fetchTargets()
  fetchModelOptions()
})
</script>

<style scoped>
.hermes-cron {
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
.card-section {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}
.section-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 12px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.section-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.bp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}
.bp-card {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: box-shadow 0.2s, border-color 0.2s;
}
.bp-card:hover {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  border-color: var(--el-color-primary-light-5);
}
.bp-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--el-text-color-primary);
}
.bp-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  min-height: 32px;
  line-height: 1.5;
}
.bp-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.target-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.target-tag {
  cursor: pointer;
}
.table-card {
  padding: 8px;
}
.prompt-targets {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.prompt-targets-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.mini-target {
  cursor: pointer;
}
</style>