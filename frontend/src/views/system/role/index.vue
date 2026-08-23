<template>
  <el-card shadow="never" class="page-card">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索角色名"
        clearable
        style="width: 220px"
        @keyup.enter="fetchData"
      />
      <el-button type="primary" @click="fetchData">
        <el-icon><Search /></el-icon>查询
      </el-button>
      <el-button type="success" @click="openDialog()">
        <el-icon><Plus /></el-icon>新增
      </el-button>
    </div>

    <!-- Table -->
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="角色名称" min-width="120" />
      <el-table-column prop="code" label="角色编码" min-width="120" />
      <el-table-column label="数据范围" width="120">
        <template #default="{ row }">{{ scopeText[row.data_scope] || row.data_scope }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="warning" @click="openMenuDialog(row)">分配菜单</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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

  <!-- 角色编辑 Dialog -->
  <el-dialog
    v-model="dialogVisible"
    :title="editingId ? '编辑角色' : '新增角色'"
    width="480px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="角色编码" prop="code">
        <el-input v-model="form.code" :disabled="!!editingId" placeholder="如: operator" />
      </el-form-item>
      <el-form-item label="数据范围">
        <el-select v-model="form.data_scope" style="width: 100%">
          <el-option :value="1" label="仅本人数据" />
          <el-option :value="2" label="本部门及以下" />
          <el-option :value="3" label="本部门数据" />
          <el-option :value="4" label="全部数据" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" />
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

  <!-- 分配菜单 Dialog -->
  <el-dialog
    v-model="menuDialogVisible"
    title="分配菜单权限"
    width="520px"
  >
    <div class="menu-tree-header">
      <el-checkbox v-model="menuExpandAll" @change="handleExpandAll">展开/折叠</el-checkbox>
      <el-checkbox v-model="menuCheckAll" @change="handleCheckAll">全选/全不选</el-checkbox>
      <el-checkbox v-model="menuCheckStrictly">父子联动</el-checkbox>
    </div>
    <el-tree
      ref="menuTreeRef"
      :data="menuTreeData"
      show-checkbox
      node-key="id"
      :props="{ label: 'name', children: 'children' }"
      :default-expand-all="menuExpandAll"
      :check-strictly="!menuCheckStrictly"
      class="menu-tree"
    />
    <template #footer>
      <el-button @click="menuDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="menuSaving" @click="handleSaveMenus">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import type { ElTree } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole, getMenuTree } from '@/api'

interface RoleRow {
  id: number
  name: string
  code: string
  data_scope: number
  status: number
  remark: string
  menu_ids?: number[]
}

const scopeText: Record<number, string> = {
  1: '仅本人',
  2: '本部门及以下',
  3: '本部门',
  4: '全部',
}

const list = ref<RoleRow[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const query = reactive({ page: 1, page_size: 10, keyword: '' })
const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  code: '',
  data_scope: 1,
  status: 1,
  remark: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

// ===== 分配菜单 =====
const menuDialogVisible = ref(false)
const menuSaving = ref(false)
const menuTreeRef = ref<InstanceType<typeof ElTree>>()
const menuTreeData = ref<any[]>([])
const menuExpandAll = ref(true)
const menuCheckAll = ref(false)
const menuCheckStrictly = ref(true)
const currentRoleId = ref<number | null>(null)

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getRoles({
      page: query.page,
      page_size: query.page_size,
    })
    list.value = (data.items || []).map((r: any) => ({ ...r, dataScope: r.data_scope }))
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function openDialog(row?: RoleRow) {
  editingId.value = row?.id ?? null
  form.name = row?.name ?? ''
  form.code = row?.code ?? ''
  form.data_scope = row?.data_scope ?? 1
  form.status = row?.status ?? 1
  form.remark = row?.remark ?? ''
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (editingId.value) {
        await updateRole(editingId.value, {
          name: form.name,
          data_scope: form.data_scope,
          status: form.status,
          remark: form.remark,
        })
        ElMessage.success('更新成功')
      } else {
        await createRole({
          name: form.name,
          code: form.code,
          data_scope: form.data_scope,
          status: form.status,
          remark: form.remark,
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

async function handleDelete(row: RoleRow) {
  await ElMessageBox.confirm(`确定删除角色「${row.name}」吗？`, '提示', { type: 'warning' })
  await deleteRole(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

// ===== 分配菜单逻辑 =====
async function openMenuDialog(row: RoleRow) {
  currentRoleId.value = row.id

  // 加载菜单树
  if (!menuTreeData.value.length) {
    const data: any = await getMenuTree()
    menuTreeData.value = data || []
  }

  // 加载角色当前已分配的菜单 ID
  const roleData: any = await getRoleDetail(row.id)
  const menuIds = roleData?.menu_ids || []

  menuDialogVisible.value = true

  await nextTick()
  // 设置已勾选的菜单
  menuTreeRef.value?.setCheckedKeys(menuIds)
}

async function getRoleDetail(id: number) {
  // 复用 getRoles 接口，后端 GET /roles/{id} 返回含 menu_ids
  const { default: request } = await import('@/api/request')
  const res: any = await request.get(`/roles/${id}`)
  return res
}

function handleExpandAll(val: any) {
  // el-tree 通过 default-expand-all 控制，切换需要刷新
  // 这里简单处理：设置 val 后，树会响应式更新
  menuExpandAll.value = val
}

function handleCheckAll(val: any) {
  if (val) {
    // 全选：收集所有节点 id
    const allIds = collectAllIds(menuTreeData.value)
    menuTreeRef.value?.setCheckedKeys(allIds)
  } else {
    menuTreeRef.value?.setCheckedKeys([])
  }
}

function collectAllIds(nodes: any[]): number[] {
  const ids: number[] = []
  function traverse(items: any[]) {
    for (const item of items) {
      ids.push(item.id)
      if (item.children) traverse(item.children)
    }
  }
  traverse(nodes)
  return ids
}

async function handleSaveMenus() {
  if (!currentRoleId.value) return
  menuSaving.value = true
  try {
    const checkedKeys = menuTreeRef.value?.getCheckedKeys() || []
    const halfCheckedKeys = menuTreeRef.value?.getHalfCheckedKeys() || []
    const allMenuIds = [...checkedKeys, ...halfCheckedKeys]

    await updateRole(currentRoleId.value, {
      menu_ids: allMenuIds,
    })
    ElMessage.success('菜单分配成功')
    menuDialogVisible.value = false
    fetchData()
  } finally {
    menuSaving.value = false
  }
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
.pagination {
  margin-top: 14px;
  justify-content: flex-end;
}
.menu-tree-header {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}
.menu-tree {
  max-height: 400px;
  overflow-y: auto;
}
</style>
