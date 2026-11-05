<template>
  <div class="hermes-profile-builder">
    <div class="builder-header">
      <h2>新建 Profile</h2>
      <el-button text @click="cancel">取消</el-button>
    </div>

    <!-- 步进条 -->
    <div class="step-bar">
      <div
        v-for="(s, i) in steps"
        :key="s.key"
        class="step-pill"
        :class="{
          active: step === s.key,
          done: stepIndex > i,
          disabled: i > 0 && !nameValid,
        }"
        @click="goStep(i)"
      >
        {{ i + 1 }}. {{ s.label }}
      </div>
    </div>

    <!-- 步骤内容 -->
    <el-card shadow="never" class="step-card">
      <!-- 1. Identity -->
      <div v-if="step === 'identity'" class="step-body">
        <el-form label-width="100px">
          <el-form-item label="名称" required>
            <el-input v-model="name" placeholder="如 dev-assistant" />
            <div v-if="name && !nameValid" class="field-error">
              只允许小写字母、数字、下划线和连字符，且以字母/数字开头（最长 64 字符）
            </div>
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="description"
              type="textarea"
              :rows="2"
              placeholder="可选，描述这个 Profile 的用途"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 2. Model -->
      <div v-else-if="step === 'model'" class="step-body">
        <el-input
          v-model="modelFilter"
          placeholder="过滤模型…"
          clearable
          style="margin-bottom: 12px; max-width: 320px"
        />
        <div v-if="modelLoading" v-loading="true" class="list-loading" />
        <div v-else class="model-list">
          <div
            class="model-row"
            :class="{ selected: modelChoice === '' }"
            @click="modelChoice = ''"
          >
            使用默认（稍后设置）
          </div>
          <div
            v-for="m in filteredModels"
            :key="m.key"
            class="model-row"
            :class="{ selected: modelChoice === m.key }"
            @click="modelChoice = m.key"
          >
            {{ m.label }}
          </div>
          <div v-if="!filteredModels.length" class="empty-tip">无匹配模型</div>
        </div>
      </div>

      <!-- 3. Skills -->
      <div v-else-if="step === 'skills'" class="step-body">
        <el-checkbox v-model="keepAll" label="从完整默认技能包开始（推荐）" />
        <template v-if="!keepAll">
          <p class="section-hint">
            未勾选的技能将在新 Profile 中被禁用（REPLACE 语义）。
          </p>
          <el-input
            v-model="skillFilter"
            placeholder="过滤技能…"
            clearable
            style="margin: 12px 0; max-width: 320px"
          />
          <div v-if="skillsLoading" v-loading="true" class="list-loading" />
          <div v-else class="skill-list">
            <div v-for="s in filteredSkills" :key="s.name" class="skill-row">
              <el-checkbox
                :model-value="keptSkills.has(s.name)"
                @update:model-value="toggleKeep(s.name)"
              >
                <span class="skill-name">{{ s.name }}</span>
                <el-tag size="small" effect="plain" style="margin-left: 8px">
                  {{ s.category || 'general' }}
                </el-tag>
              </el-checkbox>
              <div class="skill-desc">{{ s.description }}</div>
            </div>
          </div>
        </template>

        <!-- Skills Hub -->
        <div class="hub-section">
          <h4>从技能 Hub 添加</h4>
          <div class="hub-search">
            <el-input
              v-model="hubQuery"
              placeholder="搜索技能 Hub…"
              style="max-width: 320px"
              @keyup.enter="searchHub"
            />
            <el-button :loading="hubSearching" @click="searchHub">搜索</el-button>
          </div>
          <div v-if="hubResults.length" class="hub-results">
            <div v-for="r in hubResults" :key="r.identifier" class="hub-row">
              <div class="hub-info">
                <span class="skill-name">{{ r.name }}</span>
                <el-tag size="small" effect="plain">{{ r.source }}</el-tag>
                <span class="skill-desc">{{ r.description }}</span>
              </div>
              <el-button
                size="small"
                :disabled="hubSkills.some((s) => s.identifier === r.identifier)"
                @click="addHubSkill(r)"
              >
                {{ hubSkills.some((s) => s.identifier === r.identifier) ? '已添加' : '添加' }}
              </el-button>
            </div>
          </div>
          <div v-if="hubSkills.length" class="hub-added">
            <el-tag
              v-for="s in hubSkills"
              :key="s.identifier"
              closable
              @close="removeHubSkill(s.identifier)"
            >
              {{ s.name }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 4. MCPs -->
      <div v-else-if="step === 'mcp'" class="step-body">
        <h4 class="mcp-title">已配置服务器（{{ mcpServers.length }}）</h4>
        <div v-for="(srv, i) in mcpServers" :key="srv.name" class="mcp-row">
          <div class="mcp-info">
            <span class="skill-name">{{ srv.name }}</span>
            <el-tag size="small" effect="plain">
              {{ srv.transport || 'http' }}
            </el-tag>
            <el-tag v-if="srv.auth && srv.auth !== 'none'" size="small" type="info" effect="plain">
              {{ srv.auth }}
            </el-tag>
            <code class="mono mcp-url">{{ srv.url || srv.command }}</code>
          </div>
          <el-button size="small" type="danger" text @click="mcpServers.splice(i, 1)">
            移除
          </el-button>
        </div>
        <div v-if="!mcpServers.length" class="empty-tip">尚未配置任何 MCP 服务器</div>

        <el-divider />
        <h4>添加服务器</h4>
        <el-form label-width="100px">
          <el-form-item label="名称" required>
            <el-input v-model="mcpDraft.name" placeholder="如 github" />
          </el-form-item>
          <el-form-item label="传输方式">
            <el-radio-group v-model="mcpDraft.transport" @change="onTransportChange">
              <el-radio-button value="http">HTTP / SSE</el-radio-button>
              <el-radio-button value="stdio">stdio</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <template v-if="mcpDraft.transport === 'http'">
            <el-form-item label="URL" required>
              <el-input v-model="mcpDraft.url" placeholder="https://example.com/mcp" />
            </el-form-item>
            <el-form-item label="认证">
              <el-radio-group v-model="mcpDraft.httpAuth">
                <el-radio-button value="none">无</el-radio-button>
                <el-radio-button value="header">Bearer token</el-radio-button>
                <el-radio-button value="oauth">OAuth</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item v-if="mcpDraft.httpAuth === 'header'" label="Token" required>
              <el-input
                v-model="mcpDraft.bearerToken"
                type="password"
                show-password
                autocomplete="new-password"
              />
              <span class="form-hint">Token 存入 profile 的 .env，config.yaml 仅存环境变量引用</span>
            </el-form-item>
            <el-alert
              v-if="mcpDraft.httpAuth === 'oauth'"
              type="info"
              :closable="false"
              show-icon
              title="创建 Profile 后请到 MCP 页面点击「认证」完成 OAuth 授权流程"
            />
          </template>
          <template v-else>
            <el-form-item label="命令" required>
              <el-input v-model="mcpDraft.command" placeholder="如 npx" />
            </el-form-item>
            <el-form-item label="参数">
              <el-input v-model="mcpDraft.args" placeholder="空格或逗号分隔" />
            </el-form-item>
            <el-form-item label="环境变量">
              <el-input
                v-model="mcpDraft.env"
                type="textarea"
                :rows="3"
                placeholder="每行一个 KEY=VALUE"
              />
            </el-form-item>
          </template>
        </el-form>
        <el-button type="primary" plain @click="addMcpDraft">添加到列表</el-button>
      </div>

      <!-- 5. Review -->
      <div v-else class="step-body">
        <div class="review-row">
          <span class="review-label">名称</span>
          <code>{{ name }}</code>
        </div>
        <div class="review-row">
          <span class="review-label">描述</span>
          <span>{{ description.trim() || '—' }}</span>
        </div>
        <div class="review-row">
          <span class="review-label">模型</span>
          <span>{{ pickedModel ? pickedModel.label : '默认（稍后设置）' }}</span>
        </div>
        <div class="review-row">
          <span class="review-label">技能</span>
          <span>
            {{ keepAll ? '完整默认技能包' : `${keptSkills.size} 个保留 + ${hubSkills.length} 个 Hub` }}
          </span>
        </div>
        <div v-if="hubSkills.length" class="review-row">
          <span class="review-label">Hub 技能</span>
          <span>{{ hubSkills.map((s) => s.name).join('、') }}</span>
        </div>
        <div class="review-row">
          <span class="review-label">MCP 服务器</span>
          <span>{{ mcpServers.length ? mcpServers.map((s) => s.name).join('、') : '无' }}</span>
        </div>
      </div>

      <!-- 底部导航 -->
      <div class="step-footer">
        <el-button :disabled="stepIndex === 0" @click="prev">上一步</el-button>
        <el-button
          v-if="step !== 'review'"
          type="primary"
          :disabled="!canAdvance"
          @click="next"
        >
          下一步
        </el-button>
        <el-button v-else type="primary" :loading="creating" :disabled="!nameValid" @click="submit">
          创建 Profile
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { hermes } from '@/api/hermes'

const router = useRouter()

const steps = [
  { key: 'identity', label: '基本信息' },
  { key: 'model', label: '模型' },
  { key: 'skills', label: '技能' },
  { key: 'mcp', label: 'MCP' },
  { key: 'review', label: '确认' },
] as const

const step = ref<string>('identity')
const stepIndex = computed(() => steps.findIndex((s) => s.key === step.value))

// ── identity ──
const name = ref('')
const description = ref('')
const NAME_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/
const nameValid = computed(() => NAME_RE.test(name.value))

// ── model ──
const modelChoices = ref<{ provider: string; model: string; label: string; key: string }[] | null>(null)
const modelLoading = ref(false)
const modelLoaded = ref(false)
const modelChoice = ref('')
const modelFilter = ref('')

const filteredModels = computed(() => {
  if (!modelChoices.value) return []
  const q = modelFilter.value.toLowerCase()
  return q ? modelChoices.value.filter((m) => m.label.toLowerCase().includes(q)) : modelChoices.value
})

const pickedModel = computed(() =>
  modelChoices.value?.find((m) => m.key === modelChoice.value)
)

async function loadModels() {
  if (modelLoaded.value || modelLoading.value) return
  modelLoading.value = true
  try {
    const res: any = await hermes.getModelOptions()
    const flat: { provider: string; model: string; label: string; key: string }[] = []
    for (const p of res.providers || []) {
      for (const m of p.models || []) {
        flat.push({
          provider: p.slug,
          model: m,
          label: `${p.name} · ${m}`,
          key: `${p.slug}\u0000${m}`,
        })
      }
    }
    modelChoices.value = flat
    modelLoaded.value = true
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '加载模型选项失败')
  } finally {
    modelLoading.value = false
  }
}

