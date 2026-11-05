<template>
  <div class="hermes-plugins-page">
    <!-- Providers 配置 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <span class="card-title">记忆与上下文引擎</span>
      </template>

      <el-form label-width="130px" v-loading="hubLoading">
        <el-form-item label="记忆 Provider">
          <el-select v-model="memorySel" style="max-width: 320px" @change="loadMemoryConfig">
            <el-option
              label="内置（MEMORY.md）"
              :value="BUILTIN_SENTINEL"
            />
            <el-option
              v-for="p in memoryOptions"
              :key="p.name"
              :label="p.label || p.name"
              :value="p.name"
            />
          </el-select>
          <el-tag
            v-if="memoryStatusTag"
            size="small"
            :type="memoryStatusTag.type"
            effect="plain"
            style="margin-left: 10px"
          >
            {{ memoryStatusTag.label }}
          </el-tag>
        </el-form-item>

        <!-- provider 动态表单 -->
        <template v-if="memorySel !== BUILTIN_SENTINEL">
          <el-form-item
            v-for="f in visibleMemoryFields"
            :key="f.key"
            :label="f.label || f.key"
          >
            <el-input-number
              v-if="f.kind === 'integer' || f.kind === 'number'"
              v-model="memoryValues[f.key]"
            />
            <el-switch
              v-else-if="f.kind === 'boolean'"
              v-model="memoryValues[f.key]"
            />
            <el-select
              v-else-if="f.kind === 'select'"
              v-model="memoryValues[f.key]"
              style="max-width: 320px"
            >
              <el-option v-for="o in f.options" :key="o" :label="o" :value="o" />
            </el-select>
            <el-input
              v-else
              v-model="memoryValues[f.key]"
              :type="f.kind === 'secret' ? 'password' : 'text'"
              :show-password="f.kind === 'secret'"
              :autocomplete="f.kind === 'secret' ? 'new-password' : 'off'"
              :placeholder="f.kind === 'secret' && f.is_set ? '已设置，留空保留原值' : ''"
              style="max-width: 320px"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :loading="busy === 'memory-save'"
              @click="saveMemoryProvider"
            >
              保存
            </el-button>
            <el-button
              :loading="busy === 'memory-setup'"
              @click="installProviderDeps"
            >
              安装依赖
            </el-button>
          </el-form-item>
        </template>

        <el-form-item label="上下文引擎">
          <el-select v-model="contextSel" style="max-width: 320px">
            <el-option
              v-for="c in contextOptions"
              :key="c"
              :label="c === 'compressor' ? 'Compressor（内置）' : c"
              :value="c"
            />
          </el-select>
          <el-button
            type="primary"
            :loading="busy === 'context-save'"
            style="margin-left: 10px"
            @click="saveContextEngine"
          >
            保存
          </el-button>
        </el-form-item>
      </el-form>

      <!-- setup 结果 -->
      <div v-if="setupResult" class="setup-result">
        <div
          v-for="(r, i) in setupResult"
          :key="i"
          class="setup-item"
          :class="r.status"
        >
          <span class="setup-name">{{ r.kind }} · {{ r.name }} — {{ r.status }}</span>
          <pre v-if="r.stdout" class="mono">{{ r.stdout }}</pre>
          <pre v-if="r.stderr" class="mono err">{{ r.stderr }}</pre>
        </div>
      </div>
    </el-card>

    <!-- 手动安装 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="card-title">手动安装插件</span></template>
      <el-form label-width="90px" inline>
        <el-form-item label="标识">
          <el-input
            v-model="manualIdentifier"
            placeholder="owner/repo 或 Git URL"
            style="width: 320px"
          />
        </el-form-item>
        <el-form-item label="强制重装">
          <el-switch v-model="manualForce" />
        </el-form-item>
        <el-form-item label="装后启用">
          <el-switch v-model="manualEnable" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="busy === 'manual-install'" @click="manualInstall">
            安装
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 插件目录 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-title-row">
          <span class="card-title">插件目录</span>
          <el-input
            v-model="catalogFilter"
            placeholder="搜索插件…"
            clearable
            style="width: 240px"
          />
        </div>
      </template>

      <div v-for="e in filteredCatalog" :key="e.name" class="catalog-row">
        <div class="catalog-main">
          <div class="catalog-title">
            <span class="catalog-name">{{ e.name }}</span>
            <el-tag size="small" :type="e.tier === 'official' ? 'success' : 'info'" effect="plain">
              {{ e.tier === 'official' ? '官方' : '社区' }}
            </el-tag>
            <el-tag v-if="e.installed" size="small" type="success" effect="plain">已安装</el-tag>
            <el-tag v-if="e.update_available" size="small" type="warning" effect="plain">
              有更新
            </el-tag>
          </div>
          <div class="catalog-desc">{{ e.description }}</div>
          <div class="catalog-meta">
            <span>维护者: {{ e.maintainer }}</span>
            <span v-if="e.capabilities?.provides_tools?.length">
              工具: {{ e.capabilities.provides_tools.join(', ') }}
            </span>
            <span v-if="e.capabilities?.requires_env?.length" class="req-env">
              需要 ENV: {{ e.capabilities.requires_env.join(', ') }}
            </span>
          </div>
        </div>
        <div class="catalog-actions">
          <el-button
            v-if="!e.installed"
            size="small"
            type="primary"
            :loading="catalogBusy === e.name"
            @click="confirmInstallCatalog(e)"
          >
            安装
          </el-button>
          <el-tag v-else size="small" type="success" effect="plain">Installed ✓</el-tag>
        </div>
      </div>
      <div v-if="!filteredCatalog.length && !catalogLoading" class="empty-tip">无匹配插件</div>
    </el-card>

    <!-- 已装插件 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-title-row">
          <span class="card-title">已安装插件（{{ hubPlugins.length }}）</span>
          <el-button size="small" :loading="busy === 'rescan'" @click="rescan">
            重新扫描
          </el-button>
        </div>
      </template>

      <div v-for="p in hubPlugins" :key="p.name" class="plugin-row">
        <div class="plugin-main">
          <div class="catalog-title">
            <span class="catalog-name">{{ p.name }}</span>
            <el-tag v-if="p.version" size="small" effect="plain">v{{ p.version }}</el-tag>
            <el-tag
              size="small"
              :type="p.runtime_status === 'enabled' ? 'success' : p.runtime_status === 'disabled' ? 'info' : 'warning'"
              effect="plain"
            >
              {{ p.runtime_status }}
            </el-tag>
            <el-tag v-if="p.can_update_git" size="small" type="warning" effect="plain">
              可更新
            </el-tag>
            <el-tag v-if="p.user_hidden" size="small" type="info" effect="plain">
              已隐藏
            </el-tag>
          </div>
          <div v-if="p.auth_required" class="auth-cmd">
            <code class="mono">{{ p.auth_command }}</code>
            <el-button size="small" text @click="copy(p.auth_command)">复制</el-button>
          </div>
          <div v-if="p.removed_reason" class="removed-reason">{{ p.removed_reason }}</div>
        </div>
        <div class="plugin-actions">
          <el-button
            size="small"
            :loading="busy === `toggle:${p.name}`"
            @click="togglePlugin(p)"
          >
            {{ p.runtime_status === 'enabled' ? '禁用' : '启用' }}
          </el-button>
          <el-button
            v-if="p.can_update_git"
            size="small"
            :loading="busy === `update:${p.name}`"
            @click="updatePlugin(p)"
          >
            更新
          </el-button>
          <el-button size="small" text @click="toggleVisibility(p)">
            {{ p.user_hidden ? '显示' : '隐藏' }}
          </el-button>
          <el-button size="small" type="danger" text @click="confirmRemove(p)">
            移除
          </el-button>
        </div>
      </div>
      <div v-if="!hubPlugins.length && !hubLoading" class="empty-tip">暂无已安装插件</div>
    </el-card>

    <!-- 孤儿 dashboard 插件 -->
    <el-card v-if="orphans.length" shadow="never" class="section-card">
      <template #header><span class="card-title">Dashboard 插件（孤儿）</span></template>
      <div v-for="o in orphans" :key="o.name" class="plugin-row">
        <span>{{ o.name }}</span>
        <code class="mono">{{ o.tab?.path }}</code>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { hermes } from '@/api/hermes'

