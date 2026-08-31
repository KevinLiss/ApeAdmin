<template>
  <div class="content-admin">
    <!-- 工具栏：搜索 + 操作 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索区块标识、标题、副标题…"
          :prefix-icon="Search"
          clearable
          class="search-input"
        />
        <el-select v-model="filterStatus" placeholder="全部状态" clearable class="filter-select">
          <el-option label="全部状态" value="" />
          <el-option label="已启用" value="enabled" />
          <el-option label="已禁用" value="disabled" />
        </el-select>
        <div class="count-badge">
          共 <span class="count-num">{{ filteredList.length }}</span> 项
        </div>
      </div>
      <div class="toolbar-right">
        <el-button :icon="Refresh" @click="refreshPreview">刷新预览</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">新增内容块</el-button>
      </div>
    </div>

    <!-- 左右分栏：实时预览 + 侧边编辑面板 -->
    <div class="preview-layout">
      <!-- 左：官网实时预览 -->
      <div class="preview-pane">
        <div class="preview-toolbar">
          <div class="preview-title">
            <el-icon><Monitor /></el-icon>
            <span>官网实时预览</span>
            <span class="preview-hint">拖动右侧区块调整顺序，hover 高亮定位</span>
          </div>
          <div class="preview-actions">
            <el-radio-group v-model="previewWidth" size="small">
              <el-radio-button :value="375">375</el-radio-button>
              <el-radio-button :value="768">768</el-radio-button>
              <el-radio-button :value="0">全宽</el-radio-button>
            </el-radio-group>
            <el-button
              size="small"
              text
              :icon="Link"
              @click="openPreview"
              title="在新标签页打开官网"
            />
          </div>
        </div>
        <div class="preview-body" :class="{ 'preview-narrow': previewWidth > 0 }" :style="previewWidth > 0 ? { maxWidth: previewWidth + 'px' } : {}">
          <iframe
            ref="previewFrame"
            :src="previewUrl"
            class="preview-frame"
            title="官网首页预览"
            v-loading="iframeLoading"
          />
        </div>
      </div>

      <!-- 右：侧边编辑面板 -->
      <div class="side-panel" v-loading="loading">
        <!-- 区块列表 -->
        <template v-if="!editingBlock">
          <div class="panel-header">
            <span class="panel-title">区块列表</span>
            <span class="panel-sub" v-if="!isFiltered">拖动排序，松手自动保存</span>
            <span class="panel-sub" v-else>筛选状态下暂不支持拖拽</span>
          </div>
          <div ref="listRef" class="block-list">
            <div
              v-for="item in filteredList"
              :key="item.id"
              class="block-item"
              :class="{ 'block-disabled': !item.enabled }"
              @mouseenter="highlightBlock(item.block_key)"
              @mouseleave="clearHighlight"
            >
              <span
                class="drag-handle"
                :class="{ disabled: isFiltered }"
                :title="isFiltered ? '筛选模式下不可拖拽' : '拖动排序'"
              >
                <el-icon><Rank /></el-icon>
              </span>
              <div class="block-info" @click="openEdit(item)">
                <div class="block-icon" :style="{ background: blockMeta[item.block_key]?.bg || 'var(--el-fill-color)' }">
                  {{ blockMeta[item.block_key]?.icon || '📦' }}
                </div>
                <div class="block-text">
                  <div class="block-title-row">
                    <span class="block-key-tag">{{ item.block_key }}</span>
                    <span class="block-label">{{ blockMeta[item.block_key]?.label || item.block_key }}</span>
                  </div>
                  <div class="block-title">{{ item.title || '—' }}</div>
                </div>
                <div class="block-ops">
                  <el-switch
                    :model-value="item.enabled"
                    @change="(val: any) => toggleEnabled(item, val as boolean)"
                    :loading="item._toggling"
                    size="small"
                    @click.stop
                  />
                </div>
              </div>
            </div>

            <el-empty v-if="!loading && !filteredList.length" description="暂无内容块" :image-size="80" />
          </div>
        </template>

        <!-- 编辑表单 -->
        <template v-else>
          <div class="panel-header">
            <el-button text :icon="ArrowLeft" @click="goEdit">返回列表</el-button>
            <span class="panel-title">{{ editingBlock.id ? '编辑内容块' : '新增内容块' }}</span>
          </div>
          <div class="edit-form">
            <el-form :model="editingBlock" label-position="top">
              <el-form-item label="区块标识">
                <el-input
                  v-model="editingBlock.block_key"
                  placeholder="hero / features / footer 等"
                  :disabled="!!editingBlock.id"
                />
              </el-form-item>
              <el-form-item label="排序">
                <el-input-number v-model="editingBlock.sort" :min="0" style="width: 100%" />
              </el-form-item>
              <el-form-item label="标题">
                <el-input v-model="editingBlock.title" placeholder="区块标题" />
              </el-form-item>
              <el-form-item label="副标题">
                <el-input v-model="editingBlock.subtitle" placeholder="区块副标题（选填）" />
              </el-form-item>
              <el-form-item label="正文（支持 Markdown）">
                <el-input
                  v-model="editingBlock.body"
                  type="textarea"
                  :rows="6"
                  placeholder="区块正文内容，支持 Markdown 语法"
                />
              </el-form-item>
              <el-form-item label="图片 URL">
                <el-input v-model="editingBlock.image" placeholder="区块配图地址（选填）">
                  <template #prepend v-if="editingBlock.image">
                    <el-image :src="editingBlock.image" fit="cover" class="url-preview" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="启用状态">
                <el-switch v-model="editingBlock.enabled" />
                <span class="switch-hint">{{ editingBlock.enabled ? '前端可见' : '前端隐藏' }}</span>
              </el-form-item>
            </el-form>

            <div class="edit-actions">
              <el-button @click="goEdit">取消</el-button>
              <el-button
                type="danger"
                plain
                :loading="deleting"
                v-if="editingBlock.id"
                @click="handleDelete(editingBlock)"
              >
                删除
              </el-button>
              <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Refresh, Rank, Monitor, Link, ArrowLeft } from '@element-plus/icons-vue'
