<template>
  <div class="aimeeting-env-page">
    <div class="page-header">
      <div>
        <h2>运行环境</h2>
        <p class="text-muted">AI 会议语音转写所需依赖与模型的只读自检。本页面不执行任何安装或下载。</p>
      </div>
      <el-button :loading="loading" @click="fetchCheck">
        <el-icon><Refresh /></el-icon> 重新检测
      </el-button>
    </div>

    <!-- 总状态横幅 -->
    <el-alert
      v-if="data"
      :type="overallType"
      :closable="false"
      show-icon
      class="overall-alert"
    >
      <template #title>
        <span class="overall-title">{{ overallText }}</span>
      </template>
      <div class="overall-body">
        <span>依赖库 {{ s.deps_ok }}/{{ s.deps_total }}</span>
        <el-divider direction="vertical" />
        <span>模型 {{ s.models_ok }}/{{ s.models_total }}</span>
        <el-divider direction="vertical" />
        <span>Python {{ data.python?.version }}</span>
        <el-divider direction="vertical" />
        <span>ffmpeg {{ data.ffmpeg?.available ? '可用' : '未检测到' }}</span>
      </div>
      <div v-if="s.missing_deps.length" class="missing-line">
        缺失依赖：<el-tag v-for="d in s.missing_deps" :key="d" size="small" type="danger" class="mr">{{ d }}</el-tag>
      </div>
      <div v-if="s.missing_critical_models.length" class="missing-line">
        缺失核心模型：<el-tag v-for="m in s.missing_critical_models" :key="m" size="small" type="danger" class="mr">{{ m }}</el-tag>
      </div>
      <div v-if="s.degraded_models.length" class="missing-line">
        降级（可选模型缺失）：<el-tag v-for="m in s.degraded_models" :key="m" size="small" type="warning" class="mr">{{ m }}</el-tag>
      </div>
    </el-alert>

    <el-empty v-if="!data && !loading" description="点击「重新检测」获取环境状态" />

    <div v-loading="loading">
      <!-- 依赖库 -->
      <el-card v-if="data" shadow="never" class="section-card">
        <template #header><span>Python 依赖库</span></template>
        <el-table :data="data.dependencies" size="small">
          <el-table-column label="状态" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.ok ? 'success' : 'danger'" size="small">{{ row.ok ? 'OK' : '缺失' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="pip" label="包名" width="180" />
          <el-table-column label="已装版本" width="120">
            <template #default="{ row }">{{ row.installed || '—' }}</template>
          </el-table-column>
          <el-table-column prop="wanted" label="期望版本" width="110" />
          <el-table-column prop="role" label="用途" min-width="220" show-overflow-tooltip />
        </el-table>
      </el-card>

      <!-- 模型文件 -->
      <el-card v-if="data" shadow="never" class="section-card">
        <template #header><span>本地模型文件</span></template>
        <el-table :data="data.models" size="small">
          <el-table-column label="状态" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.ok ? 'success' : (row.critical ? 'danger' : 'warning')" size="small">
                {{ row.ok ? 'OK' : (row.critical ? '缺失' : '降级') }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="模型" width="220" />
          <el-table-column label="体积" width="100">
            <template #default="{ row }">{{ row.size_mb ? row.size_mb + ' MB' : '—' }}</template>
          </el-table-column>
          <el-table-column prop="role" label="说明" min-width="240" show-overflow-tooltip />
          <el-table-column label="路径" min-width="240" show-overflow-tooltip>
            <template #default="{ row }"><code class="path">{{ row.path }}</code></template>
          </el-table-column>
          <el-table-column label="缺失文件" min-width="160">
            <template #default="{ row }">
              <span v-if="!row.missing_files?.length" class="text-muted">—</span>
              <el-tag v-for="f in row.missing_files" :key="f" size="small" type="info" class="mr">{{ f }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 补齐指引 -->
      <el-card v-if="data && data.overall !== 'ready'" shadow="never" class="section-card guide-card">
        <template #header><span>如何补齐环境</span></template>
        <ol class="guide">
          <li>在服务器 backend 目录运行一键脚本：<code>bash scripts/setup_aimeeting_env.sh</code></li>
          <li>脚本会安装 Python 依赖（<code>pip install -e ".[meeting]"</code>）并检查模型目录。</li>
          <li>faster-whisper 模型可从 HuggingFace 自动下载；<b>sherpa 声纹/流式模型建议从现有部署机拷贝</b> <code>backend/models/</code> 对应目录。</li>
          <li>补齐后<b>重启后端</b>，再回本页「重新检测」。系统不提供在线安装/下载按钮（避免在运行的服务里改依赖导致不可控故障）。</li>
        </ol>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { checkEnv } from '@/api/aimeeting'

const loading = ref(false)
const data = ref<any>(null)

const s = computed(() => data.value?.summary || { deps_ok: 0, deps_total: 0, models_ok: 0, models_total: 0, missing_deps: [], missing_critical_models: [], degraded_models: [] })
const overallType = computed(() => (data.value?.overall === 'ready' ? 'success' : data.value?.overall === 'degraded' ? 'warning' : 'error'))
const overallText = computed(() => {
  switch (data.value?.overall) {
    case 'ready': return '环境就绪 — 转写、说话人分离、实时流式全部可用'
    case 'degraded': return '环境降级 — 主流程可用，部分能力（说话人分离/实时流式）受限'
    case 'broken': return '环境不完整 — 语音转写核心依赖缺失，功能不可用'
    default: return '环境状态未知'
  }
})

async function fetchCheck() {
  loading.value = true
  try {
    data.value = await checkEnv()
  } catch {
    // interceptor 已提示
  } finally {
    loading.value = false
  }
}

onMounted(fetchCheck)
</script>

<style scoped>
.aimeeting-env-page { padding: 20px; }
.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0 0 4px; font-size: 20px; }
.page-header .text-muted { color: #999; font-size: 13px; margin: 0; }
.overall-alert { margin-bottom: 16px; }
.overall-title { font-weight: 600; font-size: 15px; }
.overall-body { margin-top: 6px; font-size: 13px; }
.missing-line { margin-top: 6px; font-size: 13px; }
.mr { margin-right: 6px; }
.section-card { margin-bottom: 16px; }
.path { font-size: 12px; color: #666; word-break: break-all; }
.text-muted { color: #999; }
.guide { margin: 0; padding-left: 20px; line-height: 1.9; font-size: 13px; }
.guide code { background: #f5f5f5; padding: 1px 5px; border-radius: 3px; }
</style>
