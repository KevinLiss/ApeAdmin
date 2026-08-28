<template>
  <div class="docs-admin">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card total">
        <div class="stat-icon">📄</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">文档总数</div>
        </div>
      </div>
      <div class="stat-card published">
        <div class="stat-icon">✅</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.published }}</div>
          <div class="stat-label">已发布</div>
        </div>
      </div>
      <div class="stat-card draft">
        <div class="stat-icon">✏️</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.draft }}</div>
          <div class="stat-label">草稿</div>
        </div>
      </div>
      <div class="stat-card views">
        <div class="stat-icon">👁</div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.totalViews }}</div>
          <div class="stat-label">总浏览量</div>
        </div>
      </div>
    </div>

    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>文档管理</span>
          <div class="header-actions">
            <el-button size="small" @click="catDialogVisible = true">分类管理</el-button>
            <el-button type="primary" size="small" @click="openDocDialog()">新增文档</el-button>
          </div>
        </div>
      </template>

      <div class="toolbar">
        <el-select v-model="query.category_id" placeholder="按分类筛选" clearable style="width: 160px" @change="search">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-input v-model="query.keyword" placeholder="搜索标题" clearable style="width: 240px" @keyup.enter="search">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="search">查询</el-button>
      </div>

      <el-table :data="docList" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="category_name" label="分类" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.category_name" size="small" effect="light" round>{{ row.category_name }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80">
          <template #default="{ row }"><span class="ver-tag">v{{ row.version }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.published ? 'success' : 'info'" size="small" effect="light" round>{{ row.published ? '已发布' : '草稿' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览" width="80" align="center">
          <template #default="{ row }"><span class="view-count">{{ row.view_count }}</span></template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="70" align="center" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openDocDialog(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
        <template #empty><el-empty description="暂无文档" /></template>
      </el-table>

      <div class="pager" v-if="total > query.page_size">
        <el-pagination v-model:current-page="query.page" :page-size="query.page_size" :total="total" layout="prev, pager, next" @current-change="loadList" />
      </div>

      <!-- 文档编辑弹窗 -->
      <el-dialog v-model="docDialogVisible" :title="docEditing.id ? '编辑文档' : '新增文档'" width="780px" top="5vh" destroy-on-close>
        <div class="dialog-body">
          <div class="dialog-hint">
            <el-icon><InfoFilled /></el-icon>
            <span>文档支持 Markdown 格式正文，发布后将在官网文档站展示。</span>
          </div>
          <el-form :model="docEditing" label-position="top">
            <el-form-item label="标题">
              <el-input v-model="docEditing.title" placeholder="文档标题" />
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="分类">
                  <el-select v-model="docEditing.category_id" clearable placeholder="选择分类" style="width: 100%">
                    <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Slug">
                  <el-input v-model="docEditing.slug" placeholder="URL 标识" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="版本">
                  <el-input v-model="docEditing.version" placeholder="1.0.0" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="摘要">
              <el-input v-model="docEditing.summary" type="textarea" :rows="2" placeholder="文档摘要" />
            </el-form-item>
            <el-form-item label="正文（Markdown）">
              <el-input v-model="docEditing.body" type="textarea" :rows="10" placeholder="支持 Markdown 格式" />
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="排序">
                  <el-input-number v-model="docEditing.sort" :min="0" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="发布状态">
                  <el-switch v-model="docEditing.published" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
        <template #footer>
          <el-button @click="docDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSaveDoc">保存</el-button>
        </template>
      </el-dialog>

      <!-- 分类管理弹窗 -->
      <el-dialog v-model="catDialogVisible" title="文档分类管理" width="560px" destroy-on-close>
        <div class="cat-manage">
          <div class="cat-add">
            <el-input v-model="newCat.name" placeholder="分类名称" style="width: 150px" />
            <el-input v-model="newCat.description" placeholder="描述" style="width: 180px" />
            <el-input-number v-model="newCat.sort" :min="0" placeholder="排序" style="width: 100px" />
            <el-button type="primary" size="small" @click="handleAddCat">添加</el-button>
          </div>
          <el-table :data="categories" size="small" stripe>
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="description" label="描述" min-width="160" />
            <el-table-column prop="sort" label="排序" width="80" align="center" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button size="small" text type="danger" @click="handleDeleteCat(row)">删除</el-button>
              </template>
            </el-table-column>
            <template #empty><el-empty description="暂无分类" :image-size="60" /></template>
          </el-table>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, Search } from '@element-plus/icons-vue'