import Sortable from 'sortablejs'
import { getAdminContent, createAdminContent, updateAdminContent, reorderAdminContent, deleteAdminContent } from '@/api/apehub_web'

const contentList = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const listRef = ref<HTMLElement>()
const previewFrame = ref<HTMLIFrameElement>()
const iframeLoading = ref(false)
let sortableInstance: Sortable | null = null

// 预览
const previewUrl = '/apehub-web/index.html'
const previewWidth = ref(0)

// 搜索与筛选
const searchQuery = ref('')
const filterStatus = ref('')

// 编辑态
const editingBlock = ref<any>(null)

// 区块元信息：图标、背景色、中文标签
const blockMeta: Record<string, { icon: string; bg: string; label: string }> = {
  hero:         { icon: '🏠', bg: 'linear-gradient(135deg, #667eea, #764ba2)', label: '主视觉区' },
  features:     { icon: '✨', bg: 'linear-gradient(135deg, #f093fb, #f5576c)', label: '核心特性' },
  architecture: { icon: '🏗️', bg: 'linear-gradient(135deg, #4facfe, #00f2fe)', label: '架构设计' },
  mcp:          { icon: '🔌', bg: 'linear-gradient(135deg, #43e97b, #38f9d7)', label: 'MCP 网关' },
  techstack:    { icon: '⚙️', bg: 'linear-gradient(135deg, #fa709a, #fee140)', label: '技术栈' },
  plugin_eco:   { icon: '🧩', bg: 'linear-gradient(135deg, #a8edea, #fed6e3)', label: '插件生态' },
  quickstart:   { icon: '🚀', bg: 'linear-gradient(135deg, #ffecd2, #fcb69f)', label: '快速开始' },
  cta:          { icon: '📢', bg: 'linear-gradient(135deg, #ff9a9e, #fad0c4)', label: '行动号召' },
  footer:       { icon: '📄', bg: 'linear-gradient(135deg, #a18cd1, #fbc2eb)', label: '页脚信息' },
}

