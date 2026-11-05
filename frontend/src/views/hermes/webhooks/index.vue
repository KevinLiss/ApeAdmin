<template>
  <div class="hermes-webhooks-page">
    <!-- 未启用警告 -->
    <el-alert
      v-if="!enabled"
      type="warning"
      :closable="false"
      show-icon
      title="Webhook 接收器未启用"
    >
      <p>Webhooks 是独立的网关平台，需要在网关配置中显式启用。启用后可能触发网关重启。</p>
      <el-button
        size="small"
        type="primary"
        :loading="enabling"
        style="margin-top: 8px"
        @click="enable"
      >
        启用 Webhooks
      </el-button>
    </el-alert>

    <!-- 重启状态提示 -->
    <el-alert
      v-if="restarting"
      type="info"
      :closable="false"
      show-icon
      title="网关正在重启…"
    />
    <el-alert
      v-else-if="restartError"
      type="error"
      :closable="false"
      show-icon
      :title="restartError"
    >
      <el-button
        size="small"
        type="warning"
        plain
        style="margin-top: 8px"
        @click="restartGateway"
      >
        重启网关
      </el-button>
    </el-alert>

    <!-- 订阅列表 -->
    <el-card shadow="never">
      <template #header>
        <div class="section-header">
          <span>订阅列表（{{ subscriptions.length }}）</span>
          <el-button size="small" type="primary" :disabled="!enabled" @click="openCreate">
            新建订阅
          </el-button>
        </div>
      </template>

      <div v-if="!loading && !subscriptions.length" class="empty-tip">
        {{ enabled ? '暂无订阅。点击右上角"新建订阅"创建。' : '启用 Webhooks 后可创建订阅。' }}
      </div>

      <div v-for="sub in subscriptions" :key="sub.name" class="sub-row">
        <div class="sub-main">
          <div class="sub-title">
            <span class="sub-name">{{ sub.name }}</span>
            <el-tag v-if="sub.deliver" size="small" type="info" effect="plain">
              投递: {{ sub.deliver }}
            </el-tag>
            <el-tag v-if="sub.deliver_only" size="small" type="warning" effect="plain">
              仅投递
            </el-tag>
            <el-tag v-if="!sub.enabled" size="small" type="danger" effect="plain">
              已禁用
            </el-tag>
          </div>
          <div v-if="sub.description" class="sub-desc">{{ sub.description }}</div>
          <div class="sub-events">
            <el-tag
              v-for="ev in (sub.events?.length ? sub.events : ['(全部)'])"
              :key="ev"
              size="small"
              effect="plain"
            >
              {{ ev }}
            </el-tag>
          </div>
          <div class="sub-url" :class="{ disabled: !sub.enabled }">
            <code>{{ sub.url }}</code>
            <el-button size="small" text @click="copyText(sub.url, $event)">复制</el-button>
          </div>
        </div>
        <div class="sub-actions">
          <el-button
            size="small"
            :loading="toggling === sub.name"
            @click="toggle(sub)"
          >
            {{ sub.enabled ? '禁用' : '启用' }}
          </el-button>
          <el-button
            size="small"
            type="danger"
            text
            @click="confirmDelete(sub)"
          >
            删除
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 新建订阅对话框 -->
    <el-dialog
      v-model="createOpen"
      title="新建订阅"
      width="560px"
      :close-on-click-modal="false"
    >
      <!-- 一次性凭证态 -->
      <div v-if="created" class="created-box">
        <el-alert
          type="warning"
          :closable="false"
          show-icon
          title="Secret 仅此一次展示，请立即保存"
          style="margin-bottom: 12px"
        />
        <div class="cred-row">
          <span class="cred-label">Webhook URL</span>
          <code class="cred-value">{{ created.url }}</code>
          <el-button size="small" @click="copyText(created.url, $event)">复制</el-button>
        </div>
        <div class="cred-row">
          <span class="cred-label">Secret</span>
          <code class="cred-value">{{ created.secret }}</code>
          <el-button size="small" @click="copyText(created.secret, $event)">复制</el-button>
        </div>
        <el-button type="primary" style="margin-top: 12px" @click="closeCreate">
          我已保存
        </el-button>
      </div>

      <!-- 表单态 -->
      <el-form v-else label-width="110px" size="default">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="my-subscription" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" placeholder="可选" />
        </el-form-item>
        <el-form-item label="事件">
          <el-input
            v-model="form.events"
            placeholder="逗号分隔，留空订阅全部事件，如 message.new, session.ended"
          />
        </el-form-item>
        <el-form-item label="投递到">
          <el-select v-model="form.deliver" style="width: 100%">
            <el-option
              v-for="d in deliverOptions"
              :key="d.value"
              :label="d.label"
              :value="d.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="仅投递">
          <el-switch v-model="form.deliver_only" />
          <span class="form-hint">开启后跳过 agent 直接投递到目标渠道</span>
        </el-form-item>
        <el-form-item label="提示词">
          <el-input
            v-model="form.prompt"
            type="textarea"
            :rows="3"
            placeholder="可选，事件触发的 agent 提示词"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button v-if="!created" @click="createOpen = false">取消</el-button>
        <el-button v-if="!created" type="primary" :loading="creating" @click="create">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { hermes } from '@/api/hermes'

interface WebhookRoute {
  name: string
  description: string
  events: string[]
  deliver: string
  deliver_only: boolean
  prompt: string
  skills: string[]
  created_at: string | null
  url: string
  secret_set: boolean
  enabled: boolean
}