const BUILTIN_SENTINEL = '__hermes_memory_builtin__'

const hubData = ref<any>(null)
const hubLoading = ref(false)
const catalogData = ref<any>(null)
const catalogLoading = ref(false)
const busy = ref<string | null>(null)
const catalogBusy = ref<string | null>(null)

const memorySel = ref(BUILTIN_SENTINEL)
const contextSel = ref('compressor')
const memoryFields = ref<any[]>([])
const memoryValues = ref<Record<string, any>>({})
const setupResult = ref<any[] | null>(null)

const manualIdentifier = ref('')
const manualForce = ref(false)
const manualEnable = ref(false)
const catalogFilter = ref('')

const hubPlugins = computed<any[]>(() => hubData.value?.plugins || [])
const orphans = computed<any[]>(() => hubData.value?.orphan_dashboard_plugins || [])
const memoryOptions = computed<any[]>(() => hubData.value?.providers?.memory_options || [])
const contextOptions = computed<string[]>(
  () => hubData.value?.providers?.context_options || []
)

const visibleMemoryFields = computed(() =>
  memoryFields.value.filter((f) => fieldIsVisible(f))
)

/** 官方 fieldIsVisible：when 条件过滤 */
function fieldIsVisible(f: any): boolean {
  const w = f.when
  if (!w || typeof w !== 'object') return true
  for (const [key, cond] of Object.entries(w)) {
    if (typeof cond !== 'object' || cond === null) continue
    const current = memoryValues.value[key]
    if ('value' in cond && current !== cond.value) return false
    if ('not_value' in cond && current === cond.not_value) return false
  }
  return true
}

