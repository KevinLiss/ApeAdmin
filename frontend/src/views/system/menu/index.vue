<template>
  <el-card shadow="never" class="page-card">
    <div class="toolbar">
      <el-button type="success" @click="openDialog()" v-permission="'system:menu:add'">
        <el-icon><Plus /></el-icon>{{ t('system.menu.createMenu') }}
      </el-button>
    </div>

    <el-table
      :data="tree"
      row-key="id"
      v-loading="loading"
      :tree-props="{ children: 'children' }"
      default-expand-all
    >
      <el-table-column prop="name" :label="t('system.menu.menuName')" min-width="180" />
      <el-table-column :label="t('common.action.type')" width="80">
        <template #default="{ row }">
          <el-tag :type="typeTag[row.type]" size="small">{{ typeText[row.type] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="path" :label="t('system.menu.route')" min-width="120" />
      <el-table-column prop="component" :label="t('system.menu.componentPath')" min-width="150" show-overflow-tooltip />
      <el-table-column prop="permission" :label="t('system.menu.permission')" min-width="150" />
      <el-table-column prop="sort" :label="t('system.menu.sort')" width="70" />
      <el-table-column :label="t('system.menu.status')" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? t('system.menu.active') : t('system.menu.disabled') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.action.actions')" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)" v-permission="'system:menu:edit'">{{ t('common.action.edit') }}</el-button>
          <el-button link type="danger" @click="handleDelete(row)" v-permission="'system:menu:delete'">{{ t('common.action.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <el-dialog v-model="dialogVisible" :title="editingId ? t('system.menu.editMenu') : t('system.menu.createMenu')" width="520px">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item :label="t('system.menu.parentMenu')">
        <el-tree-select
          v-model="form.parent_id"
          :data="parentOptions"
          :props="{ label: 'name', children: 'children' }"
          check-strictly
          clearable
          @clear="form.parent_id = 0"
          :placeholder="t('system.menu.parentPlaceholder')"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item :label="t('system.menu.menuType')">
        <el-radio-group v-model="form.type">
          <el-radio value="M">{{ t('system.menu.typeDirectory') }}</el-radio>
          <el-radio value="C">{{ t('system.menu.typeMenu') }}</el-radio>
          <el-radio value="F">{{ t('system.menu.typeButton') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item :label="t('system.menu.menuName')" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item v-if="form.type !== 'F'" :label="t('system.menu.routeAddress')" prop="path">
        <el-input v-model="form.path" :placeholder="t('system.menu.routeExample')" />
      </el-form-item>
      <el-form-item v-if="form.type !== 'F'" :label="t('system.menu.componentPath')" prop="component">
        <el-input v-model="form.component" :placeholder="t('system.menu.componentExample')" />
      </el-form-item>
      <el-form-item v-if="form.type === 'F'" :label="t('system.menu.permission')">
        <el-input v-model="form.permission" :placeholder="t('system.menu.permissionPlaceholder')" />
      </el-form-item>
      <el-form-item :label="t('system.menu.sort')">
        <el-input-number v-model="form.sort" :min="0" />
      </el-form-item>
      <el-form-item :label="t('system.menu.status')">
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getMenuTree, createMenu, updateMenu, deleteMenu } from '@/api'
import { useUserStore } from '@/stores/user'
import { refreshDynamicRoutes } from '@/router'

const { t } = useI18n()

const userStore = useUserStore()

const typeText = computed<Record<string, string>>(() => ({
  M: t('system.menu.typeDirectory'),
  C: t('system.menu.typeMenu'),
  F: t('system.menu.typeButton'),
}))
const typeTag: Record<string, string> = { M: 'info', C: 'primary', F: 'warning' }

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
  type: 'C',
  path: '',
  component: '',
  permission: '',
  sort: 0,
  status: 1,
})

const rules: FormRules = {
  name: [{ required: true, message: () => t('common.validation.required', { name: t('system.menu.menuName') }), trigger: 'blur' }],
  path: [{ required: true, message: () => t('common.validation.required', { name: t('system.menu.routeAddress') }), trigger: 'blur' }],
  component: [{
    validator: (_rule: any, value: string, callback: (err?: Error) => void) => {
      if (form.type === 'C' && !value) {
        callback(new Error(t('system.menu.componentRequired')))
      } else {
        callback()
      }
    },
    trigger: 'blur',
  }],
}

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getMenuTree()
    tree.value = data || []
    parentOptions.value = buildParentOptions(editingId.value)
  } finally {
    loading.value = false
  }
}

function removeBranch(nodes: any[], excludedId: number | null): any[] {
  return nodes
    .filter((node) => node.id !== excludedId)
    .map((node) => ({
      ...node,
      children: removeBranch(node.children || [], excludedId),
    }))
}

function buildParentOptions(excludedId: number | null = null) {
  return [{ id: 0, name: t('system.menu.topLevel'), children: removeBranch(tree.value, excludedId) }]
}

function openDialog(row?: any) {
  editingId.value = row?.id ?? null
  form.parent_id = row?.parent_id ?? 0
  form.name = row?.name ?? ''
  form.type = row?.type ?? 'C'
  form.path = row?.path ?? ''
  form.component = row?.component ?? ''
  form.permission = row?.permission ?? ''
  form.sort = row?.sort ?? 0
  form.status = row?.status ?? 1
  parentOptions.value = buildParentOptions(editingId.value)
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const payload = {
        parent_id: Number(form.parent_id) || 0,
        name: form.name,
        type: form.type,
        path: form.type === 'F' ? null : form.path,
        component: form.type === 'F' ? null : form.component,
        permission: form.type === 'F' ? form.permission : form.permission || null,
        sort: form.sort,
        status: form.status,
      }
      if (editingId.value) {
        await updateMenu(editingId.value, payload)
        ElMessage.success(t('common.message.updateSuccess'))
      } else {
        await createMenu(payload)
        ElMessage.success(t('common.message.createSuccess'))
      }
      dialogVisible.value = false
      await fetchData()
      await refreshMenuSidebar()
    } finally {
      saving.value = false
    }
  })
}

async function handleDelete(row: any) {
  await ElMessageBox.confirm(t('system.menu.deleteConfirm', { name: row.name }), t('common.action.tip'), { type: 'warning' })
  await deleteMenu(row.id)
  ElMessage.success(t('common.message.deleteSuccess'))
  await fetchData()
  await refreshMenuSidebar()
}

// 保存/删除菜单后同步刷新侧边栏菜单与动态路由，无需重新登录
async function refreshMenuSidebar() {
  try {
    await userStore.fetchUserInfo()
    refreshDynamicRoutes(userStore.menus)
  } catch (e) {
    console.error('[Menu] 刷新菜单失败:', e)
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
</style>