// ── skills ──
interface SkillInfo { name: string; description: string; category: string; enabled: boolean }
const skills = ref<SkillInfo[] | null>(null)
const skillsLoading = ref(false)
const skillsLoaded = ref(false)
const keepAll = ref(true)
const keptSkills = ref(new Set<string>())
const skillFilter = ref('')

const filteredSkills = computed(() => {
  if (!skills.value) return []
  const q = skillFilter.value.toLowerCase()
  if (!q) return skills.value
  return skills.value.filter(
    (s) =>
      s.name.toLowerCase().includes(q) ||
      (s.description || '').toLowerCase().includes(q) ||
      (s.category || '').toLowerCase().includes(q)
  )
})

function toggleKeep(n: string) {
  const s = new Set(keptSkills.value)
  if (s.has(n)) s.delete(n)
  else s.add(n)
  keptSkills.value = s
}

async function loadSkills() {
  if (skillsLoaded.value || skillsLoading.value) return
  skillsLoading.value = true
  try {
    const res: any = await hermes.getSkills()
    const list: SkillInfo[] = (res.skills || res || []).map?.((s: any) => s) || []
    skills.value = list
    keptSkills.value = new Set(list.filter((s) => s.enabled).map((s) => s.name))
    skillsLoaded.value = true
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '加载技能失败')
  } finally {
    skillsLoading.value = false
  }
}

