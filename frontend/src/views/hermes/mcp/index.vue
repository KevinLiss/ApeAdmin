<template>
  <div class="hermes-mcp-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button :icon="Refresh" :loading="loading" @click="loadData">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openAddDialog">添加服务器</el-button>
      </div>
      <div class="toolbar-right">
        <el-tag size="small" type="info" effect="plain">共 {{ servers.length }} 个 MCP 服务器</el-tag>
      </div>
    </div>

    <!-- MCP 服务器表格 -->
    <el-card shadow="never" class="card">
      <template #header>
        <div class="card-header">
          <span>MCP 服务器</span>
        </div>
      </template>
      <el-table :data="servers" v-loading="loading" border stripe>
        <el-table-column prop="name" label="名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="transport" label="传输方式" width="160">
          <template #default="{ row }">
            <el-tag :type="transportTagType(row.transport)" size="small" effect="plain">
              {{ row.transport || 'unknown' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="130">
          <template #default="{ row }">
            <el-tag :type="row.status === 'connected' ? 'success' : 'danger'" size="small">
              <span class="dot" :class="{ online: row.status === 'connected' }"></span>
              {{ row.status || 'unknown' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="工具数" width="100" align="center">
          <template #default="{ row }">
            {{ row.tool_count ?? row.tools?.length ?? 0 }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :icon="Connection" :loading="testing === row.name" @click="testServer(row)">
              测试
            </el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="removeServer(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!servers.length && !loading" description="暂无 MCP 服务器" :image-size="80" />
    </el-card>

    <!-- 添加 MCP 服务器弹窗 -->
    <el-dialog v-model="addVisible" title="添加 MCP 服务器" width="560px" destroy-on-close>
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="110px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="addForm.name" placeholder="如：filesystem / playwright" clearable />
        </el-form-item>
        <el-form-item label="传输方式" prop="transport">
          <el-select v-model="addForm.transport" style="width: 100%">
            <el-option label="stdio" value="stdio" />
            <el-option label="sse" value="sse" />
            <el-option label="streamable_http" value="streamable_http" />
          </el-select>
        </el-form-item>
        <template v-if="addForm.transport === 'stdio'">
          <el-form-item label="启动命令" prop="command">
            <el-input
              v-model="addForm.command"
              placeholder="如：npx -y @modelcontextprotocol/server-filesystem"
              clearable
            />
          </el-form-item>
          <el-form-item label="参数 (args)">
            <el-input
              v-model="addForm.args"
              type="textarea"
              :rows="2"
              placeholder="每行一个参数，如：/Users/mac/data"
            />
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item label="端点 URL" prop="url">
            <el-input
              v-model="addForm.url"
              placeholder="如：http://127.0.0.1:8000/sse 或 /mcp"
              clearable
            />
          </el-form-item>
        </template>
        <el-form-item label="环境变量 (env)">
          <el-input
            v-model="addForm.env"
            type="textarea"
            :rows="3"
            placeholder='JSON 格式，如：{"API_KEY":"xxx"}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submitAdd">保存</el-button>
      </template>
    </el-dialog>

    <!-- 测试结果弹窗 -->
    <el-dialog v-model="testVisible" title="连接测试结果" width="560px">
      <div class="test-result" :class="{ ok: testResult?.ok }">
        <pre class="test-json">{{ testText }}</pre>
      </div>
      <template #footer>
        <el-button type="primary" @click="testVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- MCP Catalog -->
    <el-card shadow="never" class="card catalog-card">
      <template #header>
        <div class="card-header">
          <span>MCP Catalog</span>
          <el-button size="small" :icon="Refresh" text :loading="catalogLoading" @click="loadCatalog">
            刷新
          </el-button>
        </div>
      </template>
      <el-table :data="catalog" v-loading="catalogLoading" border stripe>
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="260" show-overflow-tooltip />
        <el-table-column label="安装方式" min-width="240">
          <template #default="{ row }">
            <code class="cmd">{{ row.command || row.install || row.package || '-' }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.source" size="small" effect="plain">{{ row.source }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!catalog.length && !catalogLoading" description="暂无可用 Catalog" :image-size="80" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from 'element-plus'
import { Refresh, Plus, Delete, Connection } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

interface McpServer {
  name: string
  transport?: string
  status?: string
  tools?: unknown[]
  tool_count?: number
  [key: string]: unknown
}

// ── 列表加载 ──────────────────────────────────────
const loading = ref(false)
const servers = ref<McpServer[]>([])
const catalog = ref<Record<string, any>[]>([])
const catalogLoading = ref(false)

async function loadServers() {
  loading.value = true
  try {
    const res: any = await hermes.getMcpServers()
    // dashboard/plugins 返回格式可能是数组或 { plugins: [...] }
    servers.value = res?.plugins ?? res?.servers ?? (Array.isArray(res) ? res : [])
  } catch (e: any) {
    ElMessage.error(e?.message || '获取 MCP 服务器列表失败')
  } finally {
    loading.value = false
  }
}

async function loadCatalog() {
  catalogLoading.value = true
  try {
    const res: any = await hermes.getMcpCatalog()
    catalog.value = res?.catalog ?? (Array.isArray(res) ? res : [])
  } catch (e: any) {
    ElMessage.error(e?.message || '获取 MCP Catalog 失败')
  } finally {
    catalogLoading.value = false
  }
}

async function loadData() {
  await Promise.all([loadServers(), loadCatalog()])
}

// ── 添加服务器 ─────────────────────────────────────
const addVisible = ref(false)
const saving = ref(false)
const addFormRef = ref<FormInstance>()
const addForm = reactive({
  name: '',
  transport: 'stdio',
  command: '',
  url: '',
  env: '',
  args: '',
})

const addRules: FormRules = {
  name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
  transport: [{ required: true, message: '请选择传输方式', trigger: 'change' }],
  command: [{ required: true, message: '请输入启动命令', trigger: 'blur' }],
  url: [{ required: true, message: '请输入端点 URL', trigger: 'blur' }],
}

function openAddDialog() {
  addForm.name = ''
  addForm.transport = 'stdio'
  addForm.command = ''
  addForm.url = ''
  addForm.env = ''
  addForm.args = ''
  addVisible.value = true
}

function parseArgs(text: string): string[] {
  return text
    .split(/[\n,]/)
    .map((s) => s.trim())
    .filter(Boolean)
}

function parseEnv(text: string): Record<string, string> | undefined {
  const trimmed = text.trim()
  if (!trimmed) return undefined
  try {
    return JSON.parse(trimmed)
  } catch {
    ElMessage.error('环境变量不是合法的 JSON 格式')
    throw new Error('INVALID_ENV')
  }
}

async function submitAdd() {
  const valid = await addFormRef.value?.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    const payload: Record<string, any> = {
      name: addForm.name.trim(),
      transport: addForm.transport,
    }
    if (addForm.transport === 'stdio') {
      payload.command = addForm.command.trim()
      payload.args = parseArgs(addForm.args)
    } else {
      payload.url = addForm.url.trim()
    }
    const env = parseEnv(addForm.env)
    if (env) payload.env = env

    await hermes.addMcpServer(payload)
    ElMessage.success('已添加 MCP 服务器')
    addVisible.value = false
    loadServers()
  } catch (e: any) {
    if (e?.message !== 'INVALID_ENV') {
      ElMessage.error(e?.message || '添加失败')
    }
  } finally {
    saving.value = false
  }
}

// ── 删除服务器 ─────────────────────────────────────
async function removeServer(row: McpServer) {
  try {
    await ElMessageBox.confirm(`确定删除 MCP 服务器「${row.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await hermes.removeMcpServer(row.name)
    ElMessage.success('已删除')
    loadServers()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

// ── 测试连接 ───────────────────────────────────────
const testing = ref<string | null>(null)
const testVisible = ref(false)
const testResult = ref<any>(null)

const testText = computed(() => {
  if (!testResult.value) return ''
  return JSON.stringify(testResult.value, null, 2)
})

async function testServer(row: McpServer) {
  testing.value = row.name
  try {
    const res: any = await hermes.testMcpServer(row.name)
    testResult.value = res ?? { ok: true }
    testVisible.value = true
  } catch (e: any) {
    testResult.value = { ok: false, error: e?.message || '连接测试失败' }
    testVisible.value = true
  } finally {
    testing.value = null
  }
}

// ── 辅助 ───────────────────────────────────────────
function transportTagType(transport?: string): '' | 'success' | 'warning' {
  if (transport === 'sse') return 'success'
  if (transport === 'streamable_http') return 'warning'
  return ''
}

onMounted(loadData)
</script>

<style scoped>
.hermes-mcp-page {
  padding: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card {
  margin-bottom: 14px;
  border-radius: 10px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f56c6c;
  margin-right: 5px;
  vertical-align: middle;
}

.dot.online {
  background: #67c23a;
}

.cmd {
  font-family: 'SF Mono', 'Monaco', monospace;
  font-size: 12px;
  color: var(--el-color-primary);
  background: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 4px;
}

.test-result {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 12px;
  max-height: 320px;
  overflow: auto;
}

.test-result.ok {
  border-color: rgba(103, 194, 58, 0.4);
}

.test-json {
  margin: 0;
  font-family: 'SF Mono', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--el-text-color-regular);
}
</style>