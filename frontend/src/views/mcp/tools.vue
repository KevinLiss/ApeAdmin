<template>
  <el-card shadow="never" class="page-card">
    <div class="toolbar">
      <el-button type="primary" @click="fetchData">
        <el-icon><Refresh /></el-icon>刷新
      </el-button>
    </div>

    <el-table :data="tools" v-loading="loading" stripe>
      <el-table-column prop="name" label="工具名称" width="180" />
      <el-table-column prop="description" label="描述" min-width="250" />
      <el-table-column label="输入参数" min-width="200">
        <template #default="{ row }">
          <el-tag v-for="(v, k) in row.input_schema?.properties || {}" :key="k" size="small" class="param-tag">
            {{ k }}:{{ v.type }}
          </el-tag>
          <span v-if="!Object.keys(row.input_schema?.properties || {}).length">无参数</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" v-permission="'mcp:tools:call'" @click="openCall(row)">调用</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- Call dialog -->
  <el-dialog v-model="callVisible" :title="`调用工具: ${currentTool?.name || ''}`" width="520px">
    <el-form label-width="90px">
      <el-form-item v-for="(v, k) in currentTool?.input_schema?.properties || {}" :key="k" :label="k">
        <el-input v-model="callArgs[k]" :placeholder="`${v.type} 类型参数`" />
      </el-form-item>
      <el-form-item v-if="!Object.keys(currentTool?.input_schema?.properties || {}).length" label="说明">
        <span style="color: #909399">该工具无参数，可直接调用</span>
      </el-form-item>
    </el-form>
    <div v-if="callResult !== null" class="result-box">
      <pre>{{ JSON.stringify(callResult, null, 2) }}</pre>
    </div>
    <template #footer>
      <el-button @click="callVisible = false">关闭</el-button>
      <el-button type="primary" :loading="calling" @click="doCall">调用</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMcpTools, callMcpTool } from '@/api'

const tools = ref<any[]>([])
const loading = ref(false)
const callVisible = ref(false)
const calling = ref(false)
const currentTool = ref<any>(null)
const callArgs = reactive<Record<string, string>>({})
const neverResult = ref(null)
const callResult = ref<any>(null)

async function fetchData() {
  loading.value = true
  try {
    const data: any = await getMcpTools()
    tools.value = data || []
  } finally {
    loading.value = false
  }
}

function openCall(row: any) {
  currentTool.value = row
  // Reset args
  Object.keys(callArgs).forEach((k) => delete callArgs[k])
  callResult.value = null
  callVisible.value = true
}

async function doCall() {
  if (!currentTool.value) return
  calling.value = true
  try {
    // Convert string args to proper types based on schema
    const typedArgs: Record<string, any> = {}
    const props = currentTool.value.input_schema?.properties || {}
    for (const [k, v] of Object.entries(callArgs)) {
      const schema = props[k] as any
      if (!callArgs[k]) continue
      if (schema?.type === 'number') typedArgs[k] = Number(callArgs[k])
      else if (schema?.type === 'boolean') typedArgs[k] = callArgs[k] === 'true'
      else typedArgs[k] = callArgs[k]
    }
    const data: any = await callMcpTool(currentTool.value.name, typedArgs)
    callResult.value = data?.result
    ElMessage.success('调用成功')
  } catch {
    // error handled by interceptor
  } finally {
    calling.value = false
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
.result {
  margin-top: 12px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  max-height: 200px;
  overflow: auto;
  font-size: 12px;
  font-family: monospace;
  white-space: pre-wrap;
}
</style>