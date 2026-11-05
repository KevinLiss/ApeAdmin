<template>
  <div class="hermes-channels-page">
    <!-- 网关未运行提示 -->
    <el-alert
      v-if="gatewayDown"
      type="info"
      :closable="false"
      show-icon
      title="网关未运行"
    >
      <p class="mono small">{{ gatewayStartCommand || 'hermes gateway start' }}</p>
      <el-button size="small" type="primary" plain style="margin-top: 8px" @click="restart">
        重启网关
      </el-button>
    </el-alert>

    <!-- 需要重启横幅 -->
    <el-alert
      v-if="restartNeeded"
      type="warning"
      :closable="false"
      show-icon
      title="配置已保存，需要重启网关生效"
    >
      <el-button size="small" type="warning" plain style="margin-top: 8px" @click="restart">
        重启网关
      </el-button>
    </el-alert>

    <!-- 统计 -->
    <div class="stat-line">
      {{ configuredCount }} / {{ platforms.length }} 个渠道已配置
      <el-button size="small" text :loading="loading" @click="load">刷新</el-button>
    </div>

    <!-- 平台卡片列表 -->
    <el-card v-for="p in platforms" :key="p.id" shadow="never" class="platform-card">
      <div class="platform-head">
        <div class="platform-title">
          <span class="platform-name">{{ p.name }}</span>
          <el-tag size="small" :type="stateTagType(p.state)" effect="plain">
            {{ stateLabel(p.state) }}
          </el-tag>
        </div>
        <div class="platform-ops">
          <el-switch
            :model-value="p.enabled"
            :loading="toggling === p.id"
            @change="togglePlatform(p, $event as boolean)"
          />
          <el-button size="small" :loading="testing === p.id" @click="test(p)">
            测试
          </el-button>
          <el-button v-if="p.id !== 'telegram'" size="small" @click="openConfig(p)">
            配置
          </el-button>
          <el-button v-if="p.id === 'telegram' || p.id === 'whatsapp'" size="small" type="primary" plain @click="startWizard(p)">
            QR 配对
          </el-button>
        </div>
      </div>

      <div v-if="p.description" class="platform-desc">{{ p.description }}</div>
      <div v-if="p.error_message" class="platform-error">{{ p.error_message }}</div>
      <div v-if="p.ingress_url" class="platform-url mono">{{ p.ingress_url }}</div>

      <!-- Telegram 向导 -->
      <div v-if="p.id === 'telegram' && wizard.platform === 'telegram'" class="wizard-box">
        <el-divider />
        <h4>Telegram QR 配对</h4>
        <template v-if="wizard.phase === 'idle'">
          <el-form inline>
            <el-form-item label="机器人名称">
              <el-input v-model="tgBotName" placeholder="可选" style="width: 200px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="wizard.busy" @click="startTelegram">
                开始配对
              </el-button>
            </el-form-item>
          </el-form>
        </template>

        <template v-else-if="wizard.phase === 'waiting' || wizard.phase === 'ready'">
          <div class="qr-area">
            <img v-if="wizard.qrDataUrl" :src="wizard.qrDataUrl" class="qr-img" alt="QR" />
            <div class="qr-side">
              <p v-if="wizard.expiresAt" class="expiry">
                二维码有效期剩余: {{ formatExpiry(wizard.expiresAt) }}
              </p>
              <p class="small">
                用 Telegram 扫描二维码（或打开深链）向机器人发送任意消息。
              </p>
              <p v-if="wizard.phase === 'ready'" class="ready-tip">
                已捕获 owner_user_id: <code>{{ wizard.ownerUserId }}</code>
              </p>
              <!-- 允许用户列表 -->
              <div class="allowed-box">
                <span class="small">允许的用户 ID：</span>
                <el-tag
                  v-for="id in wizard.allowedIds"
                  :key="id"
                  closable
                  size="small"
                  @close="removeAllowed(id)"
                >
                  {{ id }}
                </el-tag>
                <el-input
                  v-model="wizard.newAllowedId"
                  size="small"
                  style="width: 140px"
                  placeholder="输入用户 ID"
                  @keyup.enter="addAllowed"
                />
                <el-button size="small" @click="addAllowed">添加</el-button>
              </div>
              <el-button
                type="primary"
                :loading="wizard.busy"
                style="margin-top: 12px"
                @click="applyTelegram"
              >
                保存并重启
              </el-button>
              <el-button size="small" text @click="cancelWizard">取消</el-button>
            </div>
          </div>
        </template>
      </div>

      <!-- WhatsApp 向导 -->
      <div v-if="p.id === 'whatsapp' && wizard.platform === 'whatsapp'" class="wizard-box">
        <el-divider />
        <h4>WhatsApp QR 配对</h4>
        <template v-if="wizard.phase === 'idle'">
          <el-form inline>
            <el-form-item label="模式">
              <el-radio-group v-model="waMode">
                <el-radio-button value="bot">机器人模式</el-radio-button>
                <el-radio-button value="self-chat">自聊模式</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="wizard.busy" @click="startWhatsApp">
                开始配对
              </el-button>
            </el-form-item>
          </el-form>
        </template>

        <template v-else-if="wizard.phase === 'waiting' || wizard.phase === 'connected'">
          <div class="qr-area">
            <img v-if="wizard.qrDataUrl" :src="wizard.qrDataUrl" class="qr-img" alt="QR" />
            <div class="qr-side">
              <p v-if="wizard.expiresAt" class="expiry">
                二维码有效期剩余: {{ formatExpiry(wizard.expiresAt) }}
              </p>
              <p class="small">用 WhatsApp 扫描二维码完成登录。</p>
              <p v-if="wizard.phase === 'connected'" class="ready-tip">
                已连接账号: <code>{{ wizard.waAccountName || wizard.waAccountPhone }}</code>
                <a
                  v-if="wizard.waAccountPhone"
                  :href="`https://wa.me/${wizard.waAccountPhone}`"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  wa.me
                </a>
              </p>
              <el-button
                type="primary"
                :loading="wizard.busy"
                style="margin-top: 12px"
                @click="applyWhatsApp"
              >
                保存并重启
              </el-button>
              <el-button size="small" text @click="cancelWizard">取消</el-button>
            </div>
          </div>
        </template>
      </div>
    </el-card>

    <!-- 配置对话框 -->
    <el-dialog v-model="configOpen" :title="`配置 ${configPlatform?.name || ''}`" width="520px">
      <div v-if="configPlatform?.id === 'telegram'" class="tg-guide">
        <ol class="small">
          <li>在 Telegram 中找 <b>@BotFather</b> 发送 <code>/newbot</code></li>
          <li>按提示创建机器人，拿到 token</li>
          <li>将 token 填入下方 TELEGRAM_BOT_TOKEN</li>
        </ol>
      </div>

      <el-form label-width="220px">
        <el-form-item
          v-for="v in configVars"
          :key="v.key"
          :label="v.key"
          :required="v.required"
        >
          <el-input
            v-if="v.is_password"
            v-model="configValues[v.key]"
            type="password"
            show-password
            autocomplete="new-password"
            :placeholder="v.is_set ? '已设置，留空保留原值' : (v.prompt || '')"
          />
          <el-input
            v-else
            v-model="configValues[v.key]"
            :placeholder="v.is_set ? (v.redacted_value || '已设置') : (v.prompt || '')"
          />
          <div v-if="v.help" class="form-hint">{{ v.help }}</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="configOpen = false">取消</el-button>
        <el-button type="primary" :loading="savingConfig" @click="saveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { hermes } from '@/api/hermes'

