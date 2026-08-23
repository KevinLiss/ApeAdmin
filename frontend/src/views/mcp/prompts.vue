<template>
  <el-card shadow="never" class="page-card">
    <div class="toolbar">
      <el-button type="primary" @click="fetchData">
        <el-icon><Refresh /></el-icon>刷新
      </el-button>
    </div>

    <el-table :data="prompts" v-loading="loading" stripe>
      <el-table-column prop="name" label="提示词名称" width="200" />
      <el-table-column prop="description" label="描述" min-width="260" />
      <el-table-column label="参数" min-width="180">
        <template #default="{ row }">
          <el-tag v-for="arg in row.arguments || []" :key="arg" size="small" class="param-tag">
            {{ arg }}
          </el-tag>
          <span v-if="!(row.arguments || []).length" style="color: #909399">无参数</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openRender(row)">渲染</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- Render dialog -->
  <el-dialog v-model="renderVisible" :title="`渲染提示词: ${currentPrompt?.name || ''}`" width="600px">
    <el-form label-width="90px">
      <el-form-item v-for="arg in currentPrompt?.arguments || []" :key="arg" :label="arg">
        <el-input v-model="renderArgs[arg]" :placeholder="`请输入 ${arg}`" />
      </el-form-item>
      <el-form-item v-if="!(currentPrompt?.arguments || []).length" label="说明">
        <span style="color: #909399">该提示词无参数，可直接渲染</span>
      </el-form-item>
    </el-form>
    <div v-if="rendered !== null" class="result-box">
      <pre>{{ rendered }}</pre>
    </div>
    <template #footer>
      <el-button @click="renderVisible = false">关闭</el-button>
      <el-button type="primary" :loading="rendering" @click="doRender">渲染</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMcpPrompts, renderMcpPrompt } from '@/api'

const prompts = ref<any[]>([])
const loading = ref(false)
const renderVisible = ref(false)
const rendering = ref(false)
const currentPrompt = ref<any>(null)
const renderArgs = reactive<Record<string, string>>({})
const rendered = ref<string | null>(null)

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getMcpPrompts()
    prompts.value = data || []
  } finally {
    loading.value = false
  }
}

function openRender(row: any) {
  currentPrompt.value = row
  Object.keys(renderArgs).forEach((k) => delete renderArgs[k])
  rendered.value = null
  renderVisible.value = true
}

async function doRender() {
  if (!currentPrompt.value) return
  rendering.value = true
  try {
    const typedArgs: Record<string, string> = {}
    for (const k of Object.keys(renderArgs)) {
      if (renderArgs[k]) typedArgs[k] = renderArgs[k]
    }
    const data: any = await renderMcpPrompt(currentPrompt.value.name, typedArgs)
    rendered.value = data?.rendered || ''
    ElMessage.success('渲染成功')
  } catch {
    // error handled by interceptor
  } finally {
    rendering.value = false
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
.param-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}
.result-box {
  margin-top: 12px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  max-height: 240px;
  overflow: auto;
  font-size: 12px;
  font-family: monospace;
  white-space: pre-wrap;
}
</style>