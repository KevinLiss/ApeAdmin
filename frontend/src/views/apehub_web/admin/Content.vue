<template>
  <div class="content-admin">
    <!-- 工具栏：搜索 + 筛选 + 新增 -->
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
      <el-button type="primary" :icon="Plus" @click="openDialog()">新增内容块</el-button>
    </div>

    <!-- 数据表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="filteredList" v-loading="loading" stripe row-key="id">
        <!-- 区块标识 -->
        <el-table-column prop="block_key" label="区块标识" width="150">
          <template #default="{ row }">
            <el-tooltip :content="getBlockHint(row.block_key)" placement="top" :show-after="300">
              <span class="block-key-tag">{{ row.block_key }}</span>
            </el-tooltip>
          </template>
        </el-table-column>

        <!-- 内容预览（标题 + 副标题 + 正文摘要组合） -->
        <el-table-column label="内容" min-width="320">
          <template #default="{ row }">
            <div class="content-preview">
              <div class="preview-title">{{ row.title || '—' }}</div>
              <div class="preview-sub" v-if="row.subtitle">{{ row.subtitle }}</div>
              <div class="preview-body" v-if="row.body">{{ truncate(stripMarkdown(row.body), 80) }}</div>
            </div>
          </template>
        </el-table-column>

        <!-- 配图 -->
        <el-table-column label="配图" width="70" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="row.image"
              :preview-src-list="[row.image]"
              fit="cover"
              class="thumb"
              :preview-teleported="true"
            />
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>

        <!-- 排序 -->
        <el-table-column prop="sort" label="排序" width="80" align="center">
          <template #default="{ row }">
            <span class="sort-num">{{ row.sort }}</span>
          </template>
        </el-table-column>

        <!-- 状态（行内 Switch） -->
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.enabled"
              @change="(val: any) => toggleEnabled(row, val as boolean)"
              :loading="row._toggling"
            />
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>

        <template #empty><el-empty description="暂无内容" /></template>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editing.id ? '编辑内容块' : '新增内容块'"
      width="720px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <div class="dialog-body">
        <!-- 基本信息 -->
        <div class="form-section">
          <div class="form-section-title">基本信息</div>
          <el-form :model="editing" label-position="top">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="区块标识">
                  <el-input
                    v-model="editing.block_key"
                    placeholder="hero / features / footer 等"
                    :disabled="!!editing.id"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="排序">
                  <el-input-number v-model="editing.sort" :min="0" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="标题">
              <el-input v-model="editing.title" placeholder="区块标题" />
            </el-form-item>
            <el-form-item label="副标题">
              <el-input v-model="editing.subtitle" placeholder="区块副标题（选填）" />
            </el-form-item>
          </el-form>
        </div>

        <!-- 内容详情 -->
        <div class="form-section">
          <div class="form-section-title">内容详情</div>
          <el-form :model="editing" label-position="top">
            <el-form-item label="正文（支持 Markdown）">
              <el-input
                v-model="editing.body"
                type="textarea"
                :rows="5"
                placeholder="区块正文内容，支持 Markdown 语法"
              />
            </el-form-item>
            <el-form-item label="图片 URL">
              <el-input v-model="editing.image" placeholder="区块配图地址（选填）">
                <template #prepend v-if="editing.image">
                  <el-image :src="editing.image" fit="cover" class="url-preview" />
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </div>

        <!-- 高级设置 -->
        <div class="form-section">
          <div class="form-section-title">高级设置</div>
          <el-form :model="editing" label-position="left" label-width="80px">
            <el-form-item label="启用状态">
              <el-switch v-model="editing.enabled" />
              <span class="switch-hint">{{ editing.enabled ? '前端可见' : '前端隐藏' }}</span>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getAdminContent, createAdminContent, updateAdminContent, deleteAdminContent } from '@/api/apehub_web'

const contentList = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)

// 搜索与筛选
const searchQuery = ref('')
const filterStatus = ref('')

const editing = ref<any>({
  block_key: '', title: '', subtitle: '', body: '', image: '', sort: 0, enabled: true,
})

// 区块标识 → 官网位置说明
const blockHints: Record<string, string> = {
  hero: '首页顶部主视觉区（品牌标语 + CTA）',
  features: '核心特性展示区（功能亮点）',
  architecture: '架构设计说明区',
  mcp: 'MCP 网关说明区',
  techstack: '技术栈展示区',
  plugin_eco: '插件生态介绍区',
  quickstart: '快速开始引导区',
  cta: '底部行动号召区（转化引导）',
  footer: '页脚信息区',
}

const getBlockHint = (key: string) => blockHints[key] || `区块 "${key}"，对应官网展示区域`

// 搜索筛选
const filteredList = computed(() => {
  let list = contentList.value
  // 状态筛选
  if (filterStatus.value === 'enabled') list = list.filter(c => c.enabled)
  else if (filterStatus.value === 'disabled') list = list.filter(c => !c.enabled)
  // 关键词搜索
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

// 工具函数
const stripMarkdown = (md: string) => md?.replace(/[#*`>\-\[\]()!]/g, '').replace(/\n+/g, ' ').trim() || ''
const truncate = (str: string, len: number) => str.length > len ? str.slice(0, len) + '…' : str

// 加载列表
const loadList = async () => {
  loading.value = true
  try { contentList.value = await getAdminContent() } finally { loading.value = false }
}

// 行内切换启用状态
const toggleEnabled = async (row: any, val: boolean) => {
  row._toggling = true
  try {
    await updateAdminContent(row.id, { ...row, enabled: val })
    row.enabled = val
    ElMessage.success(val ? '已启用' : '已禁用')
  } catch {
    // 失败不翻转
  } finally {
    row._toggling = false
  }
}

// 打开弹窗
const openDialog = (row?: any) => {
  if (row) {
    editing.value = { ...row }
  } else {
    editing.value = { block_key: '', title: '', subtitle: '', body: '', image: '', sort: 0, enabled: true }
  }
  dialogVisible.value = true
}

// 保存
const handleSave = async () => {
  if (!editing.value.block_key?.trim()) {
    ElMessage.warning('请填写区块标识')
    return
  }
  saving.value = true
  try {
    if (editing.value.id) {
      await updateAdminContent(editing.value.id, editing.value)
    } else {
      await createAdminContent(editing.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadList()
  } finally { saving.value = false }
}

// 删除
const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除内容块「${row.title || row.block_key}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteAdminContent(row.id)
  ElMessage.success('已删除')
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
/* —— 工具栏 —— */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
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

/* —— 表格卡片 —— */
.table-card {
  border-radius: 10px;
}
.table-card :deep(.el-card__body) {
  padding: 0;
}
.table-card :deep(.el-table) {
  border-radius: 10px;
}

/* 区块标识 tag */
.block-key-tag {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  color: var(--el-color-primary);
  cursor: default;
}

/* 内容预览 */
.content-preview {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.preview-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary);
  line-height: 1.4;
}
.preview-sub {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.3;
}
.preview-body {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

/* 配图缩略图 */
.thumb {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--el-border-color-lighter);
}
.text-muted {
  color: var(--el-text-color-placeholder);
}

/* 排序数字 */
.sort-num {
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

/* —— 弹窗 —— */
.dialog-body {
  padding: 4px 0;
}
.form-section {
  margin-bottom: 20px;
}
.form-section:last-child {
  margin-bottom: 0;
}
.form-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.switch-hint {
  margin-left: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.url-preview {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

/* —— 响应式 —— */
@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
  }
  .toolbar-left {
    flex-wrap: wrap;
  }
  .search-input {
    width: 100%;
  }
}
</style>