interface EnvVar {
  key: string
  required: boolean
  is_set: boolean
  redacted_value?: string
  description?: string
  prompt?: string
  help?: string
  is_password?: boolean
  advanced?: boolean
}

interface Platform {
  id: string
  name: string
  description?: string
  enabled: boolean
  configured: boolean
  state: string
  error_message?: string
  ingress_url?: string
  env_vars?: EnvVar[]
  whatsapp_setup?: { mode: string; allowed_users_set: boolean }
}

const TELEGRAM_BOT_TOKEN_RE = /^\d+:[A-Za-z0-9_-]{30,}$/

const data = ref<any>(null)
const platforms = ref<Platform[]>([])
const loading = ref(false)
const toggling = ref<string | null>(null)
const testing = ref<string | null>(null)
const restartNeeded = ref(false)
const gatewayDown = ref(false)

const configOpen = ref(false)
const configPlatform = ref<Platform | null>(null)
const configVars = ref<EnvVar[]>([])
const configValues = ref<Record<string, string>>({})
const savingConfig = ref(false)

const tgBotName = ref('')
const waMode = ref<'bot' | 'self-chat'>('bot')

const wizard = reactive({
  platform: '' as '' | 'telegram' | 'whatsapp',
  phase: 'idle' as 'idle' | 'starting' | 'waiting' | 'ready' | 'connected' | 'applying',
  busy: false,
  pairingId: '',
  qrDataUrl: '',
  expiresAt: 0,
  ownerUserId: '',
  allowedIds: [] as string[],
  newAllowedId: '',
  waAccountName: '',
  waAccountPhone: '',
  error: '',
})