// ── hub ──
interface HubSkill { identifier: string; name: string }
const hubQuery = ref('')
const hubResults = ref<any[]>([])
const hubSearching = ref(false)
const hubSkills = ref<HubSkill[]>([])

async function searchHub() {
  if (!hubQuery.value.trim()) return
  hubSearching.value = true
  try {
    const res: any = await hermes.searchSkillsHub(hubQuery.value.trim(), 'all', 20)
    hubResults.value = res.results || []
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '搜索失败')
  } finally {
    hubSearching.value = false
  }
}

function addHubSkill(r: any) {
  if (hubSkills.value.some((s) => s.identifier === r.identifier)) return
  hubSkills.value.push({ identifier: r.identifier, name: r.name })
}

function removeHubSkill(identifier: string) {
  hubSkills.value = hubSkills.value.filter((s) => s.identifier !== identifier)
}

// ── mcp ──
interface McpServerDraft {
  name: string
  transport: 'http' | 'stdio'
  url: string
  httpAuth: 'none' | 'header' | 'oauth'
  bearerToken: string
  command: string
  args: string
  env: string
}

function emptyDraft(): McpServerDraft {
  return {
    name: '',
    transport: 'http',
    url: '',
    httpAuth: 'none',
    bearerToken: '',
    command: '',
    args: '',
    env: '',
  }
}

const mcpDraft = ref<McpServerDraft>(emptyDraft())
const mcpServers = ref<any[]>([])

function onTransportChange() {
  const d = mcpDraft.value
  if (d.transport === 'http') {
    d.command = ''
    d.args = ''
    d.env = ''
  } else {
    d.url = ''
    d.bearerToken = ''
    d.httpAuth = 'none'
  }
}

