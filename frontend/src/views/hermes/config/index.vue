<template>
  <div class="hermes-config-page">
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <div class="toolbar-title">Hermes 配置</div>
      <div class="toolbar-actions">
        <el-button :icon="Refresh" :loading="loading" @click="loadConfig">刷新</el-button>
        <el-button type="primary" :loading="saving" :disabled="!dirty" @click="saveConfig">保存</el-button>
        <el-button :loading="rawLoading" @click="viewRaw">查看原始配置</el-button>
      </div>
    </div>

    <!-- 折叠面板：按顶层 key 分组 -->
    <div class="config-panel" v-loading="loading">
      <el-collapse v-model="activeGroups">
        <el-collapse-item v-for="group in groups" :key="group.topKey" :name="group.topKey">
          <template #title>
            <span class="group-title">{{ group.topKey }}</span>
            <el-tag size="small" effect="plain" class="group-count">{{ group.items.length }} 项</el-tag>
          </template>
          <div class="config-items">
            <div v-for="item in group.items" :key="item.fullKey" class="config-item-row">
              <div class="config-key">
                <span class="key-name">{{ item.key }}</span>
                <el-tag size="small" effect="plain" class="key-type">{{ item.typeLabel }}</el-tag>
              </div>
              <div class="config-value-wrap">
                <el-input
                  v-if="!item.isComplex"
                  :model-value="item.text"
                  placeholder="配置值"
                  @update:model-value="(v: any) => onSimpleChange(item, v)"
                />
                <el-input
                  v-else
                  :model-value="item.text"
                  type="textarea"
                  :autosize="{ minRows: 2, maxRows: 12 }"
                  placeholder="JSON 配置值"
                  @update:model-value="(v: any) => onComplexChange(item, v)"
                />
                <div
                  v-if="item.defaultText !== undefined && item.defaultText !== item.text"
                  class="default-hint"
                >
                  默认：{{ item.defaultText }}
                </div>
              </div>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
      <el-empty v-if="!loading && !groups.length" description="暂无配置" :image-size="80" />
    </div>

    <!-- 原始配置查看弹窗 -->
    <el-dialog v-model="rawDialogVisible" title="原始 YAML 配置" width="640px" top="6vh">
      <div class="raw-config">
        <pre>{{ rawConfig }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  ElButton, ElCollapse, ElCollapseItem, ElInput, ElMessage, ElDialog, ElTag,
} from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

// ── 类型 ──────────────────────────────────────────
interface ConfigItem {
  key: string
  fullKey: string
  isComplex: boolean
  text: string
  typeLabel: string
  original: any
  defaultText?: string
}
interface ConfigGroup {
  topKey: string
  items: ConfigItem[]
}

// ── 状态 ──────────────────────────────────────────
const loading = ref(false)
const saving = ref(false)
const rawLoading = ref(false)
const dirty = ref(false)
const configData = ref<Record<string, any>>({})
const defaultsData = ref<Record<string, any>>({})
const groups = ref<ConfigGroup[]>([])
const activeGroups = ref<string[]>([])
const rawDialogVisible = ref(false)
const rawConfig = ref('')

// ── 工具函数 ──────────────────────────────────────
function isComplex(v: any): boolean {
  return v !== null && typeof v === 'object'
}

function typeLabel(v: any): string {
  if (v === null) return 'null'
  if (Array.isArray(v)) return 'array'
  return typeof v
}

function unwrapObject(res: any): Record<string, any> {
  if (res && typeof res === 'object') {
    if (res.config && typeof res.config === 'object') return res.config
    if (res.data && typeof res.data === 'object' && !Array.isArray(res.data)) return res.data
    return res
  }
  return {}
}

function getByPath(obj: any, path: string): any {
  const parts = path.split('.')
  let cur = obj
  for (const p of parts) {
    if (cur == null) return undefined
    cur = cur[p]
  }
  return cur
}

function setByPath(obj: any, path: string, value: any) {
  const parts = path.split('.')
  let cur = obj
  for (let i = 0; i < parts.length - 1; i++) {
    if (cur[parts[i]] == null) cur[parts[i]] = {}
    cur = cur[parts[i]]
  }
  cur[parts[parts.length - 1]] = value
}

function coerceValue(text: string, original: any): any {
  if (typeof original === 'number') {
    const n = Number(text)
    return Number.isNaN(n) ? text : n
  }
  if (typeof original === 'boolean') return text === 'true'
  if (original === null) return text === 'null' ? null : text
  return text
}