let pollTimer: ReturnType<typeof setTimeout> | null = null
let tickTimer: ReturnType<typeof setInterval> | null = null
let cancelled = false

const configuredCount = computed(() => platforms.value.filter((p) => p.configured).length)
const gatewayStartCommand = computed(() => data.value?.gateway_start_command || '')

const stateLabelMap: Record<string, string> = {
  connected: '已连接',
  pending_restart: '待重启',
  disabled: '已禁用',
  disconnected: '未连接',
  fatal: '故障',
  waiting_for_qr: '等待扫码',
  unconfigured: '未配置',
}
const stateLabel = (s: string) => stateLabelMap[s] || s
const stateTagType = (s: string) => {
  const map: Record<string, string> = {
    connected: 'success',
    disabled: 'info',
    fatal: 'danger',
    pending_restart: 'warning',
  }
  return (map[s] || 'info') as any
}

async function load() {
  loading.value = true
  try {
    const res: any = await hermes.getMessagingPlatforms()
    data.value = res
    platforms.value = res.platforms || []
    const status: any = await hermes.getStatus()
    gatewayDown.value = !status.gateway_running
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '加载渠道失败')
  } finally {
    loading.value = false
  }
}

async function togglePlatform(p: Platform, enabled: boolean) {
  toggling.value = p.id
  // 乐观更新
  p.enabled = enabled
  p.state = enabled ? 'pending_restart' : 'disabled'
  try {
    const res: any = await hermes.updateMessagingPlatform(p.id, { enabled })
    if (res.hot_served) {
      setTimeout(() => { if (!cancelled) load() }, 4000)
    } else {
      restartNeeded.value = true
    }
  } catch (e: any) {
    await load()
    ElMessage.error(e?.response?.data?.detail || e?.message || '操作失败')
  } finally {
    toggling.value = null
  }
}

async function test(p: Platform) {
  testing.value = p.id
  try {
    const res: any = await hermes.testMessagingPlatform(p.id)
    if (res.ok) ElMessage.success(`测试通过（${stateLabel(res.state || p.state)}）`)
    else ElMessage.warning(`测试失败：${res.message || res.state || '未知错误'}`)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '测试失败')
  } finally {
    testing.value = null
  }
}

function openConfig(p: Platform) {
  configPlatform.value = p
  configVars.value = (p.env_vars || []).filter((v) => !v.advanced)
  configValues.value = {}
  for (const v of configVars.value) configValues.value[v.key] = ''
  configOpen.value = true
}

async function saveConfig() {
  if (!configPlatform.value) return
  // 校验必填 + 格式
  const env: Record<string, string> = {}
  for (const v of configVars.value) {
    const val = (configValues.value[v.key] || '').trim()
    if (!val) {
      if (v.required && !v.is_set) {
        ElMessage.warning(`请填写 ${v.key}`)
        return
      }
      continue // 留空保留
    }
    if (v.key === 'TELEGRAM_BOT_TOKEN' && !TELEGRAM_BOT_TOKEN_RE.test(val)) {
      ElMessage.warning('Telegram token 格式不正确（形如 123456:ABC-...）')
      return
    }
    env[v.key] = val
  }
  savingConfig.value = true
  try {
    const res: any = await hermes.updateMessagingPlatform(configPlatform.value.id, {
      env,
      enabled: true,
    })
    configOpen.value = false
    ElMessage.success('配置已保存')
    if (res.hot_served) {
      setTimeout(() => { if (!cancelled) load() }, 4000)
    } else {
      restartNeeded.value = true
    }
    await load()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '保存失败')
  } finally {
    savingConfig.value = false
  }
}

