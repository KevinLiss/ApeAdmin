<template>
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

    <!-- 搜索栏 -->
    <div class="toolbar">
      <el-select v-model="query.category_id" placeholder="按分类筛选" clearable style="width: 160px" @change="loadList">
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-input v-model="query.keyword" placeholder="搜索标题" clearable style="width: 200px" @keyup.enter="loadList" />
      <el-button type="primary" @click="loadList">查询</el-button>
    </div>

    <el-table :data="docList" v-loading="loading" stripe>
      <el-table-column prop="title" label="标题" min-width="200" />
      <el-table-column prop="category_name" label="分类" width="120" />
      <el-table-column prop="version" label="版本" width="80" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.published ? 'success' : 'info'" size="small">{{ row.published ? '已发布' : '草稿' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="view_count" label="浏览" width="80" />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" text @click="openDocDialog(row)">编辑</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty><div style="padding: 24px">暂无文档</div></template>
    </el-table>

    <!-- 分页 -->
    <div class="pager" v-if="total > query.page_size">
      <el-pagination
        v-model:current-page="query.page"
        :page-size="query.page_size"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadList"
      />
    </div>

    <!-- 文档编辑弹窗 -->
    <el-dialog v-model="docDialogVisible" :title="docEditing.id ? '编辑文档' : '新增文档'" width="780px" top="5vh">
      <el-form :model="docEditing" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="docEditing.title" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="docEditing.category_id" clearable placeholder="选择分类" style="width: 200px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Slug">
              <el-input v-model="docEditing.slug" placeholder="URL 标识" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="版本">
              <el-input v-model="docEditing.version" placeholder="1.0.0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="摘要">
          <el-input v-model="docEditing.summary" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="正文">
          <el-input v-model="docEditing.body" type="textarea" :rows="10" placeholder="支持 Markdown 格式" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="docEditing.sort" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发布">
              <el-switch v-model="docEditing.published" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="docDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveDoc">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分类管理弹窗 -->
    <el-dialog v-model="catDialogVisible" title="文档分类管理" width="560px">
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
          <el-table-column prop="sort" label="排序" width="80" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" text type="danger" @click="handleDeleteCat(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
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
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 8px; }
.toolbar { display: flex; gap: 12px; margin-bottom: 16px; }
.pager { margin-top: 16px; display: flex; justify-content: center; }
.cat-manage { display: flex; flex-direction: column; gap: 12px; }
.cat-add { display: flex; gap: 8px; align-items: center; }
</style>
