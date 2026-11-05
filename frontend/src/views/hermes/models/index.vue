<template>
  <div class="hermes-models-page">
    <!-- 顶部工具栏 -->
    <div class="page-toolbar">
      <div class="page-title">
        <h3>模型配置</h3>
        <span class="page-sub">管理 Hermes 引擎的当前模型、辅助模型与 MoA 路由</span>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="loadAll">刷新</el-button>
    </div>

    <div class="grid-layout" v-loading="loading">
      <!-- 左列：当前模型信息 + 模型切换 -->
      <div class="left-col">
        <!-- 当前模型信息卡片 -->
        <el-card shadow="never" class="model-card">
          <template #header>
            <div class="card-header">
              <span>当前模型信息</span>
              <el-tag v-if="modelInfo?.model" type="success" size="small" effect="light">
                {{ modelInfo.provider || 'unknown' }}
              </el-tag>
            </div>
          </template>

          <el-descriptions :column="1" border size="small" class="model-descriptions">
            <el-descriptions-item label="模型">
              <span class="model-name">{{ modelInfo?.model || '—' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="Provider">
              {{ modelInfo?.provider || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="上下文窗口">
              {{ formatContextWindow(modelInfo?.context_window) }}
            </el-descriptions-item>
            <el-descriptions-item label="视觉 (Vision)">
              <el-tag :type="modelInfo?.supports_vision ? 'success' : 'info'" size="small" effect="plain">
                {{ modelInfo?.supports_vision ? '支持' : '不支持' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="推理 (Reasoning)">
              <el-tag :type="modelInfo?.supports_reasoning ? 'success' : 'info'" size="small" effect="plain">
                {{ modelInfo?.supports_reasoning ? '支持' : '不支持' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 模型切换卡片 -->
        <el-card shadow="never" class="model-card">
          <template #header>
            <div class="card-header">
              <span>切换模型</span>
            </div>
          </template>

          <div class="switch-form">
            <div class="form-row">
              <label class="form-label">模型</label>
              <el-select
                v-model="selectedModel"
                filterable
                allow-create
                default-first-option
                placeholder="选择或输入模型名"
                class="form-control"
              >
                <el-option
                  v-for="m in modelOptions"
                  :key="m.key || m.model + m.provider"
                  :label="m.model"
                  :value="m.model"
                >
                  <div class="option-line">
                    <span class="option-model">{{ m.model }}</span>
                    <el-tag v-if="m.provider" size="small" type="info" effect="plain">{{ m.provider }}</el-tag>
                  </div>
                </el-option>
              </el-select>
            </div>
            <div class="form-row">
              <label class="form-label">Provider</label>
              <el-select
                v-model="selectedProvider"
                filterable
                allow-create
                default-first-option
                placeholder="选择或输入 provider"
                class="form-control"
              >
                <el-option
                  v-for="p in providerOptions"
                  :key="p"
                  :label="p"
                  :value="p"
                />
              </el-select>
            </div>
            <div class="form-actions">
              <el-button type="primary" :loading="switching" @click="handleSwitchModel">保存切换</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右列：推荐模型 + MoA 配置 -->
      <div class="right-col">
        <!-- 推荐默认模型卡片 -->
        <el-card shadow="never" class="model-card">
          <template #header>
            <div class="card-header">
              <span>推荐默认模型</span>
            </div>
          </template>

          <div class="recommended-list" v-if="recommendedModels.length">
            <div
              v-for="(rec, idx) in recommendedModels"
              :key="rec.key || idx"
              class="recommended-item"
              :class="{ active: isCurrent(rec) }"
            >
              <div class="rec-main">
                <span class="rec-model">{{ rec.model }}</span>
                <el-tag v-if="rec.provider" size="small" type="info" effect="plain">{{ rec.provider }}</el-tag>
                <el-tag v-if="rec.tag" size="small" effect="light">{{ rec.tag }}</el-tag>
              </div>
              <div class="rec-side">
                <el-tag v-if="isCurrent(rec)" type="success" size="small" effect="dark">当前</el-tag>
                <el-button size="small" :loading="switching" @click="applyRecommended(rec)">一键切换</el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无推荐模型" :image-size="60" />
        </el-card>

        <!-- MoA 配置卡片 -->
        <el-card shadow="never" class="model-card">
          <template #header>
            <div class="card-header">
              <span>MoA（Mixture of Agents）</span>
              <el-switch
                v-model="moaEnabled"
                :loading="moaSaving"
                @change="handleMoaChange"
              />
            </div>
          </template>

          <div class="moa-content">
            <p class="moa-desc">
              多智能体混合路由：将请求分发给多个辅助模型，聚合结果以提升回复质量与多样性。
            </p>
            <el-descriptions :column="1" size="small" class="moa-meta" v-if="moaInfo && Object.keys(moaInfo).length > 1">
              <el-descriptions-item
                v-for="(val, key) in moaInfo"
                :key="key"
                :label="String(key)"
              >
                {{ typeof val === 'boolean' ? (val ? '是' : '否') : Array.isArray(val) ? (val.length ? val.join(', ') : '—') : val }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 下方：辅助模型 + 本地模型 -->
    <div class="bottom-layout" v-loading="loading">
      <!-- 辅助模型配置 -->
      <el-card shadow="never" class="model-card">
        <template #header>
          <div class="card-header">
            <span>辅助模型（Auxiliary）</span>
            <div class="card-actions">
              <el-button size="small" :loading="auxSaving" @click="saveAuxiliary">保存</el-button>
            </div>
          </div>
        </template>

        <div class="aux-body">
          <div v-if="auxiliaryModels.length" class="aux-list">
            <div v-for="(aux, idx) in auxiliaryModels" :key="idx" class="aux-row">
              <el-select
                v-model="aux.model"
                filterable
                allow-create
                default-first-option
                placeholder="模型名"
                class="aux-select"
              >
                <el-option
                  v-for="m in modelOptions"
                  :key="m.key || m.model"
                  :label="m.model"
                  :value="m.model"
                />
              </el-select>
              <el-select
                v-model="aux.provider"
                filterable
                allow-create
                default-first-option
                placeholder="provider"
                class="aux-select provider"
              >
                <el-option
                  v-for="p in providerOptions"
                  :key="p"
                  :label="p"
                  :value="p"
                />
              </el-select>
              <el-button size="small" type="danger" plain :icon="Delete" circle @click="removeAuxiliary(idx)" />
            </div>
          </div>
          <el-empty v-else description="暂无辅助模型" :image-size="60" />

          <div class="aux-footer">
            <el-button size="small" type="primary" plain :icon="Plus" @click="addAuxiliary">添加辅助模型</el-button>
          </div>
        </div>
      </el-card>

      <!-- 本地模型列表 -->
      <el-card shadow="never" class="model-card">
        <template #header>
          <div class="card-header">
            <span>本地模型</span>
            <el-tag v-if="localModels.length" type="info" size="small" effect="plain">
              {{ localModels.length }} 个
            </el-tag>
          </div>
        </template>

        <div v-if="localModels.length" class="local-grid">
          <div v-for="(lm, idx) in localModels" :key="idx" class="local-item">
            <div class="local-name">
              {{ typeof lm === 'string' ? lm : (lm?.name || lm?.model || JSON.stringify(lm)) }}
            </div>
            <el-tag v-if="typeof lm !== 'string' && (lm?.running || lm?.loaded)" type="success" size="small" effect="light">
              运行中
            </el-tag>
          </div>
        </div>
        <el-empty v-else description="未检测到本地模型" :image-size="60" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

// ── 状态 ──────────────────────────────────────
const loading = ref(false)
const switching = ref(false)

// 当前模型信息
const modelInfo = ref<any>(null)

// 模型切换表单
const selectedModel = ref('')
const selectedProvider = ref('')

// 可用模型选项
const modelOptions = ref<any[]>([])
const providerOptions = ref<string[]>([])

// 推荐默认模型
const recommendedModels = ref<any[]>([])

// 辅助模型
const auxiliaryModels = ref<any[]>([])
const auxSaving = ref(false)

// MoA
const moaInfo = ref<any>(null)
const moaEnabled = ref(false)
const moaSaving = ref(false)

// 本地模型
const localModels = ref<any[]>([])

// ── 派生 ──────────────────────────────────────
/** 提供下拉的 model → provider 映射 */
const providerOfModel = computed(() => {
  const map: Record<string, string> = {}
  modelOptions.value.forEach((m) => {
    if (m.model && m.provider && !map[m.model]) map[m.model] = m.provider
  })
  recommendedModels.value.forEach((m) => {
    if (m.model && m.provider && !map[m.model]) map[m.model] = m.provider
  })
  return map
})

function isCurrent(m: any): boolean {
  const info = modelInfo.value
  return !!info?.model && m?.model === info.model && (!m?.provider || m.provider === info.provider)
}

function formatContextWindow(n: number | undefined | null): string {
  if (!n) return '—'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(n % 1000 === 0 ? 0 : 1)}K`
  return String(n)
}

// ── 数据加载 ──────────────────────────────────────
async function loadModelInfo() {
  const res: any = await hermes.getModelInfo()
  if (!res) return
  Object.assign(modelInfo, res)
  // 同步下拉框当前值
  if (res.model) {
    selectedModel.value = res.model
    selectedProvider.value = res.provider || providerOfModel.value[res.model] || ''
  }
}

async function loadModelOptions() {
  const res: any = await hermes.getModelOptions()
  const list: any[] = res?.models || res?.options || (Array.isArray(res) ? res : [])
  modelOptions.value = list
  const providers = new Set<string>()
  list.forEach((m: any) => {
    if (m?.provider) providers.add(m.provider)
  })
  providerOptions.value = Array.from(providers)
}

async function loadRecommended() {
  const res: any = await hermes.getModelRecommended()
  if (Array.isArray(res)) {
    recommendedModels.value = res
  } else if (res?.models) {
    recommendedModels.value = res.models
  } else if (res?.model || res?.provider) {
    recommendedModels.value = [res]
  } else {
    recommendedModels.value = []
  }
}

async function loadAuxiliary() {
  const res: any = await hermes.getAuxiliaryModels()
  if (Array.isArray(res)) {
    auxiliaryModels.value = res
  } else if (res?.models) {
    auxiliaryModels.value = res.models
  } else {
    auxiliaryModels.value = []
  }
}

async function loadMoa() {
  const res: any = await hermes.getMoa()
  moaInfo.value = res || {}
  moaEnabled.value = !!res?.enabled
}

// getLocalModels 已移除——hermes 无 /api/local-models 路由
async function loadLocalModels() {
  localModels.value = []
}

async function loadAll() {
  loading.value = true
  try {
    // 先加载选项，供后续回填 provider 使用
    await Promise.allSettled([loadModelOptions(), loadRecommended()])
    await Promise.allSettled([
      loadModelInfo(),
      loadAuxiliary(),
      loadMoa(),
      loadLocalModels(),
    ])
  } finally {
    loading.value = false
  }
}

// ── 模型切换 ──────────────────────────────────────
async function handleSwitchModel() {
  const model = selectedModel.value.trim()
  if (!model) {
    ElMessage.warning('请先选择或输入模型名')
    return
  }
  switching.value = true
  try {
    const res: any = await hermes.setModel(model, selectedProvider.value.trim() || undefined)
    if (res?.ok === false) {
      ElMessage.error(res?.error || '切换模型失败')
      return
    }
    ElMessage.success(`已切换到 ${model}`)
    await loadModelInfo()
  } catch (e: any) {
    ElMessage.error(e?.message || '切换模型失败')
  } finally {
    switching.value = false
  }
}

async function applyRecommended(rec: any) {
  if (!rec?.model) return
  switching.value = true
  try {
    const res: any = await hermes.setModel(rec.model, rec.provider || undefined)
    if (res?.ok === false) {
      ElMessage.error(res?.error || '切换模型失败')
      return
    }
    ElMessage.success(`已切换到推荐模型 ${rec.model}`)
    await loadModelInfo()
  } catch (e: any) {
    ElMessage.error(e?.message || '切换模型失败')
  } finally {
    switching.value = false
  }
}

// ── 辅助模型 ──────────────────────────────────────
function addAuxiliary() {
  auxiliaryModels.value.push({ model: '', provider: '' })
}

function removeAuxiliary(idx: number) {
  auxiliaryModels.value.splice(idx, 1)
}

async function saveAuxiliary() {
  const valid = auxiliaryModels.value.filter((a) => a?.model?.trim())
  if (valid.length !== auxiliaryModels.value.length) {
    ElMessage.warning('存在未填写模型名的辅助模型条目，将忽略')
  }
  auxSaving.value = true
  try {
    const res: any = await hermes.setAuxiliaryModels({ models: valid })
    if (res?.ok === false) {
      ElMessage.error(res?.error || '保存辅助模型失败')
      return
    }
    ElMessage.success('辅助模型已保存')
    await loadAuxiliary()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存辅助模型失败')
  } finally {
    auxSaving.value = false
  }
}

// ── MoA ──────────────────────────────────────
async function handleMoaChange(val: boolean | string | number) {
  moaSaving.value = true
  const enabled = !!val
  try {
    const res: any = await hermes.setMoa({ enabled, ...(moaInfo.value || {}) })
    if (res?.ok === false) {
      moaEnabled.value = !enabled
      ElMessage.error(res?.error || '更新 MoA 配置失败')
      return
    }
    ElMessage.success(enabled ? 'MoA 已启用' : 'MoA 已关闭')
    moaInfo.value = res ?? moaInfo.value
  } catch (e: any) {
    moaEnabled.value = !enabled
    ElMessage.error(e?.message || '更新 MoA 配置失败')
  } finally {
    moaSaving.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.hermes-models-page {
  padding: 4px 2px 24px;
}

.page-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2329;
}

.page-title .page-sub {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #8a919f;
}

.grid-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.left-col,
.right-col {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bottom-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}

.model-card {
  border-radius: 8px;
  border-color: #e5e7eb;
  background: #fff;
}

.model-card :deep(.el-card__header) {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f1f3;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 600;
  color: #1f2329;
}

.card-header .el-tag {
  font-weight: 400;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* ── 当前模型信息 ── */
.model-descriptions {
  margin-top: 4px;
}

.model-descriptions :deep(.el-descriptions__label) {
  width: 120px;
  color: #6b7280;
}

.model-name {
  font-weight: 500;
  color: #1f2329;
  word-break: break-all;
}

/* ── 切换模型 ── */
.switch-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-label {
  width: 72px;
  flex-shrink: 0;
  font-size: 13px;
  color: #4b5563;
}

.form-control {
  flex: 1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.option-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-model {
  font-weight: 500;
}

/* ── 推荐模型 ── */
.recommended-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommended-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #eef0f2;
  border-radius: 8px;
  background: #fafbfc;
  transition: border-color 0.2s;
}

.recommended-item:hover {
  border-color: #c6d4f9;
}

.recommended-item.active {
  border-color: #67c23a;
  background: #f0f9eb;
}

.rec-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 0;
}

.rec-model {
  font-weight: 500;
  font-size: 13px;
  color: #1f2329;
}

.rec-side {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ── MoA ── */
.moa-desc {
  margin: 0 0 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #6b7280;
}

.moa-meta :deep(.el-descriptions__label) {
  width: 120px;
  color: #6b7280;
}

/* ── 辅助模型 ── */
.aux-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.aux-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.aux-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.aux-select {
  flex: 1;
  min-width: 0;
}

.aux-select.provider {
  flex: 0 0 45%;
}

.aux-footer {
  display: flex;
  justify-content: flex-start;
  padding-top: 4px;
}

/* ── 本地模型 ── */
.local-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}

.local-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid #eef0f2;
  border-radius: 8px;
  background: #fafbfc;
}

.local-name {
  font-size: 13px;
  font-weight: 500;
  color: #1f2329;
  word-break: break-all;
}

@media (max-width: 960px) {
  .grid-layout,
  .bottom-layout {
    grid-template-columns: 1fr;
  }
}
</style>