async function restart() {
  restartNeeded.value = false
  try {
    await hermes.restartGateway()
    ElMessage.success('网关重启中…')
    setTimeout(() => { if (!cancelled) load() }, 4000)
    // 兜底轮询 action 状态
    for (let i = 0; i < 20; i++) {
      await sleep(1500)
      if (cancelled) return
      try {
        const res: any = await hermes.getActionStatus('gateway-restart', 5)
        if (!res.running) {
          if (res.exit_code != null && res.exit_code !== 0) {
            ElMessage.error(`网关重启失败（exit_code=${res.exit_code}）`)
          }
          break
        }
      } catch { continue }
    }
    await load()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '重启失败')
  }
}

// ── QR 向导 ──────────────────────────────────────

async function makeQr(payload: string) {
  try {
    const mod: any = await import('qrcode')
    wizard.qrDataUrl = await mod.toDataURL(payload, {
      errorCorrectionLevel: 'M',
      margin: 2,
      width: 240,
    })
  } catch {
    wizard.qrDataUrl = ''
  }
}

function startWizard(p: Platform) {
  wizard.platform = p.id as 'telegram' | 'whatsapp'
  wizard.phase = 'idle'
  wizard.busy = false
  wizard.qrDataUrl = ''
  wizard.allowedIds = []
  wizard.ownerUserId = ''
}

async function startTelegram() {
  wizard.busy = true
  wizard.phase = 'starting'
  try {
    const res: any = await hermes.startTelegramOnboarding(
      tgBotName.value.trim() ? { bot_name: tgBotName.value.trim() } : {}
    )
    wizard.pairingId = res.pairing_id
    wizard.expiresAt = Date.now() + (res.expires_at ? res.expires_at * 1000 : 0) || Date.now() + 300000
    if (res.qr_payload) await makeQr(res.qr_payload)
    wizard.phase = 'waiting'
    pollTelegram()
  } catch (e: any) {
    wizard.phase = 'idle'
    ElMessage.error(e?.response?.data?.detail || e?.message || '启动配对失败')
  } finally {
    wizard.busy = false
  }
}

async function pollTelegram() {
  if (cancelled || !wizard.pairingId) return
  pollTimer = setTimeout(async () => {
    try {
      const res: any = await hermes.getTelegramOnboardingStatus(wizard.pairingId)
      if (res.status === 'ready' || res.owner_user_id) {
        wizard.phase = 'ready'
        if (res.owner_user_id && !wizard.allowedIds.includes(String(res.owner_user_id))) {
          wizard.allowedIds.push(String(res.owner_user_id))
          wizard.ownerUserId = String(res.owner_user_id)
        }
        if (res.qr_payload) await makeQr(res.qr_payload)
        return // ready 后停止轮询
      }
      if (res.qr_payload && res.qr_payload !== wizard.qrDataUrl) {
        // payload 无从比对，简单刷新
      }
    } catch (e: any) {
      if (isTerminalError(e)) {
        wizard.phase = 'idle'
        ElMessage.error('配对已过期，请重新开始')
        return
      }
    }
    pollTelegram()
  }, 2000)
}

async function applyTelegram() {
  if (!wizard.allowedIds.length) {
    ElMessage.warning('至少需要一个允许的用户 ID')
    return
  }
  wizard.busy = true
  wizard.phase = 'applying'
  try {
    await hermes.applyTelegramOnboarding(wizard.pairingId, {
      allowed_user_ids: wizard.allowedIds,
    })
    ElMessage.success('配置已保存，网关重启中…')
    cancelWizard()
    setTimeout(() => { if (!cancelled) load() }, 4000)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '保存失败')
    wizard.phase = 'ready'
  } finally {
    wizard.busy = false
  }
}

async function startWhatsApp() {
  wizard.busy = true
  wizard.phase = 'starting'
  try {
    const res: any = await hermes.startWhatsAppOnboarding({ mode: waMode.value })
    wizard.pairingId = res.pairing_id
    wizard.expiresAt = Date.now() + 300000
    if (res.qr_payload) await makeQr(res.qr_payload)
    wizard.phase = 'waiting'
    pollWhatsApp()
  } catch (e: any) {
    wizard.phase = 'idle'
    ElMessage.error(e?.response?.data?.detail || e?.message || '启动配对失败')
  } finally {
    wizard.busy = false
  }
}