const memoryStatusTag = computed(() => {
  const opt = memoryOptions.value.find((o) => o.name === memorySel.value)
  if (!opt) return null
  const statusMap: Record<string, { type: string; label: string }> = {
    ready: { type: 'success', label: '就绪' },
    'needs setup': { type: 'warning', label: '需要配置' },
    unavailable: { type: 'danger', label: '不可用' },
    missing: { type: 'info', label: '未安装' },
  }
  return statusMap[opt.status] || null
})

const filteredCatalog = computed(() => {
  const entries: any[] = catalogData.value?.entries || []
  const q = catalogFilter.value.toLowerCase()
  if (!q) return entries
  return entries.filter((e) =>
    [e.name, e.description, e.maintainer, ...(e.capabilities?.provides_tools || [])]
      .filter(Boolean)
      .some((s: string) => s.toLowerCase().includes(q))
  )
})

async function loadHub() {
  hubLoading.value = true
  try {
    const res: any = await hermes.getPluginsHub()
    hubData.value = res
    const providers = res.providers || {}
    memorySel.value = providers.memory_provider || BUILTIN_SENTINEL
    contextSel.value = providers.context_engine || 'compressor'
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '加载插件中心失败')
  } finally {
    hubLoading.value = false
  }
}

async function loadCatalog() {
  catalogLoading.value = true
  try {
    catalogData.value = await hermes.getPluginsCatalog()
  } catch (e: any) {
    // catalog 拉取失败不阻塞页面
  } finally {
    catalogLoading.value = false
  }
}

async function loadMemoryConfig() {
  if (memorySel.value === BUILTIN_SENTINEL) {
    memoryFields.value = []
    memoryValues.value = {}
    return
  }
  try {
    const res: any = await hermes.getMemoryProviderConfig(memorySel.value)
    memoryFields.value = res.fields || []
    const vals: Record<string, any> = {}
    for (const f of memoryFields.value) {
      vals[f.key] = fieldInitialValue(f)
    }
    memoryValues.value = vals
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '加载配置失败')
  }
}

/** 官方 fieldInitialValue */
function fieldInitialValue(f: any): any {
  if (f.kind === 'secret') return ''
  if (f.kind === 'boolean') return Boolean(f.value)
  if (f.kind === 'integer' || f.kind === 'number') return f.value ?? 0
  return f.value == null ? '' : String(f.value)
}

async function saveMemoryProvider() {
  if (memorySel.value === BUILTIN_SENTINEL) {
    busy.value = 'memory-save'
    try {
      await hermes.setMemoryProvider('')
      ElMessage.success('已切回内置记忆')
      await loadHub()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || e?.message || '保存失败')
    } finally {
      busy.value = null
    }
    return
  }
  busy.value = 'memory-save'
  try {
    const values: Record<string, any> = {}
    for (const f of visibleMemoryFields.value) {
      const v = memoryValues.value[f.key]
      if (f.kind === 'secret' && (v === '' || v == null)) continue // 留空保留
      values[f.key] = v
    }
    await hermes.updateMemoryProviderConfig(memorySel.value, values)
    ElMessage.success('已保存')
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '保存失败')
  } finally {
    busy.value = null
  }
}

async function installProviderDeps() {
  if (memorySel.value === BUILTIN_SENTINEL) return
  busy.value = 'memory-setup'
  try {
    const res: any = await hermes.setupMemoryProvider(memorySel.value)
    setupResult.value = res.results || []
    ElMessage.success('依赖安装完成')
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '安装失败')
  } finally {
    busy.value = null
  }
}

async function saveContextEngine() {
  busy.value = 'context-save'
  try {
    await hermes.savePluginProviders({ context_engine: contextSel.value })
    ElMessage.success('已保存上下文引擎')
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '保存失败')
  } finally {
    busy.value = null
  }
}

