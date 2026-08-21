<template>
  <el-card shadow="never" class="page-card">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索插件名称"
        clearable
        style="width: 220px"
        @keyup.enter="fetchData"
      />
      <el-button type="primary" @click="fetchData">
        <el-icon><Search /></el-icon>查询
      </el-button>
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
            @change="(val) => handleToggle(item, val as boolean)"
          />
        </div>

        <p class="plugin-desc">{{ item.description || '暂无描述' }}</p>

        <div class="plugin-meta">
          <el-tag size="small" type="info">{{ item.author || '未知作者' }}</el-tag>
          <span class="plugin-path">{{ item.module_path }}</span>
        </div>

        <div class="plugin-footer">
          <span class="plugin-time">{{ formatTime(item.updated_at) }}</span>
          <el-button link type="primary" @click="openConfig(item)">
            <el-icon><Setting /></el-icon>配置
          </el-button>
        </div>
      </el-card>

      <el-empty v-if="!loading && filteredList.length === 0" description="暂无插件" />
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
    :title="`配置 - ${currentPlugin?.display_name || currentPlugin?.name || ''}`"
    width="600px"
  >
    <el-alert
      title="插件配置为 JSON 格式，修改后需重启后端生效"
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
      <el-button @click="configVisible = false">取消</el-button>
      <el-button type="primary" :loading="savingConfig" @click="saveConfig">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPlugins, togglePlugin, getPluginConfig, updatePluginConfig } from '@/api'

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

// Config dialog state
const configVisible = ref(false)
const currentPlugin = ref<PluginRow | null>(null)
const configText = ref('')
const savingConfig = ref(false)

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
    await togglePlugin(item.id, val)
    ElMessage.success(`${val ? '启用' : '禁用'}成功，重启后端后生效`)
  } catch {
    // Revert on error
    item.enabled = !val
    ElMessage.error('操作失败')
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
    ElMessage.error('JSON 格式错误，请检查')
    return
  }

  savingConfig.value = true
  try {
    await updatePluginConfig(currentPlugin.value.id, parsed)
    ElMessage.success('配置已保存')
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