async function pollWhatsApp() {
  if (cancelled || !wizard.pairingId) return
  pollTimer = setTimeout(async () => {
    try {
      const res: any = await hermes.getWhatsAppOnboardingStatus(wizard.pairingId)
      if (res.qr_payload) await makeQr(res.qr_payload)
      if (res.status === 'connected') {
        wizard.phase = 'connected'
        wizard.waAccountName = res.account_name || ''
        wizard.waAccountPhone = res.account_phone || res.account_id || ''
        return
      }
      if (res.status === 'error') {
        wizard.phase = 'idle'
        ElMessage.error(res.error || '配对失败')
        return
      }
    } catch (e: any) {
      if (isTerminalError(e)) {
        wizard.phase = 'idle'
        ElMessage.error('配对已过期，请重新开始')
        return
      }
    }
    pollWhatsApp()
  }, 1500)
}

async function applyWhatsApp() {
  wizard.busy = true
  wizard.phase = 'applying'
  try {
    await hermes.applyWhatsAppOnboarding(wizard.pairingId, { mode: waMode.value })
    ElMessage.success('配置已保存，网关重启中…')
    cancelWizard()
    setTimeout(() => { if (!cancelled) load() }, 4000)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '保存失败')
    wizard.phase = 'connected'
  } finally {
    wizard.busy = false
  }
}

function addAllowed() {
  const id = wizard.newAllowedId.trim()
  if (!/^\d+$/.test(id)) {
    ElMessage.warning('用户 ID 必须为数字')
    return
  }
  if (!wizard.allowedIds.includes(id)) wizard.allowedIds.push(id)
  wizard.newAllowedId = ''
}

function removeAllowed(id: string) {
  wizard.allowedIds = wizard.allowedIds.filter((i) => i !== id)
}

function cancelWizard() {
  if (wizard.pairingId) {
    if (wizard.platform === 'telegram') hermes.cancelTelegramOnboarding(wizard.pairingId).catch(() => {})
    else if (wizard.platform === 'whatsapp') hermes.cancelWhatsAppOnboarding(wizard.pairingId).catch(() => {})
  }
  if (pollTimer) clearTimeout(pollTimer)
  wizard.platform = ''
  wizard.phase = 'idle'
  wizard.pairingId = ''
  wizard.qrDataUrl = ''
}

function isTerminalError(e: any): boolean {
  const msg = String(e?.response?.status || e?.message || '')
  return msg.includes('410') || msg.includes('Gone') || msg.includes('expired')
}

function formatExpiry(ts: number): string {
  const secs = Math.max(0, Math.floor((ts - Date.now()) / 1000))
  return `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, '0')}`
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))

onMounted(() => {
  load()
  // 过期倒计时每秒刷新
  tickTimer = setInterval(() => {}, 1000)
})

onUnmounted(() => {
  cancelled = true
  if (pollTimer) clearTimeout(pollTimer)
  if (tickTimer) clearInterval(tickTimer)
})
</script>

<style scoped>
.hermes-channels-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-line {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.platform-card {
  margin-bottom: 0;
}

.platform-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.platform-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.platform-name {
  font-weight: 600;
  font-size: 15px;
}

.platform-ops {
  display: flex;
  align-items: center;
  gap: 10px;
}

.platform-desc {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-top: 8px;
}

.platform-error {
  color: var(--el-color-danger);
  font-size: 13px;
  margin-top: 6px;
}

.platform-url {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 6px;
  word-break: break-all;
}

.wizard-box h4 {
  margin: 0 0 12px;
}

.qr-area {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.qr-img {
  width: 240px;
  height: 240px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
}

.qr-side {
  flex: 1;
  min-width: 240px;
}

.expiry {
  color: var(--el-color-warning);
  font-size: 13px;
  font-weight: 500;
}

.ready-tip code {
  padding: 2px 6px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.allowed-box {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.tg-guide {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
}

.tg-guide ol {
  margin: 0;
  padding-left: 20px;
}

.form-hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 2px;
}

.small {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.mono {
  font-family: ui-monospace, 'SF Mono', Consolas, monospace;
}
</style>
