<template>
  <el-card shadow="never" class="page-card">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        :placeholder="t('system.user.searchPlaceholder')"
        clearable
        style="width: 220px"
        @keyup.enter="fetchData"
      />
      <el-button type="primary" @click="fetchData">
        <el-icon><Search /></el-icon>{{ t('common.action.query') }}
      </el-button>
    <el-button type="success" @click="openDialog()" v-permission="'system:user:add'">
      <el-icon><Plus /></el-icon>{{ t('common.action.create') }}
    </el-button>
    </div>

    <!-- Table -->
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" :label="t('system.user.username')" min-width="110" />
      <el-table-column prop="nickname" :label="t('system.user.nickname')" min-width="110" />
      <el-table-column :label="t('system.user.dept')" min-width="120">
        <template #default="{ row }">{{ row.dept?.name || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('system.user.role')" min-width="140">
        <template #default="{ row }">
          <el-tag v-for="r in row.roles" :key="r.id" size="small" class="role-tag">{{ r.name }}</el-tag>
          <span v-if="!row.roles?.length">—</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('system.user.status')" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? t('system.user.active') : t('system.user.disabled') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" :label="t('system.user.createTime')" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.action.actions')" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)" v-permission="'system:user:edit'">{{ t('common.action.edit') }}</el-button>
          <el-button link type="danger" @click="handleDelete(row)" v-permission="'system:user:delete'">{{ t('common.action.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <el-pagination
      v-model:current-page="query.page"
      v-model:page-size="query.page_size"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next, jumper"
      class="pagination"
      @change="fetchData"
    />
  </el-card>

  <!-- Dialog -->
  <el-dialog
    v-model="dialogVisible"
    :title="editingId ? t('system.user.editUser') : t('system.user.createUser')"
    width="480px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item :label="t('system.user.username')" prop="username">
        <el-input v-model="form.username" :disabled="!!editingId" />
      </el-form-item>
      <el-form-item :label="t('system.user.nickname')" prop="nickname">
        <el-input v-model="form.nickname" />
      </el-form-item>
      <el-form-item v-if="!editingId" :label="t('system.user.password')" prop="password">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item :label="t('system.user.role')" prop="role_ids">
        <el-select v-model="form.role_ids" multiple :placeholder="t('system.user.selectRole')" style="width: 100%">
          <el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('system.user.status')">
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
import { getUsers, createUser, updateUser, deleteUser, getAllRoles } from '@/api'

const { t } = useI18n()

interface UserRow {
  id: number
  username: string
  nickname: string
  dept?: { id: number; name: string }
  roles: { id: number; name: string }[]
  status: number
  created_at: string
}

const list = ref<UserRow[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const roleOptions = ref<any[]>([])

const query = reactive({ page: 1, page_size: 10, keyword: '' })
const formRef = ref<FormInstance>()
const form = reactive({
  username: '',
  nickname: '',
  password: '',
  role_ids: [] as number[],
  status: 1,
})

const rules: FormRules = {
  username: [{ required: true, message: () => t('common.validation.required', { name: t('system.user.username') }), trigger: 'blur' }],
  password: [{ required: true, message: () => t('common.validation.required', { name: t('system.user.password') }), trigger: 'blur' }],
}

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getUsers({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

async function loadRoles() {
  try {
    const data: any = await getAllRoles()
    roleOptions.value = data || []
  } catch {
    roleOptions.value = []
  }
}

function openDialog(row?: UserRow) {
  editingId.value = row?.id ?? null
  form.username = row?.username ?? ''
  form.nickname = row?.nickname ?? ''
  form.password = ''
  form.role_ids = row?.roles?.map((r) => r.id) ?? []
  form.status = row?.status ?? 1
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (editingId.value) {
        await updateUser(editingId.value, {
          nickname: form.nickname,
          status: form.status,
          role_ids: form.role_ids,
        })
        ElMessage.success(t('common.message.updateSuccess'))
      } else {
        await createUser({
          username: form.username,
          nickname: form.nickname,
          password: form.password,
          role_ids: form.role_ids,
          status: form.status,
        })
        ElMessage.success(t('common.message.createSuccess'))
      }
      dialogVisible.value = false
      fetchData()
    } finally {
      saving.value = false
    }
  })
}

async function handleDelete(row: UserRow) {
  await ElMessageBox.confirm(t('system.user.deleteConfirm', { name: row.username }), t('common.action.tip'), { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success(t('common.message.deleteSuccess'))
  fetchData()
}

function formatTime(t: string) {
  if (!t) return '—'
  return t.replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  fetchData()
  loadRoles()
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
.role-tag {
  margin-right: 4px;
}
.pagination {
  margin-top: 14px;
  justify-content: flex-end;
}
</style>