import {
  getAdminDocs, createAdminDoc, updateAdminDoc, deleteAdminDoc,
  getAdminDocCategories, createAdminDocCategory, deleteAdminDocCategory,
} from '@/api/apehub_web'

const docList = ref<any[]>([])
const categories = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const total = ref(0)

const query = ref({ category_id: undefined as number | undefined, keyword: '', page: 1, page_size: 20 })

const docDialogVisible = ref(false)
const catDialogVisible = ref(false)
const docEditing = ref<any>({ title: '', slug: '', category_id: null, version: '1.0.0', summary: '', body: '', published: true, sort: 0 })
const newCat = ref({ name: '', description: '', sort: 0 })

const stats = computed(() => {
  const totalDocs = docList.value.length
  const published = docList.value.filter(d => d.published).length
  const totalViews = docList.value.reduce((sum, d) => sum + Number(d.view_count || 0), 0)
  return { total: totalDocs, published, draft: totalDocs - published, totalViews }
})

const loadList = async () => {
  loading.value = true
  try {
    const data = await getAdminDocs(query.value)
    docList.value = data.items || []
    total.value = data.total || 0
  } finally { loading.value = false }
}

const loadCategories = async () => {
  try { categories.value = await getAdminDocCategories() } catch { /* */ }
}

const search = () => { query.value.page = 1; loadList() }

const openDocDialog = (row?: any) => {
  if (row) {
    docEditing.value = { ...row }
  } else {
    docEditing.value = { title: '', slug: '', category_id: null, version: '1.0.0', summary: '', body: '', published: true, sort: 0 }
  }
  docDialogVisible.value = true
}

const handleSaveDoc = async () => {
  saving.value = true
  try {
    if (docEditing.value.id) {
      await updateAdminDoc(docEditing.value.id, docEditing.value)
    } else {
      await createAdminDoc(docEditing.value)
    }
    ElMessage.success('保存成功')
    docDialogVisible.value = false
    loadList()
  } finally { saving.value = false }
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm('确认删除该文档？', '提示', { type: 'warning' })
  await deleteAdminDoc(row.id)
  ElMessage.success('已删除')
  loadList()
}

const handleAddCat = async () => {
  if (!newCat.value.name) { ElMessage.warning('请输入分类名称'); return }
  await createAdminDocCategory(newCat.value)
  ElMessage.success('分类已添加')
  newCat.value = { name: '', description: '', sort: 0 }
  loadCategories()
}

const handleDeleteCat = async (row: any) => {
  await ElMessageBox.confirm('确认删除该分类？', '提示', { type: 'warning' })
  await deleteAdminDocCategory(row.id)
  ElMessage.success('已删除')
  loadCategories()
}

onMounted(async () => {
  await Promise.all([loadList(), loadCategories()])
})
</script>

<style scoped>
.stats-row { display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-card {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 24px; border-radius: 12px;
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-lighter);
  min-width: 140px; flex: 1; transition: all 0.2s;
}
.stat-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.stat-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.stat-card.total .stat-icon { background: #e6f0ff; }
.stat-card.published .stat-icon { background: #e8f5e9; }
.stat-card.draft .stat-icon { background: #fef3e2; }
.stat-card.views .stat-icon { background: #e6e6fa; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--el-text-color-primary); }
.stat-label { font-size: 13px; color: var(--el-text-color-secondary); margin-top: 2px; }

.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 8px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }

.ver-tag { font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px; color: var(--el-text-color-secondary); }
.view-count { font-weight: 600; }
.text-muted { color: var(--el-text-color-secondary); font-size: 13px; }

.dialog-body { padding: 4px 0; }
.dialog-hint {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 14px; margin-bottom: 16px;
  background: #e6f4ec; border-radius: 8px; font-size: 13px; color: #2e7d32;
}
.dialog-hint .el-icon { margin-top: 1px; flex-shrink: 0; }

.cat-manage { display: flex; flex-direction: column; gap: 12px; }
.cat-add { display: flex; gap: 8px; align-items: center; }
</style>