async function manualInstall() {
  const id = manualIdentifier.value.trim()
  if (!id) {
    ElMessage.warning('请输入插件标识')
    return
  }
  busy.value = 'manual-install'
  try {
    const res: any = await hermes.installAgentPlugin({
      identifier: id,
      force: manualForce.value || undefined,
      enable: manualEnable.value || undefined,
    })
    let msg = '插件已安装'
    if (res.warnings?.length) msg += `（${res.warnings.join('; ')}）`
    if (res.missing_env?.length) msg += `，缺少环境变量: ${res.missing_env.join(', ')}`
    ElMessage.success(msg)
    manualIdentifier.value = ''
    await loadHub()
    await loadCatalog()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '安装失败')
  } finally {
    busy.value = null
  }
}

function confirmInstallCatalog(e: any) {
  const envList = e.capabilities?.requires_env?.join(', ')
  ElMessageBox.confirm(
    `安装插件 "${e.name}"？\n${e.description}\n${envList ? `\n需要环境变量: ${envList}` : ''}`,
    '安装插件',
    { confirmButtonText: '安装', cancelButtonText: '取消' }
  ).then(() => installCatalog(e)).catch(() => {})
}

async function installCatalog(e: any) {
  catalogBusy.value = e.name
  try {
    const res: any = await hermes.installAgentPlugin({
      identifier: e.name,
      enable: false,
      catalog_name: e.name,
    })
    let msg = '插件已安装'
    if (res.missing_env?.length) msg += `，缺少环境变量: ${res.missing_env.join(', ')}`
    ElMessage.success(msg)
    await loadHub()
    await loadCatalog()
  } catch (e2: any) {
    ElMessage.error(e2?.response?.data?.detail || e2?.message || '安装失败')
  } finally {
    catalogBusy.value = null
  }
}

async function rescan() {
  busy.value = 'rescan'
  try {
    const res: any = await hermes.rescanPlugins()
    ElMessage.success(`扫描完成，发现 ${res.count ?? 0} 个插件`)
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '扫描失败')
  } finally {
    busy.value = null
  }
}

async function togglePlugin(p: any) {
  busy.value = `toggle:${p.name}`
  try {
    if (p.runtime_status === 'enabled') await hermes.disableAgentPlugin(p.name)
    else await hermes.enableAgentPlugin(p.name)
    ElMessage.success('操作成功')
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  } finally {
    busy.value = null
  }
}

async function updatePlugin(p: any) {
  busy.value = `update:${p.name}`
  try {
    await hermes.updateAgentPlugin(p.name)
    ElMessage.success('更新完成')
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '更新失败')
  } finally {
    busy.value = null
  }
}

async function toggleVisibility(p: any) {
  try {
    await hermes.setPluginVisibility(p.name, !p.user_hidden)
    ElMessage.success('已更新可见性')
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  }
}

function confirmRemove(p: any) {
  ElMessageBox.confirm(
    `确定移除插件 "${p.name}"？`,
    '移除插件',
    { type: 'warning', confirmButtonText: '移除', cancelButtonText: '取消' }
  ).then(() => doRemove(p)).catch(() => {})
}

async function doRemove(p: any) {
  busy.value = `remove:${p.name}`
  try {
    await hermes.removeAgentPlugin(p.name)
    ElMessage.success('已移除')
    await loadHub()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '移除失败')
  } finally {
    busy.value = null
  }
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

onMounted(() => {
  loadHub().then(() => loadMemoryConfig())
  loadCatalog()
})
</script>

<style scoped>
.hermes-plugins-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-title {
  font-weight: 600;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setup-result {
  margin-top: 12px;
  border-top: 1px dashed var(--el-border-color);
  padding-top: 12px;
}

.setup-item {
  padding: 8px 0;
}

.setup-item.error {
  color: var(--el-color-danger);
}

.setup-name {
  font-size: 13px;
  font-weight: 500;
}

.setup-item pre {
  margin: 6px 0 0;
  padding: 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  font-size: 12px;
  max-height: 160px;
  overflow: auto;
  white-space: pre-wrap;
}

.setup-item pre.err {
  color: var(--el-color-danger);
}

.catalog-row,
.plugin-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 4px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.catalog-row:last-child,
.plugin-row:last-child {
  border-bottom: none;
}

.catalog-main,
.plugin-main {
  flex: 1;
  min-width: 0;
}

.catalog-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.catalog-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.catalog-desc {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin: 4px 0;
}

.catalog-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.req-env {
  color: var(--el-color-warning);
}

.catalog-actions,
.plugin-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: stretch;
  flex-shrink: 0;
}

.auth-cmd {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.auth-cmd code {
  font-size: 12px;
  padding: 4px 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.removed-reason {
  color: var(--el-color-danger);
  font-size: 12px;
  margin-top: 4px;
}

.mono {
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
}

.empty-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  padding: 8px 0;
}
</style>