// ── 分组构建（按顶层 key 分组，复杂值 JSON 化）──────
function buildGroups(data: Record<string, any>, defaults: Record<string, any>) {
  const gs: ConfigGroup[] = []
  Object.entries(data).forEach(([topKey, v]) => {
    const items: ConfigItem[] = []
    if (isComplex(v) && !Array.isArray(v)) {
      // 顶层对象：展平一层子项
      Object.entries(v).forEach(([k, sv]) => {
        const fullKey = `${topKey}.${k}`
        const complex = isComplex(sv)
        const dflt = getByPath(defaults, fullKey)
        items.push({
          key: k,
          fullKey,
          isComplex: complex,
          text: complex ? JSON.stringify(sv, null, 2) : String(sv),
          typeLabel: complex ? (Array.isArray(sv) ? `array[${sv.length}]` : 'object') : typeLabel(sv),
          original: sv,
          defaultText: dflt === undefined ? undefined : (isComplex(dflt) ? JSON.stringify(dflt, null, 2) : String(dflt)),
        })
      })
    } else {
      // 顶层为简单值 / 数组，整体作为一项展示
      const complex = isComplex(v)
      const dflt = getByPath(defaults, topKey)
      items.push({
        key: topKey,
        fullKey: topKey,
        isComplex: complex,
        text: complex ? JSON.stringify(v, null, 2) : String(v),
        typeLabel: complex ? (Array.isArray(v) ? `array[${v.length}]` : 'object') : typeLabel(v),
        original: v,
        defaultText: dflt === undefined ? undefined : (isComplex(dflt) ? JSON.stringify(dflt, null, 2) : String(dflt)),
      })
    }
    gs.push({ topKey, items })
  })
  groups.value = gs
}

// ── 数据加载 ──────────────────────────────────────
async function loadConfig() {
  loading.value = true
  try {
    const cfgRes: any = await hermes.getConfig()
    configData.value = unwrapObject(cfgRes)
  } catch (e: any) {
    ElMessage.error(`加载配置失败: ${e.message}`)
    loading.value = false
    return
  }
  try {
    const defRes: any = await hermes.getConfigDefaults()
    defaultsData.value = unwrapObject(defRes)
  } catch {
    defaultsData.value = {}
  }
  buildGroups(configData.value, defaultsData.value)
  dirty.value = false
  loading.value = false
}

async function viewRaw() {
  rawLoading.value = true
  try {
    const res: any = await hermes.getConfigRaw()
    if (typeof res === 'string') {
      rawConfig.value = res
    } else {
      rawConfig.value = res?.raw ?? res?.content ?? JSON.stringify(res, null, 2)
    }
    rawDialogVisible.value = true
  } catch (e: any) {
    ElMessage.error(`获取原始配置失败: ${e.message}`)
  } finally {
    rawLoading.value = false
  }
}

// ── 编辑 ──────────────────────────────────────────
function onSimpleChange(item: ConfigItem, text: string) {
  const val = coerceValue(text, item.original)
  item.text = text
  item.original = val
  setByPath(configData.value, item.fullKey, val)
  dirty.value = true
}

function onComplexChange(item: ConfigItem, text: string) {
  item.text = text
  try {
    const parsed = JSON.parse(text)
    item.original = parsed
    item.typeLabel = Array.isArray(parsed) ? `array[${parsed.length}]` : 'object'
    setByPath(configData.value, item.fullKey, parsed)
    dirty.value = true
  } catch {
    // JSON 语法暂不合法，不写回，等待用户修正
  }
}

// ── 保存 ──────────────────────────────────────────
async function saveConfig() {
  saving.value = true
  try {
    await hermes.setConfig(configData.value)
    ElMessage.success('配置已保存')
    dirty.value = false
    await loadConfig()
  } catch (e: any) {
    ElMessage.error(`保存失败: ${e.message}`)
  } finally {
    saving.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.hermes-config-page {
  background: #f5f7fa;
  min-height: 100%;
  padding: 16px;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 12px;
}
.toolbar-title {
  font-size: 15px;
  font-weight: 600;
}
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.config-panel {
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 4px 16px;
}
.group-title {
  font-weight: 600;
  font-size: 14px;
}
.group-count {
  margin-left: 8px;
}
.config-items {
  padding: 4px 8px 8px;
}
.config-item-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.config-item-row:last-child {
  border-bottom: none;
}
.config-key {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 6px;
}
.key-name {
  font-size: 13px;
  font-weight: 500;
  word-break: break-all;
}
.key-type {
  flex-shrink: 0;
}
.config-value-wrap {
  flex: 1;
  min-width: 0;
}
.default-hint {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 6px;
  word-break: break-all;
}
.raw-config {
  background: #f7f8fa;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  padding: 12px;
  max-height: 60vh;
  overflow: auto;
}
.raw-config pre {
  margin: 0;
  font-size: 12px;
  font-family: 'SFMono-Regular', Consolas, Menlo, monospace;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>