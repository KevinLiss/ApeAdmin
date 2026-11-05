<template>
  <div class="hermes-system-page">
    <!-- 顶部：标题 + 刷新 -->
    <div class="page-header">
      <div class="header-left">
        <h3 class="page-title">系统管理</h3>
        <span class="page-subtitle">hermes 引擎状态、网关、更新与资源统计</span>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" :loading="loading" @click="loadAll">刷新</el-button>
      </div>
    </div>

    <!-- 两列布局 -->
    <el-row :gutter="16">
      <!-- 左列：系统状态 + 版本信息 + 更新 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never" class="sys-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-tag
                v-if="canUpdate"
                type="warning"
                size="small"
                effect="light"
                class="update-tag"
              >
                有新版本可用
              </el-tag>
            </div>
          </template>
          <el-descriptions :column="1" border size="small" class="sys-desc">
            <el-descriptions-item label="Hermes 版本">
              <span class="version-text">{{ version || '--' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="Config 版本">
              {{ configVersion || '--' }}
            </el-descriptions-item>
            <el-descriptions-item label="最新版本">
              <span v-if="latestVersion">{{ latestVersion }}</span>
              <span v-else>--</span>
            </el-descriptions-item>
            <el-descriptions-item label="是否可更新">
              <el-tag :type="canUpdate ? 'warning' : 'success'" size="small">
                {{ canUpdate ? '可更新' : '已是最新' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
          <div class="update-actions">
            <el-button
              :icon="Refresh"
              size="small"
              :loading="checkingUpdate"
              @click="checkUpdate"
            >
              检测更新
            </el-button>
            <el-button
              type="primary"
              :icon="Upload"
              size="small"
              :disabled="!canUpdate"
              :loading="updating"
              @click="confirmUpdate"
            >
              执行更新
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右列：网关状态 + 操作 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="never" class="sys-card">
          <template #header>
            <div class="card-header">
              <span>网关状态</span>
              <el-tag :type="gatewayRunning ? 'success' : 'danger'" size="small">
                <span class="dot" :class="{ online: gatewayRunning }"></span>
                {{ gatewayRunning ? '运行中' : '已停止' }}
              </el-tag>
            </div>
          </template>
          <el-descriptions :column="1" border size="small" class="sys-desc">
        <el-descriptions-item label="运行状态">
          <el-tag :type="gatewayRunning ? 'success' : 'info'" size="small">
            {{ gatewayRunning ? '运行中' : '未运行' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="平台">
          <template v-if="gatewayPlatforms.length">
            <el-tag
              v-for="p in gatewayPlatforms"
              :key="p"
              size="small"
              effect="plain"
              class="platform-tag"
            >
              {{ p }}
            </el-tag>
          </template>
          <span v-else>--</span>
        </el-descriptions-item>
        <el-descriptions-item label="最近心跳">
          {{ lastHeartbeat || '--' }}
        </el-descriptions-item>
      </el-descriptions>

          <div class="gateway-stats">
            <el-statistic title="接入平台" :value="gatewayPlatforms.length" />
            <el-statistic :title="'运行状态'" :value="gatewayRunning ? 1 : 0">
              <template #default>
                <span class="stat-value" :class="{ online: gatewayRunning }">
                  {{ gatewayRunning ? '运行中' : '已停止' }}
                </span>
              </template>
            </el-statistic>
          </div>

          <div class="gateway-actions">
            <el-button
              type="success"
              :icon="Switch"
              size="small"
              :disabled="gatewayRunning || gatewayOpsBusy"
              @click="confirmGateway('start')"
            >
              启动
            </el-button>
            <el-button
              type="danger"
              :icon="Switch"
              size="small"
              :disabled="!gatewayRunning || gatewayOpsBusy"
              @click="confirmGateway('stop')"
            >
              停止
            </el-button>
            <el-button
              type="warning"
              :icon="Refresh"
              size="small"
              :loading="gatewayOpsBusy"
              @click="confirmGateway('restart')"
            >
              重启
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统统计 -->
    <el-card shadow="never" class="sys-card stats-card">
      <template #header>
        <div class="card-header">
          <span>系统统计</span>
          <span class="card-sub">CPU / 内存 / 磁盘使用情况</span>
        </div>
      </template>
      <el-row :gutter="24" class="stats-row">
        <el-col :xs="24" :sm="8">
          <div class="stat-item">
            <div class="stat-label">CPU 使用率</div>
            <el-progress
              :percentage="cpuPercent"
              :color="usageColor(cpuPercent)"
              :stroke-width="10"
              class="stat-progress"
            />
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="stat-item">
            <div class="stat-label">内存使用率</div>
            <el-progress
              :percentage="memoryPercent"
              :color="usageColor(memoryPercent)"
              :stroke-width="10"
              class="stat-progress"
            />
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="stat-item">
            <div class="stat-label">磁盘使用率</div>
            <el-progress
              :percentage="diskPercent"
              :color="usageColor(diskPercent)"
              :stroke-width="10"
              class="stat-progress"
            />
          </div>
        </el-col>
      </el-row>

      <!-- Ops 状态 -->
      <el-divider content-position="left">系统操作（Ops）</el-divider>
      <el-descriptions :column="2" border size="small" class="sys-desc ops-desc">
        <el-descriptions-item
          v-for="(item, idx) in opsEntries"
          :key="idx"
          :label="item.key"
        >
          <span :class="{ 'ops-value-on': String(item.val) === 'true' }">
            {{ String(item.val) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Ops 状态" v-if="!opsEntries.length">
          {{ opsEmptyText }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 运维增强：备份 / Hooks / 凭据池 -->
    <el-row :gutter="16" class="ops-row">
      <!-- 备份 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="sys-card">
          <template #header>
            <div class="card-header">
              <span>备份</span>
            </div>
          </template>
          <el-descriptions :column="1" border size="small" class="sys-desc">
            <el-descriptions-item label="最近备份">
              {{ lastBackupTime || '--' }}
            </el-descriptions-item>
          </el-descriptions>
          <div class="ops-actions">
            <el-button type="primary" :icon="Download" size="small" :loading="backingUp" @click="handleBackup">
              立即备份
            </el-button>
            <el-button :icon="Download" size="small" :disabled="!lastBackupArchive" @click="downloadBackup">
              下载备份
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- Hooks -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="sys-card">
          <template #header>
            <div class="card-header">
              <span>系统 Hooks</span>
              <el-tag size="small" effect="plain">{{ hooks.length }} 条</el-tag>
            </div>
          </template>
          <div v-if="hooks.length" class="hooks-list">
            <div v-for="(h, idx) in hooks" :key="idx" class="hook-item">
              <el-tag size="small" effect="plain">{{ h.event }}</el-tag>
              <code class="hook-cmd">{{ h.command }}</code>
            </div>
          </div>
          <el-empty v-else :image-size="48" description="暂无 hooks" />
        </el-card>
      </el-col>

      <!-- 凭据池 -->
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="sys-card">
          <template #header>
            <div class="card-header">
              <span>凭据池</span>
              <el-tag size="small" effect="plain">{{ credentialCount }} 项</el-tag>
            </div>
          </template>
          <div v-if="credentialEntries.length" class="cred-list">
            <div v-for="(c, idx) in credentialEntries" :key="idx" class="cred-item">
              <span class="cred-provider">{{ c.provider }}</span>
              <span class="cred-meta">{{ c.label || c.api_key_preview || '已配置' }}</span>
            </div>
          </div>
          <el-empty v-else :image-size="48" description="暂无凭据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  ElCard, ElDescriptions, ElDescriptionsItem, ElButton, ElTag,
  ElStatistic, ElMessage, ElMessageBox, ElProgress, ElDivider,
} from 'element-plus'
import { Refresh, Switch, Upload, Download } from '@element-plus/icons-vue'
import { hermes } from '@/api/hermes'

// ── 状态 ──────────────────────────────────────────
const loading = ref(false)
const checkingUpdate = ref(false)
const updating = ref(false)
const gatewayOpsBusy = ref(false)

// ── 系统状态 ──────────────────────────────────────
const version = ref('')
const configVersion = ref('')
const latestVersion = ref('')
const canUpdate = ref(false)

// ── 网关 ─────────────────────────────────────────
const gatewayRunning = ref(false)
const gatewayPlatforms = ref<string[]>([])
const lastHeartbeat = ref('')

// ── 系统统计 ─────────────────────────────────────
const stats = ref<Record<string, any>>({})

// ── Ops ──────────────────────────────────────────
const ops = ref<Record<string, any>>({})
const opsEntries = computed(() =>
  Object.entries(ops.value || {}).map(([key, val]) => ({ key, val }))
)
const opsEmptyText = computed(() => {
  if (!Object.keys(ops.value || {}).length) return '--'
  return '正常'
})

// ── 运维增强：备份 / Hooks / 凭据 ────────────────
const backingUp = ref(false)
const lastBackupTime = ref('')
const lastBackupArchive = ref('')
const hooks = ref<any[]>([])
const credentialEntries = ref<Array<{ provider: string; label?: string; api_key_preview?: string }>>([])
const credentialCount = computed(() => credentialEntries.value.length)

async function loadOpsExtras() {
  try {
    // 备份信息：ops/checkpoints 返回备份清单
    const cp: any = await hermes.getCheckpoints().catch(() => null)
    const list = cp?.data?.checkpoints ?? cp?.checkpoints ?? cp?.items ?? []
    if (Array.isArray(list) && list.length) {
      const latest = list[0]
      lastBackupArchive.value = latest?.archive ?? latest?.path ?? ''
      lastBackupTime.value = latest?.created_at
        ? new Date(latest.created_at * 1000).toLocaleString('zh-CN')
        : '存在备份'
    }
  } catch {
    // 忽略：备份信息可选
  }

  try {
    const h: any = await hermes.getHooks()
    hooks.value = (h?.data ?? h ?? []).map((item: any) => ({
      event: item.event ?? '?',
      command: item.command ?? item.cmd ?? '',
    })).filter((x: any) => x.event && x.command)
  } catch {
    hooks.value = []
  }

  try {
    const c: any = await hermes.getCredentialPool()
    const pool = c?.data ?? c ?? {}
    // 结构：{ providers: [{ provider, entries: [...] }] }
    const providers = pool.providers ?? pool
    if (Array.isArray(providers)) {
      credentialEntries.value = providers.flatMap((p: any) => {
        const providerName = p?.provider ?? p?.name ?? '?'
        const entries = Array.isArray(p?.entries) ? p.entries : Array.isArray(p) ? p : []
        return entries.map((item: any) => ({
          provider: providerName,
          label: item?.label,
          api_key_preview: item?.token_preview ?? item?.api_key_preview,
        }))
      })
    } else {
      credentialEntries.value = Object.entries(providers ?? {}).flatMap(([provider, arr]) =>
        (Array.isArray(arr) ? arr : []).map((item: any) => ({
          provider,
          label: item?.label,
          api_key_preview: item?.token_preview ?? item?.api_key_preview,
        })),
      )
    }
  } catch {
    credentialEntries.value = []
  }
}

async function handleBackup() {
  backingUp.value = true
  try {
    const res: any = await hermes.runBackup()
    const data = res?.data ?? res ?? {}
    lastBackupArchive.value = data?.archive ?? data?.path ?? ''
    lastBackupTime.value = new Date().toLocaleString('zh-CN')
    ElMessage.success('备份完成')
  } catch (e: any) {
    ElMessage.error(e?.message || '备份失败')
  } finally {
    backingUp.value = false
  }
}

function downloadBackup() {
  const url = hermes.downloadBackupUrl(lastBackupArchive.value)
  if (!url) {
    ElMessage.warning('暂无备份可下载')
    return
  }
  window.open(url, '_blank')
}

// ── 统计百分比 ───────────────────────────────────
const cpuPercent = computed(() => toPercent(stats.value?.cpu))
const memoryPercent = computed(() => toPercent(stats.value?.memory))
const diskPercent = computed(() => toPercent(stats.value?.disk))

function toPercent(v: any): number {
  if (typeof v === 'number') return Math.min(100, Math.max(0, Math.round(v)))
  if (v && typeof v === 'object') {
    const pct = v.percent ?? v.usage_percent
    const n = Number(pct)
    if (Number.isFinite(n)) return Math.min(100, Math.max(0, Math.round(n)))
    // 形如 { used, total }
    if (Number(v.used) >= 0 && Number(v.total) > 0) {
      return Math.min(100, Math.round((Number(v.used) / Number(v.total)) * 100))
    }
  }
  return 0
}

function usageColor(pct: number): string {
  if (pct >= 90) return '#f56c6c'
  if (pct >= 70) return '#e6a23c'
  return '#4f46e5'
}

// ── 数据加载 ─────────────────────────────────────
async function loadAll() {
  loading.value = true
  try {
    // getGateway() 现在指向 status API（已包含 gateway 信息）
    // getOps() 现在指向 system/stats（与 getSystemStats 相同），合并避免重复调用
    const [statusRes, gatewayRes, statsRes]: any[] = await Promise.all([
      hermes.getStatus(),
      hermes.getGateway(),
      hermes.getSystemStats(),
    ])

    const st = statusRes?.data ?? statusRes ?? {}
    version.value = st.version ?? st.hermes_version ?? ''
    configVersion.value = st.config_version ?? st.config ?? ''
    latestVersion.value = st.latest_version ?? st.latest ?? ''
    canUpdate.value = !!(
      st.can_update_hermes ?? st.can_update ?? st.has_update
    )

    const gw = gatewayRes?.data ?? gatewayRes ?? {}
    gatewayRunning.value = !!(gw.running ?? gw.gateway_running ?? false)
    gatewayPlatforms.value = Array.isArray(gw.platforms)
      ? gw.platforms
      : Array.isArray(st.gateway_platforms)
        ? st.gateway_platforms
        : []
    lastHeartbeat.value = gw.last_heartbeat ?? gw.heartbeat_at ?? ''

    stats.value = statsRes?.data ?? statsRes ?? {}
    ops.value = stats.value // ops 与 system/stats 相同
    await loadOpsExtras()
  } catch (e: any) {
    console.error('[system] 加载系统状态失败', e)
    ElMessage.error(e?.message || '加载系统状态失败')
  } finally {
    loading.value = false
  }
}

// ── 检测更新 ─────────────────────────────────────
async function checkUpdate() {
  checkingUpdate.value = true
  try {
    const res: any = await hermes.getStatus()
    const st = res?.data ?? res ?? {}
    latestVersion.value = st.latest_version ?? st.latest ?? latestVersion.value
    canUpdate.value = !!(st.can_update_hermes ?? st.can_update ?? false)
    ElMessage.success(
      canUpdate.value
        ? `检测到新版本：${latestVersion.value || '--'}`
        : '当前已是最新版本'
    )
  } catch (e: any) {
    ElMessage.error(e?.message || '检测更新失败')
  } finally {
    checkingUpdate.value = false
  }
}

// ── 执行更新 ─────────────────────────────────────
async function confirmUpdate() {
  try {
    await ElMessageBox.confirm(
      `确定要更新 hermes 到最新版本${latestVersion.value ? '（' + latestVersion.value + '）' : ''}吗？\n更新过程中服务可能会重启，请谨慎操作。`,
      '执行系统更新',
      {
        confirmButtonText: '确认更新',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
  } catch {
    return
  }
  updating.value = true
  try {
    const res: any = await hermes.updateHermes()
    const data = res?.data ?? res ?? {}
    if (data.ok === false) {
      ElMessage.error(data.message || '更新失败')
      return
    }
    ElMessage.success('更新已触发，系统将自动重启生效')
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.message || '执行更新失败')
  } finally {
    updating.value = false
  }
}

// ── 网关操作 ─────────────────────────────────────
const GATEWAY_ACTIONS: Record<string, { title: string; message: string; run: () => Promise<any> }> = {
  start: {
    title: '启动网关',
    message: '确定要启动 Hermes 网关吗？',
    run: () => hermes.startGateway(),
  },
  stop: {
    title: '停止网关',
    message: '确定要停止 Hermes 网关吗？停止后将无法接收消息平台的消息。',
    run: () => hermes.stopGateway(),
  },
  restart: {
    title: '重启网关',
    message: '确定要重启 Hermes 网关吗？重启期间消息推送会短暂中断。',
    run: () => hermes.restartGateway(),
  },
}

async function confirmGateway(action: 'start' | 'stop' | 'restart') {
  const cfg = GATEWAY_ACTIONS[action]
  if (!cfg) return
  try {
    await ElMessageBox.confirm(cfg.message, cfg.title, {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  gatewayOpsBusy.value = true
  try {
    const res: any = await cfg.run()
    const data = res?.data ?? res ?? {}
    if (data.ok === false) {
      ElMessage.error(data.message ?? `${cfg.title}失败`)
      return
    }
    ElMessage.success(`${cfg.title}成功`)
    await loadAll()
  } catch (e: any) {
    ElMessage.error(e?.message || `${cfg.title}失败`)
  } finally {
    gatewayOpsBusy.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.hermes-system-page {
  padding: 4px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary, #1f2937);
}

.page-subtitle {
  font-size: 13px;
  color: var(--el-text-color-secondary, #909399);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sys-card {
  border-radius: 10px;
  border: 1px solid var(--el-border-color-lighter, #ebeef5);
  margin-bottom: 16px;
  transition: box-shadow 0.2s ease;
}

.sys-card:hover {
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-sub {
  font-size: 12px;
  color: var(--el-text-color-secondary, #909399);
}

.update-tag {
  margin-left: auto;
}

.sys-desc {
  margin-bottom: 14px;
}

.sys-desc :deep(.el-descriptions__label) {
  width: 120px;
  color: var(--el-text-color-secondary, #606266);
  font-weight: 500;
}

.version-text {
  font-weight: 600;
  color: var(--el-color-primary, #4f46e5);
}

.update-actions,
.gateway-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.gateway-stats {
  display: flex;
  gap: 32px;
  padding: 8px 2px 14px;
}

.gateway-stats .el-statistic {
  --el-statistic-content-font-size: 20px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #f56c6c;
}

.stat-value.online {
  color: #67c23a;
}

.platform-tag {
  margin-right: 6px;
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
  box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.2);
}

/* ── 系统统计 ── */
.stats-card {
  margin-bottom: 0;
}

.stats-row {
  margin-bottom: 8px;
}

.stat-item {
  padding: 6px 0;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-regular, #606266);
  margin-bottom: 10px;
}

.stat-progress {
  width: 100%;
}

.ops-desc {
  margin-top: 4px;
}

.ops-desc :deep(.el-descriptions__label) {
  width: 160px;
}

.ops-desc .ops-desc-item {
  word-break: break-all;
}

.ops-desc .ops-value-on {
  color: var(--el-color-success, #67c23a);
  font-weight: 600;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .sys-card:hover {
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.14);
  }
}

/* 运维增强卡片 */
.ops-row {
  margin-top: 16px;
}

.ops-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.hooks-list,
.cred-list {
  max-height: 220px;
  overflow-y: auto;
}

.hook-item,
.cred-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px;
  border-bottom: 1px solid var(--el-border-color-lighter, #ebeef5);
  font-size: 13px;
}

.hook-item:last-child,
.cred-item:last-child {
  border-bottom: none;
}

.hook-cmd {
  font-family: var(--el-font-family-mono, monospace);
  font-size: 12px;
  color: var(--el-text-color-regular, #606266);
  word-break: break-all;
}

.cred-provider {
  font-weight: 600;
  color: var(--el-color-primary, #4f46e5);
}

.cred-meta {
  color: var(--el-text-color-secondary, #909399);
  font-size: 12px;
}
</style>