const isFiltered = computed(() => !!searchQuery.value.trim() || !!filterStatus.value)
const filteredList = computed(() => {
  let list = contentList.value
  if (filterStatus.value === 'enabled') list = list.filter(c => c.enabled)
  else if (filterStatus.value === 'disabled') list = list.filter(c => !c.enabled)
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(c =>
      (c.block_key || '').toLowerCase().includes(q) ||
      (c.title || '').toLowerCase().includes(q) ||
      (c.subtitle || '').toLowerCase().includes(q)
    )
  }
  return list
})

// —— iframe 通信 ——
const postToPreview = (type: string, blockKey?: string) => {
  const frame = previewFrame.value?.contentWindow
  if (!frame) return
  frame.postMessage({ source: 'apehub-admin', type, blockKey }, window.location.origin)
}

const highlightBlock = (blockKey: string) => postToPreview('ape-highlight', blockKey)
const clearHighlight = () => postToPreview('ape-highlight-clear')
const refreshPreview = () => postToPreview('ape-refresh')

const openPreview = () => { window.open(previewUrl, '_blank') }

// —— 加载列表 ——
const loadList = async () => {
  loading.value = true
  try {
    contentList.value = await getAdminContent()
    await nextTick()
    initSortable()
  } finally { loading.value = false }
}

// —— 列表拖拽排序 ——
const initSortable = () => {
  destroySortable()
  const container = listRef.value
  if (!container || isFiltered.value) return
  sortableInstance = Sortable.create(container, {
    handle: '.drag-handle',
    animation: 200,
    ghostClass: 'item-ghost',
    chosenClass: 'item-chosen',
    dragClass: 'item-drag',
    onEnd: async (evt: any) => {
      if (evt.oldIndex === evt.newIndex) return
      const arr = contentList.value.slice()
      const [moved] = arr.splice(evt.oldIndex, 1)
      arr.splice(evt.newIndex, 0, moved)
      const items = arr.map((row, idx) => ({ id: row.id, sort: (idx + 1) * 10 }))
      try {
        await reorderAdminContent(items)
        contentList.value = arr.map((row, idx) => ({ ...row, sort: (idx + 1) * 10 }))
        ElMessage.success(`已更新排序，共 ${items.length} 个区块`)
        refreshPreview()
      } catch {
        ElMessage.error('排序保存失败')
        loadList()
      }
    },
  })
}

const destroySortable = () => {
  if (sortableInstance) {
    sortableInstance.destroy()
    sortableInstance = null
  }
}

watch(isFiltered, async () => {
  await nextTick()
  initSortable()
})

// —— 开关 ——
const toggleEnabled = async (row: any, val: boolean) => {
  row._toggling = true
  try {
    await updateAdminContent(row.id, { ...row, enabled: val })
    row.enabled = val
    ElMessage.success(val ? '已启用' : '已禁用')
    refreshPreview()
  } catch {
    // 失败不翻转
  } finally {
    row._toggling = false
  }
}

// —— 编辑面板 ——
const openCreate = () => {
  editingBlock.value = { block_key: '', title: '', subtitle: '', body: '', image: '', sort: 0, enabled: true }
}
const openEdit = (row: any) => {
  editingBlock.value = { ...row }
}
const goEdit = () => { editingBlock.value = null }

// 保存
const handleSave = async () => {
  if (!editingBlock.value.block_key?.trim()) {
    ElMessage.warning('请填写区块标识')
    return
  }
  saving.value = true
  try {
    if (editingBlock.value.id) {
      await updateAdminContent(editingBlock.value.id, editingBlock.value)
    } else {
      await createAdminContent(editingBlock.value)
    }
    ElMessage.success('保存成功')
    editingBlock.value = null
    await loadList()
    refreshPreview()
  } finally { saving.value = false }
}

// 删除
const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除内容块「${row.title || row.block_key}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  deleting.value = true
  try {
    await deleteAdminContent(row.id)
    ElMessage.success('已删除')
    editingBlock.value = null
    await loadList()
    refreshPreview()
  } finally { deleting.value = false }
}

