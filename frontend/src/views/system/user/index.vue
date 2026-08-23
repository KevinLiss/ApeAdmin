<template>
  <el-card shadow="never" class="page-card">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索用户名/昵称"
        clearable
        style="width: 220px"
        @keyup.enter="fetchData"
      />
      <el-button type="primary" @click="fetchData">
        <el-icon><Search /></el-icon>查询
      </el-button>
    <el-button type="success" @click="openDialog()" v-permission="'system:user:add'">
      <el-icon><Plus /></el-icon>新增
    </el-button>
    </div>

    <!-- Table -->
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" min-width="110" />
      <el-table-column prop="nickname" label="昵称" min-width="110" />
      <el-table-column label="部门" min-width="120">
        <template #default="{ row }">{{ row.dept?.name || '—' }}</template>
      </el-table-column>
      <el-table-column label="角色" min-width="140">
        <template #default="{ row }">
          <el-tag v-for="r in row.roles" :key="r.id" size="small" class="role-tag">{{ r.name }}</el-tag>
          <span v-if="!row.roles?.length">—</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)" v-permission="'system:user:edit'">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)" v-permission="'system:user:delete'">删除</el-button>
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
    :title="editingId ? '编辑用户' : '新增用户'"
    width="480px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" :disabled="!!editingId" />
      </el-form-item>
      <el-form-item label="昵称" prop="nickname">
        <el-input v-model="form.nickname" />
      </el-form-item>
      <el-form-item v-if="!editingId" label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="角色" prop="role_ids">
        <el-select v-model="form.role_ids" multiple placeholder="选择角色" style="width: 100%">
          <el-option v-for="r in roleOptions" :key="r.id" :label="r.name" :value="r.id" />
        </el-select>
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
import { getUsers, createUser, updateUser, deleteUser, getAllRoles } from '@/api'

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
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
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
        ElMessage.success('更新成功')
      } else {
        await createUser({
          username: form.username,
          nickname: form.nickname,
          password: form.password,
          role_ids: form.role_ids,
          status: form.status,
        })
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } finally {
      saving.value = false
    }
  })
}

async function handleDelete(row: UserRow) {
  await ElMessageBox.confirm(`确定删除用户「${row.username}」吗？`, '提示', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('删除成功')
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