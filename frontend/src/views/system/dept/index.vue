<template>
  <el-card shadow="never" class="page-card">
    <div class="toolbar">
      <el-button type="success" @click="openDialog()">
        <el-icon><Plus /></el-icon>{{ t('system.dept.createDept') }}
      </el-button>
    </div>

    <el-table
      :data="tree"
      row-key="id"
      v-loading="loading"
      :tree-props="{ children: 'children' }"
      default-expand-all
    >
      <el-table-column prop="name" :label="t('system.dept.deptName')" min-width="180" />
      <el-table-column prop="leader" :label="t('system.dept.leader')" min-width="100" />
      <el-table-column prop="phone" :label="t('system.dept.phone')" min-width="130" />
      <el-table-column prop="sort" :label="t('system.dept.sort')" width="70" />
      <el-table-column :label="t('system.dept.status')" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? t('system.dept.active') : t('system.dept.disabled') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.action.actions')" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">{{ t('common.action.edit') }}</el-button>
          <el-button link type="danger" @click="handleDelete(row)">{{ t('common.action.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? t('system.dept.editDept') : t('system.dept.createDept')" width="480px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item :label="t('system.dept.parentDept')">
        <el-tree-select
          v-model="form.parent_id"
          :data="parentOptions"
          :props="{ label: 'name', children: 'children' }"
          check-strictly
          clearable
          :placeholder="t('system.dept.parentPlaceholder')"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item :label="t('system.dept.deptName')" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('system.dept.leader')">
        <el-input v-model="form.leader" />
      </el-form-item>
      <el-form-item :label="t('system.dept.phone')">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item :label="t('system.dept.sort')">
        <el-input-number v-model="form.sort" :min="0" />
      </el-form-item>
      <el-form-item :label="t('system.dept.status')">
        <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">{{ t('common.action.cancel') }}</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">{{ t('common.action.save') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getDeptTree, createDept, updateDept, deleteDept } from '@/api'

const { t } = useI18n()

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
  name: [{ required: true, message: () => t('common.validation.required', { name: t('system.dept.deptName') }), trigger: 'blur' }],
}

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getDeptTree()
    tree.value = data || []
    parentOptions.value = [{ id: 0, name: t('system.dept.topLevel'), children: data || [] }]
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
        ElMessage.success(t('common.message.updateSuccess'))
      } else {
        await createDept(payload)
        ElMessage.success(t('common.message.createSuccess'))
      }
      dialogVisible.value = false
      fetchData()
    } finally {
      saving.value = false
    }
  })
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(t('system.dept.deleteConfirm', { name: row.name }), t('common.action.tip'), { type: 'warning' })
  await deleteDept(row.id)
  ElMessage.success(t('common.message.deleteSuccess'))
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