const data = ref<any>(null)
const loading = ref(false)
const enabling = ref(false)
const restarting = ref(false)
const restartError = ref('')
const toggling = ref<string | null>(null)
const creating = ref(false)
const createOpen = ref(false)
const created = ref<{ url: string; secret: string } | null>(null)

const form = reactive({
  name: '',
  description: '',
  events: '',
  deliver: 'log',
  deliver_only: false,
  prompt: '',
})

const deliverOptions = [
  { value: 'log', label: '日志（log）' },
  { value: 'telegram', label: 'Telegram' },
  { value: 'discord', label: 'Discord' },
  { value: 'slack', label: 'Slack' },
  { value: 'email', label: '邮件' },
  { value: 'github_comment', label: 'GitHub 评论' },
]

const enabled = computed(() => data.value?.enabled ?? false)
const subscriptions = computed<WebhookRoute[]>(() => data.value?.subscriptions ?? [])

let cancelled = false
let timers: ReturnType<typeof setTimeout>[] = []

function later(fn: () => void, ms: number) {
  const t = setTimeout(fn, ms)
  timers.push(t)
  return t
}

async function loadWebhooks() {
  loading.value = true
  try {
    data.value = await hermes.getWebhooks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '加载 Webhooks 失败')
  } finally {
    loading.value = false
  }
}

/** 网关重启结果轮询（官方 20×1.5s） */
async function watchRestartOutcome() {
  restarting.value = true
  restartError.value = ''
  for (let i = 0; i < 20; i++) {
    await new Promise<void>((r) => later(r, 1500))
    if (cancelled) return
    try {
      const res: any = await hermes.getActionStatus('gateway-restart', 5)
      if (res.running) continue
      if (res.exit_code != null && res.exit_code !== 0) {
        restartError.value = `网关重启失败（exit_code=${res.exit_code}）`
        ElMessage.error(restartError.value)
      }
      restarting.value = false
      later(loadWebhooks, 4000)
      return
    } catch {
      // 网关重启中 dashboard 可能短暂失联，继续轮询
      continue
    }
  }
  restarting.value = false
}

async function restartGateway() {
  restarting.value = true
  restartError.value = ''
  try {
    await hermes.restartGateway()
    later(watchRestartOutcome, 4000)
  } catch (e: any) {
    restarting.value = false
    restartError.value = e?.response?.data?.detail || e?.message || '重启网关失败'
  }
}

async function enable() {
  enabling.value = true
  try {
    const res: any = await hermes.enableWebhooks()
    ElMessage.success('Webhooks 已启用')
    if (res.restart_started === false) {
      restartError.value = res.restart_error || '需要重启网关以使 Webhooks 生效'
    } else if (res.needs_restart) {
      later(watchRestartOutcome, 4000)
    }
    await loadWebhooks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '启用失败')
  } finally {
    enabling.value = false
  }
}

async function toggle(sub: WebhookRoute) {
  toggling.value = sub.name
  try {
    await hermes.setWebhookEnabled(sub.name, !sub.enabled)
    ElMessage.success(sub.enabled ? '已禁用' : '已启用')
    await loadWebhooks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  } finally {
    toggling.value = null
  }
}

function confirmDelete(sub: WebhookRoute) {
  ElMessageBox.confirm(
    `确定删除订阅 "${sub.name}"？此操作不可恢复。`,
    '删除订阅',
    { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
  ).then(() => doDelete(sub)).catch(() => {})
}

async function doDelete(sub: WebhookRoute) {
  toggling.value = sub.name
  try {
    await hermes.deleteWebhook(sub.name)
    ElMessage.success('已删除')
    await loadWebhooks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '删除失败')
  } finally {
    toggling.value = null
  }
}

function openCreate() {
  form.name = ''
  form.description = ''
  form.events = ''
  form.deliver = 'log'
  form.deliver_only = false
  form.prompt = ''
  created.value = null
  createOpen.value = true
}

function closeCreate() {
  createOpen.value = false
  created.value = null
}

async function create() {
  const name = form.name.trim()
  if (!name) {
    ElMessage.warning('请填写订阅名称')
    return
  }
  creating.value = true
  try {
    const events = form.events
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    const res: any = await hermes.createWebhook({
      name,
      description: form.description.trim() || undefined,
      events: events.length ? events : undefined,
      deliver: form.deliver,
      deliver_only: form.deliver_only,
      prompt: form.prompt.trim() || undefined,
    })
    created.value = { url: res.url, secret: res.secret }
    await loadWebhooks()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '创建失败')
  } finally {
    creating.value = false
  }
}

async function copyText(text: string, ev?: Event) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制')
    if (ev?.target) (ev.target as HTMLElement).blur?.()
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

onMounted(loadWebhooks)
onUnmounted(() => {
  cancelled = true
  timers.forEach(clearTimeout)
  timers = []
})
</script>

<style scoped>
.hermes-webhooks-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
}

.sub-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 4px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.sub-row:last-child {
  border-bottom: none;
}

.sub-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sub-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.sub-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.sub-desc {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.sub-events {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.sub-url {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sub-url code {
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
  word-break: break-all;
}

.sub-url.disabled code {
  opacity: 0.6;
}

.sub-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: stretch;
}

.created-box {
  padding: 4px 0;
}

.cred-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}

.cred-label {
  width: 110px;
  flex-shrink: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.cred-value {
  flex: 1;
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
  font-size: 12px;
  word-break: break-all;
  padding: 6px 10px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.form-hint {
  margin-left: 10px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.empty-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  padding: 8px 0;
}
</style>
