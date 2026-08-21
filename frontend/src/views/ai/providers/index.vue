<template>
  <el-card shadow="never" class="page-card">
    <!-- Toolbar -->
    <div class="toolbar">
      <el-button type="success" @click="openDialog()">
        <el-icon><Plus /></el-icon>新增模型密钥
      </el-button>
      <el-button type="primary" @click="fetchData">
        <el-icon><Refresh /></el-icon>刷新
      </el-button>
    </div>

    <!-- Table -->
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="供应商名称" min-width="140" />
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="providerTagType(row.provider_type)" size="small">
            {{ providerTypeLabel(row.provider_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="base_url" label="API 地址" min-width="240" show-overflow-tooltip />
      <el-table-column label="模型" min-width="200">
        <template #default="{ row }">
          <el-tag v-for="m in row.models" :key="m" size="small" class="model-tag">{{ m }}</el-tag>
          <span v-if="!row.models?.length">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="api_key_masked" label="API Key" width="180" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.enabled === 1 ? 'success' : 'info'" size="small">
            {{ row.enabled === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sort" label="排序" width="70" />
      <el-table-column label="操作" width="230" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleTest(row)">
            <el-icon><Connection /></el-icon>测试
          </el-button>
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
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

  <!-- Dialog -->
  <el-dialog
    v-model="dialogVisible"
    :title="editingId ? '编辑模型密钥' : '新增模型密钥'"
    width="560px"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="供应商名称" prop="name">
        <el-input v-model="form.name" placeholder="如：DeepSeek 生产环境" />
      </el-form-item>
      <el-form-item label="类型" prop="provider_type">
        <el-select v-model="form.provider_type" placeholder="选择类型" style="width: 100%" @change="onTypeChange">
          <el-option label="DeepSeek" value="deepseek" />
          <el-option label="通义千问 (Qwen)" value="qwen" />
          <el-option label="智谱 GLM" value="glm" />
          <el-option label="OpenAI" value="openai" />
          <el-option label="自定义 (Custom)" value="custom" />
        </el-select>
      </el-form-item>
      <el-form-item label="API Key" prop="api_key">
        <el-input
          v-model="form.api_key"
          type="password"
          show-password
          :placeholder="editingId ? '留空则不修改' : '请输入 API Key'"
        />
      </el-form-item>
      <el-form-item label="API 地址" prop="base_url">
        <el-input v-model="form.base_url" placeholder="如：https://api.deepseek.com" />
      </el-form-item>
      <el-form-item label="模型列表" prop="models">
        <div class="models-editor">
          <div v-for="(m, i) in form.models" :key="i" class="model-row">
            <el-input v-model="form.models[i]" placeholder="模型名称" />
            <el-button link type="danger" @click="form.models.splice(i, 1)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button size="small" @click="form.models.push('')">
            <el-icon><Plus /></el-icon>添加模型
          </el-button>
        </div>
      </el-form-item>
      <el-form-item label="启用状态">
        <el-switch v-model="form.enabled" :active-value="1" :inactive-value="0" />
      </el-form-item>
      <el-form-item label="排序">
        <el-input-number v-model="form.sort" :min="0" :max="999" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>

  <!-- Test Result Dialog -->
  <el-dialog v-model="testResultVisible" title="连通性测试" width="420px">
    <div v-if="testLoading" class="test-loading">
      <el-icon class="is-loading" :size="24"><Loading /></el-icon>
      <span>正在测试连通性...</span>
    </div>
    <div v-else class="test-result">
      <el-result
        :icon="testResult.ok ? 'success' : 'error'"
        :title="testResult.ok ? '连通成功' : '连通失败'"
        :sub-title="testResult.ok ? `可用模型 ${testResult.models?.length || 0} 个` : testResult.error || ''"
      />
      <div v-if="testResult.ok && testResult.models?.length" class="test-models">
        <el-tag v-for="m in testResult.models" :key="m" size="small" class="model-tag">{{ m }}</el-tag>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { getProviders, createProvider, updateProvider, deleteProvider, testProvider } from '@/api'

interface ProviderRow {
  id: number
  name: string
  provider_type: string
  base_url: string
  models: string[]
  enabled: number
  sort: number
  remark: string | null
  api_key_masked: string
  created_at: string
}

const list = ref<ProviderRow[]>([])
const total = ref(0)
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const query = reactive({ page: 1, page_size: 10 })
const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  provider_type: 'deepseek',
  api_key: '',
  base_url: '',
  models: [] as string[],
  enabled: 1,
  sort: 0,
  remark: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  provider_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
}

// Test dialog
const testResultVisible = ref(false)
const testLoading = ref(false)
const testResult = ref<any>({})

const PROVIDER_PRESETS: Record<string, { base_url: string; models: string[] }> = {
  deepseek: { base_url: 'https://api.deepseek.com', models: ['deepseek-chat', 'deepseek-reasoner'] },
  qwen: { base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', models: ['qwen-plus', 'qwen-max', 'qwen-turbo'] },
  glm: { base_url: 'https://open.bigmodel.cn/api/paas/v4', models: ['glm-4-flash', 'glm-4', 'glm-4-air'] },
  openai: { base_url: 'https://api.openai.com/v1', models: ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo'] },
  custom: { base_url: '', models: [] },
}

function onTypeChange(type: string) {
  const preset = PROVIDER_PRESETS[type]
  if (preset) {
    if (!form.base_url) form.base_url = preset.base_url
    if (form.models.length === 0) form.models = [...preset.models]
  }
}

function providerTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    deepseek: 'DeepSeek',
    qwen: '通义千问',
    glm: '智谱GLM',
    openai: 'OpenAI',
    custom: '自定义',
  }
  return labels[type] || type
}

function providerTagType(type: string): string {
  const types: Record<string, string> = {
    deepseek: 'primary',
    qwen: 'success',
    glm: 'warning',
    openai: 'info',
    custom: '',
  }
  return types[type] || ''
}

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getProviders({ page: query.page, page_size: query.page_size })
    list.value = data.items || []
    total.value = data.total || 0
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.provider_type = 'deepseek'
  form.api_key = ''
  form.base_url = ''
  form.models = []
  form.enabled = 1
  form.sort = 0
  form.remark = ''
  editingId.value = null
  formRef.value?.resetFields()
}

function openDialog(row?: ProviderRow) {
  resetForm()
  if (row) {
    editingId.value = row.id
    form.name = row.name
    form.provider_type = row.provider_type
    form.base_url = row.base_url
    form.models = [...(row.models || [])]
    form.enabled = row.enabled
    form.sort = row.sort
    form.remark = row.remark || ''
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!formRef.value) return
  // 过滤空模型名
  const models = form.models.filter((m) => m.trim())
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (editingId.value) {
        const payload: any = {
          name: form.name,
          provider_type: form.provider_type,
          base_url: form.base_url,
          models,
          enabled: form.enabled,
          sort: form.sort,
          remark: form.remark || null,
        }
        if (form.api_key) payload.api_key = form.api_key
        await updateProvider(editingId.value, payload)
        ElMessage.success('更新成功')
      } else {
        if (!form.api_key) {
          ElMessage.warning('请输入 API Key')
          saving.value = false
          return
        }
        await createProvider({
          name: form.name,
          provider_type: form.provider_type,
          api_key: form.api_key,
          base_url: form.base_url,
          models,
          enabled: form.enabled,
          sort: form.sort,
          remark: form.remark || null,
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

async function handleDelete(row: ProviderRow) {
  await ElMessageBox.confirm(`确定删除模型密钥「${row.name}」吗？`, '提示', { type: 'warning' })
  await deleteProvider(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

async function handleTest(row: ProviderRow) {
  testResultVisible.value = true
  testLoading.value = true
  testResult.value = {}
  try {
    const data: any = await testProvider(row.id)
    testResult.value = data
  } catch (err: any) {
    testResult.value = { ok: false, error: err.message || '请求失败' }
  } finally {
    testLoading.value = false
  }
}

onMounted(() => {
  fetchData()
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
.model-tag {
  margin: 2px 4px 2px 0;
}
.pagination {
  margin-top: 14px;
  justify-content: flex-end;
}
.models-editor {
  width: 100%;
}
.model-row {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 6px;
}
.test-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px 0;
  color: #909399;
}
.test-result {
  text-align: center;
}
.test-models {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  margin-top: 12px;
  max-height: 200px;
  overflow-y: auto;
}
</style>
