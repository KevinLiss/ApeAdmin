<template>
  <div class="hermes-skills-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-tag type="info" effect="plain" size="small" class="count-tag">共 {{ total }} 个技能</el-tag>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :icon="Download" @click="installDialog = true">从 Hub 安装</el-button>
        <el-button :icon="Refresh" @click="loadSkills">刷新</el-button>
      </div>
    </div>

    <!-- 技能表格 -->
    <el-table
      :data="skills"
      v-loading="loading"
      class="skill-table"
      empty-text="暂无技能"
    >
      <el-table-column prop="name" label="名称" min-width="200">
        <template #default="{ row }">
          <span class="skill-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="skill-desc">{{ row.description || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="110">
        <template #default="{ row }">
          <el-tag :type="sourceType(row.source)" size="small" effect="plain">
            {{ sourceLabel(row.source) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-switch
            v-model="row.enabled"
            :loading="row._toggling"
            @change="toggleSkill(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="viewContent(row)">查看内容</el-button>
          <el-button v-if="isHub(row)" link type="primary" :loading="row._updating" @click="updateSkill(row)">更新</el-button>
          <el-button v-if="isHub(row)" link type="danger" :loading="row._uninstalling" @click="uninstallSkill(row)">卸载</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 从 Hub 安装弹窗 -->
    <el-dialog v-model="installDialog" title="从 Hub 安装技能" width="460px">
      <el-input
        v-model="installName"
        maxlength="120"
        placeholder="请输入技能名称，例如 hermes-tools"
        @keyup.enter="confirmInstall"
      />
      <p class="dialog-tip">技能将从 Hermes Hub 仓库拉取并安装到本地技能目录。</p>
      <template #footer>
        <el-button @click="installDialog = false">取消</el-button>
        <el-button type="primary" :loading="installing" @click="confirmInstall">安装</el-button>
      </template>
    </el-dialog>

    <!-- 查看技能内容弹窗 -->
    <el-dialog v-model="contentDialog" :title="`技能内容：${content?.name ?? ''}`" width="720px" top="6vh">
      <div v-loading="contentLoading" class="content-body">
        <pre v-if="contentText !== undefined" class="skill-content">{{ contentText }}</pre>
        <el-empty v-else-if="!contentLoading" description="暂无内容" :image-size="50" />
      </div>
      <template #footer>
        <el-button @click="contentDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElSwitch,
  ElTag,
  ElDialog,
  ElMessage,
  ElMessageBox,
  ElInput,
} from 'element-plus'
import { Refresh, Download, Upload } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

const loading = ref(false)
const skills = ref<any[]>([])

const installDialog = ref(false)
const installName = ref('')
const installing = ref(false)

const contentDialog = ref(false)
const contentLoading = ref(false)
const contentText = ref<string | undefined>(undefined)
const content = ref<any>(null)

const total = computed(() => skills.value.length)

// ── 加载 ──────────────────────────────────────────
async function loadSkills() {
  loading.value = true
  try {
    const res: any = await hermes.getSkills()
    const list = res?.skills ?? res?.items ?? (Array.isArray(res) ? res : [])
    skills.value = (list || []).map((s: any) => ({
      ...s,
      name: s.name ?? '',
      description: s.description ?? '',
      source: s.source ?? (s.local ? 'local' : 'hub'),
      enabled: !!s.enabled,
      _toggling: false,
      _updating: false,
      _uninstalling: false,
    }))
  } catch (e: any) {
    ElMessage.error(`加载技能失败: ${e.message || e}`)
  } finally {
    loading.value = false
  }
}

// ── 启用 / 禁用 ───────────────────────────────────
async function toggleSkill(row: any) {
  const target = !!row.enabled
  row._toggling = true
  try {
    await hermes.toggleSkill(row.name, target)
    ElMessage.success(`${target ? '已启用' : '已禁用'}: ${row.name}`)
  } catch (e: any) {
    // 失败回滚开关状态
    row.enabled = !target
    ElMessage.error(`操作失败: ${e.message || e}`)
  } finally {
    row._toggling = false
  }
}

// ── 来源判断 ──────────────────────────────────────
function isHub(row: any): boolean {
  return String(row.source).toLowerCase() === 'hub'
}

function sourceLabel(source?: string): string {
  return String(source ?? 'local').toLowerCase() === 'hub' ? 'Hub' : '本地'
}

function sourceType(source?: string): 'primary' | 'info' {
  return String(source ?? 'local').toLowerCase() === 'hub' ? 'primary' : 'info'
}

// ── 从 Hub 安装 ───────────────────────────────────
async function confirmInstall() {
  const name = installName.value.trim()
  if (!name) {
    ElMessage.warning('请输入技能名称')
    return
  }
  installing.value = true
  try {
    await hermes.installSkillHub(name)
    ElMessage.success(`技能安装成功: ${name}`)
    installDialog.value = false
    installName.value = ''
    loadSkills()
  } catch (e: any) {
    ElMessage.error(`安装失败: ${e.message || e}`)
  } finally {
    installing.value = false
  }
}

// ── 卸载技能 ──────────────────────────────────────
async function uninstallSkill(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定卸载技能「${row.name}」吗？该技能将从本地移除。`,
      '卸载确认',
      {
        type: 'warning',
        confirmButtonText: '卸载',
        cancelButtonText: '取消',
        confirmButtonClass: 'el-button--danger',
      }
    )
  } catch {
    return
  }
  row._uninstalling = true
  try {
    await hermes.uninstallSkillHub(row.name)
    ElMessage.success(`技能已卸载: ${row.name}`)
    loadSkills()
  } catch (e: any) {
    ElMessage.error(`卸载失败: ${e.message || e}`)
  } finally {
    row._uninstalling = false
  }
}

// ── 更新技能 ──────────────────────────────────────
async function updateSkill(row: any) {
  row._updating = true
  try {
    await hermes.updateSkillHub(row.name)
    ElMessage.success(`技能已更新: ${row.name}`)
    loadSkills()
  } catch (e: any) {
    ElMessage.error(`更新失败: ${e.message || e}`)
  } finally {
    row._updating = false
  }
}

// ── 查看技能内容 ──────────────────────────────────
async function viewContent(row: any) {
  content.value = row
  contentText.value = undefined
  contentDialog.value = true
  contentLoading.value = true
  try {
    const res: any = await hermes.getSkillContent(row.name)
    contentText.value = res?.content ?? JSON.stringify(res ?? {}, null, 2)
  } catch (e: any) {
    contentText.value = `读取失败: ${e.message || e}`
  } finally {
    contentLoading.value = false
  }
}

onMounted(loadSkills)
</script>

<style scoped>
.hermes-skills-page {
  padding: 4px 0;
}
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-bottom: none;
  border-radius: 8px 8px 0 0;
}
.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.count-tag {
  font-weight: 500;
}
.skill-table {
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 0 0 8px 8px;
  overflow: hidden;
}
.skill-name {
  font-weight: 600;
  font-size: 13px;
  color: var(--el-text-color-primary);
}
.skill-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.dialog-tip {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.content-body {
  min-height: 200px;
  max-height: 60vh;
  overflow: auto;
}
.skill-content {
  margin: 0;
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
  font-family: 'SF Mono', Menlo, Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>