onMounted(() => {
  loadList()
  iframeLoading.value = true
  // iframe 加载完成
  nextTick(() => {
    const frame = previewFrame.value
    if (frame) {
      frame.addEventListener('load', () => { iframeLoading.value = false })
    }
  })
})

onBeforeUnmount(() => {
  destroySortable()
})
</script>

<style scoped>
.content-admin {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* —— 工具栏 —— */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
  flex-shrink: 0;
}
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}
.search-input {
  width: 280px;
  max-width: 100%;
}
.filter-select {
  width: 130px;
}
.count-badge {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}
.count-num {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* —— 左右分栏 —— */
.preview-layout {
  display: flex;
  gap: 14px;
  flex: 1;
  min-height: 0;
}

/* 左：预览 */
.preview-pane {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  overflow: hidden;
  background: var(--el-bg-color);
}
.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  gap: 10px;
  flex-wrap: wrap;
}
.preview-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}
.preview-hint {
  font-size: 12px;
  font-weight: 400;
  color: var(--el-text-color-secondary);
}
.preview-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.preview-body {
  flex: 1;
  min-height: 0;
  background: var(--el-fill-color-lighter);
  padding: 12px;
  overflow: auto;
  display: flex;
  justify-content: center;
  transition: max-width .25s ease;
}
.preview-frame {
  width: 100%;
  height: 100%;
  min-height: 480px;
  border: none;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 4px 20px -8px rgba(0,0,0,.15);
}

/* —— 右：侧边面板 —— */
.side-panel {
  width: 400px;
  max-width: 42%;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  overflow: hidden;
  background: var(--el-bg-color);
  min-height: 480px;
}
.panel-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  flex-shrink: 0;
}
.panel-title {
  font-size: 14px;
  font-weight: 600;
}
.panel-sub {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 区块列表 */
.block-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
}
.block-item {
  display: flex;
  align-items: stretch;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  background: var(--el-bg-color);
  overflow: hidden;
  transition: border-color .2s, box-shadow .2s, opacity .2s;
}
.block-item:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 16px -6px rgba(0,0,0,.08);
}
.block-item.block-disabled {
  opacity: .55;
}
.block-item.block-disabled:hover {
  opacity: .8;
}
.drag-handle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  color: var(--el-text-color-placeholder);
  font-size: 16px;
  cursor: grab;
  background: var(--el-fill-color-lighter);
  border-right: 1px solid var(--el-border-color-lighter);
  flex-shrink: 0;
}
.drag-handle:hover {
  color: var(--el-color-primary);
}
.drag-handle:active {
  cursor: grabbing;
}
.drag-handle.disabled {
  cursor: not-allowed;
  opacity: .4;
}
.block-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  cursor: pointer;
  min-width: 0;
}
.block-info:hover {
  background: var(--el-fill-color-light);
}
.block-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.block-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.block-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.block-key-tag {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 10.5px;
  padding: 1px 6px;
  border-radius: 5px;
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  white-space: nowrap;
}
.block-label {
  font-size: 11.5px;
  color: var(--el-text-color-secondary);
}
.block-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.block-ops {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

/* 拖拽视觉状态 */
.block-list :deep(.item-ghost) {
  opacity: .35;
  border: 2px dashed var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}
.block-list :deep(.item-chosen) {
  box-shadow: 0 8px 28px -8px rgba(0,0,0,.18);
}
.block-list :deep(.item-drag) {
  opacity: .9;
  transform: rotate(.6deg);
  box-shadow: 0 12px 36px -8px rgba(0,0,0,.25);
}

/* —— 编辑表单 —— */
.edit-form {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.switch-hint {
  margin-left: 8px;
  font-size: 12.5px;
  color: var(--el-text-color-secondary);
}
.url-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}
.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* —— 响应式 —— */
@media (max-width: 900px) {
  .preview-layout {
    flex-direction: column;
  }
  .side-panel {
    width: 100%;
    max-width: none;
    min-height: 320px;
  }
  .preview-frame {
    min-height: 400px;
  }
}
</style>