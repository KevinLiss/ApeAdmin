<template>
  <el-card shadow="never" class="page-card">
    <div class="toolbar">
      <el-button type="success" @click="openDialog()">
        <el-icon><Plus /></el-icon>新增部门
      </el-button>
    </div>

    <el-table
      :data="tree"
      row-key="id"
      v-loading="loading"
      :tree-props="{ children: 'children' }"
      default-expand-all
    >
      <el-table-column prop="name" label="部门名称" min-width="180" />
      <el-table-column prop="leader" label="负责人" min-width="100" />
      <el-table-column prop="phone" label="联系电话" min-width="130" />
      <el-table-column prop="sort" label="排序" width="70" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑部门' : '新增部门'" width="480px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="上级部门">
        <el-tree-select
          v-model="form.parent_id"
          :data="parentOptions"
          :props="{ label: 'name', children: 'children' }"
          check-strictly
          clearable
          placeholder="选择上级（留空为顶级）"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="部门名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="负责人">
        <el-input v-model="form.leader" />
      </el-form-item>
      <el-form-item label="联系电话">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="排序">
        <el-input-number v-model="form.sort" :min="0" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getDeptTree, createDept, updateDept, deleteDept } from '@/api'

const tree = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const parentOptions = ref<any[]>([])

const formRef = ref<FormInstance>()
const form = reactive({
  parent_id: 0,
  name: '',
  leader: '',
  phone: '',
  sort: 0,
  status: 1,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
}

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getDeptTree()
    tree.value = data || []
    parentOptions.value = [{ id: 0, name: '顶级', children: data || [] }]
  } finally {
    loading.value = false
  }
}

function openDialog(row?: any) {
  editingId.value = row?.id ?? null
  form.parent_id = row?.parent_id ?? 0
  form.name = row?.name ?? ''
  form.leader = row?.leader ?? ''
  form.phone = row?.phone ?? ''
  form.sort = row?.sort ?? 0
  form.status = row?.status ?? 1
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const payload = {
        parent_id: form.parent_id,
        name: form.name,
        leader: form.leader,
        phone: form.phone,
        sort: form.sort,
        status: form.status,
      }
      if (editingId.value) {
        await updateDept(editingId.value, payload)
        ElMessage.success('更新成功')
      } else {
        await createDept(payload)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } finally {
      saving.value = false
    }
  })
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(`确定删除部门「${row.name}」吗？`, '提示', { type: 'warning' })
  await deleteDept(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

onMounted(fetchData)
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
</style>