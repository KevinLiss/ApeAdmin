<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>内容管理</span>
        <el-button type="primary" size="small" @click="openDialog()">新增内容块</el-button>
      </div>
    </template>

    <el-table :data="contentList" v-loading="loading" stripe>
      <el-table-column prop="block_key" label="区块" width="120" />
      <el-table-column prop="title" label="标题" min-width="160" />
      <el-table-column prop="subtitle" label="副标题" min-width="160" show-overflow-tooltip />
      <el-table-column prop="sort" label="排序" width="80" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" text @click="openDialog(row)">编辑</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty><div style="padding: 24px">暂无内容</div></template>
    </el-table>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="editing.id ? '编辑内容' : '新增内容'" width="640px">
      <el-form :model="editing" label-width="100px">
        <el-form-item label="区块标识">
          <el-input v-model="editing.block_key" placeholder="hero / features / footer 等" />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="editing.title" />
        </el-form-item>
        <el-form-item label="副标题">
          <el-input v-model="editing.subtitle" />
        </el-form-item>
        <el-form-item label="正文">
          <el-input v-model="editing.body" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="editing.image" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="editing.sort" :min="0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="editing.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminContent, createAdminContent, updateAdminContent, deleteAdminContent } from '@/api/apehub_web'

const contentList = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)

const editing = ref<any>({
  block_key: '', title: '', subtitle: '', body: '', image: '', sort: 0, enabled: true,
})

const loadList = async () => {
  loading.value = true
  try { contentList.value = await getAdminContent() } finally { loading.value = false }
}

const openDialog = (row?: any) => {
  if (row) {
    editing.value = { ...row }
  } else {
    editing.value = { block_key: '', title: '', subtitle: '', body: '', image: '', sort: 0, enabled: true }
  }
  dialogVisible.value = true
}

const handleSave = async () => {
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

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm('确认删除该内容块？', '提示', { type: 'warning' })
  await deleteAdminContent(row.id)
  ElMessage.success('已删除')
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