/** 官方 lib/mcp-server-create.ts buildMcpServerCreate 移植 */
function buildMcpServerCreate(d: McpServerDraft) {
  if (!d.name.trim()) throw new Error('服务器名称必填')
  if (d.transport === 'http') {
    if (!d.url.trim()) throw new Error('URL 必填')
    const out: any = { name: d.name.trim(), url: d.url.trim() }
    if (d.httpAuth !== 'none') out.auth = d.httpAuth
    if (d.httpAuth === 'header') {
      if (!d.bearerToken.trim()) throw new Error('Bearer token 必填')
      out.bearer_token = d.bearerToken.trim()
    }
    return out
  }
  if (!d.command.trim()) throw new Error('命令必填')
  const out: any = { name: d.name.trim(), command: d.command.trim() }
  const args = d.args.split(/[\s,]+/).filter(Boolean)
  if (args.length) out.args = args
  const env: Record<string, string> = {}
  for (const line of d.env.split('\n')) {
    const idx = line.indexOf('=')
    if (idx > 0) env[line.slice(0, idx).trim()] = line.slice(idx + 1).trim()
  }
  if (Object.keys(env).length) out.env = env
  return out
}

function addMcpDraft() {
  try {
    const built = buildMcpServerCreate(mcpDraft.value)
    // 同名覆盖
    const i = mcpServers.value.findIndex((s) => s.name === built.name)
    if (i >= 0) mcpServers.value.splice(i, 1, built)
    else mcpServers.value.push(built)
    mcpDraft.value = emptyDraft()
    ElMessage.success(`已添加服务器 ${built.name}`)
  } catch (e: any) {
    ElMessage.warning(e.message || '服务器配置不完整')
  }
}

// ── 步进 ──
const canAdvance = computed(() => step.value !== 'identity' || nameValid.value)

watch(step, (s) => {
  if (s === 'model') loadModels()
  if (s === 'skills') loadSkills()
})

function goStep(i: number) {
  if (i > 0 && !nameValid.value) return
  step.value = steps[i].key
}

function next() {
  const i = stepIndex.value
  if (i < steps.length - 1) step.value = steps[i + 1].key
}

function prev() {
  const i = stepIndex.value
  if (i > 0) step.value = steps[i - 1].key
}

function cancel() {
  router.push('/hermes/profiles')
}

// ── 提交 ──
const creating = ref(false)

async function submit() {
  if (!nameValid.value) {
    ElMessage.warning('Profile 名称不合法')
    step.value = 'identity'
    return
  }
  creating.value = true
  try {
    const res: any = await hermes.createProfile({
      name: name.value.trim(),
      clone_from: null,
      description: description.value.trim() || undefined,
      provider: pickedModel.value?.provider,
      model: pickedModel.value?.model,
      mcp_servers: mcpServers.value.length ? mcpServers.value : undefined,
      keep_skills: keepAll.value ? undefined : Array.from(keptSkills.value),
      hub_skills: hubSkills.value.length ? hubSkills.value.map((s) => s.identifier) : undefined,
    })
    const installing = (res.hub_installs || []).filter((h: any) => h.pid != null).length
    ElMessage.success(
      installing > 0
        ? `Profile 已创建，${installing} 个 Hub 技能正在安装`
        : 'Profile 已创建'
    )
    router.push('/hermes/profiles')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '创建 Profile 失败')
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.hermes-profile-builder {
  max-width: 780px;
  margin: 0 auto;
}

.builder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.builder-header h2 {
  margin: 0;
  font-size: 18px;
}

.step-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.step-pill {
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid var(--el-border-color);
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-blank);
}

.step-pill.active {
  color: #fff;
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

.step-pill.done {
  color: var(--el-color-primary);
  border-color: var(--el-color-primary-light-5);
}

.step-pill.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.step-card {
  min-height: 320px;
}

.step-body {
  min-height: 240px;
}

.step-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.field-error {
  color: var(--el-color-danger);
  font-size: 12px;
  margin-top: 4px;
}

.list-loading {
  height: 120px;
}

.model-list,
.skill-list {
  max-height: 320px;
  overflow: auto;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  padding: 8px;
}

.model-row {
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.model-row:hover {
  background: var(--el-fill-color-light);
}

.model-row.selected {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  font-weight: 600;
}

.skill-row {
  padding: 8px 12px;
}

.skill-name {
  font-weight: 500;
}

.skill-desc {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 2px;
  padding-left: 24px;
}

.section-hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.hub-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed var(--el-border-color);
}

.hub-section h4 {
  margin: 0 0 10px;
}

.hub-search {
  display: flex;
  gap: 8px;
}

.hub-results {
  margin-top: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  padding: 8px;
}

.hub-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 6px;
}

.hub-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.hub-added {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mcp-title {
  margin: 0 0 8px;
}

.mcp-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 4px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.mcp-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.mcp-url {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  word-break: break-all;
}

.mono {
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
}

.form-hint {
  display: block;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 4px;
}

.review-row {
  display: flex;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px dashed var(--el-border-color-lighter);
  font-size: 13px;
}

.review-label {
  width: 100px;
  flex-shrink: 0;
  color: var(--el-text-color-secondary);
}

.empty-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  padding: 8px 0;
}
</style>
