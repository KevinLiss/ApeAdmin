import request from './request'

// ── 引擎状态 ──────────────────────────────────────
export const getHermesStatus = () => request.get('/hermes/status')
export const getHermesWsUrl = () => request.get('/hermes/ws-url')
export const getHermesHealth = () => request.get('/hermes/health')
export const createHermesSession = (data: any = {}) => request.post('/hermes/sessions', data)

// ── Hermes HTTP 代理（转发到 hermes dashboard /api/*）──────────────
// 所有 hermes HTTP API 都经 ApeAdmin /api/v1/hermes/proxy/{path} 代理
// 代理自动附加 hermes 认证 token，前端无需关心
// 路径规格与官方 web/src/lib/api.ts（168 方法）逐一对齐

const PROXY_BASE = '/hermes/proxy'

/** 通用 hermes API 调用——经 ApeAdmin 代理 */
const hermesGet = (path: string, params?: any) =>
  request.get(`${PROXY_BASE}/${path}`, params ? { params } : undefined)
const hermesPost = (path: string, data?: any) =>
  request.post(`${PROXY_BASE}/${path}`, data)
const hermesPut = (path: string, data?: any) =>
  request.put(`${PROXY_BASE}/${path}`, data)
const hermesDelete = (path: string, data?: any) =>
  request.delete(`${PROXY_BASE}/${path}`, data)
const hermesPatch = (path: string, data?: any) =>
  request.patch(`${PROXY_BASE}/${path}`, data)

/** 路径段编码（保留 /，逐段 encodeURIComponent）——用于插件 registry key（如 vendor/name） */
const pluginPath = (name: string) => name.split('/').map(encodeURIComponent).join('/')

export const hermes = {
  // ── Status / System ────────────────────────────
  getStatus: () => hermesGet('status'),
  getSystemStats: () => hermesGet('system/stats'),
  getOps: () => hermesGet('system/stats'),

  // ── Auth ───────────────────────────────────────
  getAuthMe: () => hermesGet('auth/me'),
  // hermes 端 logout 实际路由是 /auth/logout（无 /api 前缀），
  // 由后端代理做路径重写，前端无需特殊处理。
  logout: () => hermesPost('auth/logout'),
  getWsTicket: () => hermesPost('auth/ws-ticket'),

  // ── Sessions ───────────────────────────────────
  getSessions: (params?: { limit?: number; offset?: number; order?: string; q?: string; source?: string; sources?: string; exclude_sources?: string; profile?: string }) =>
    hermesGet('sessions', params),
  getSessionMessages: (id: string, profile?: string) =>
    hermesGet(`sessions/${encodeURIComponent(id)}/messages`, { profile }),
  getSessionDetail: (id: string, profile?: string) =>
    hermesGet(`sessions/${encodeURIComponent(id)}`, { profile }),
  getSessionLatestDescendant: (id: string, profile?: string) =>
    hermesGet(`sessions/${encodeURIComponent(id)}/latest-descendant`, { profile }),
  deleteSession: (id: string, profile?: string) =>
    hermesDelete(`sessions/${encodeURIComponent(id)}`, { profile }),
  renameSession: (id: string, title: string, profile?: string) =>
    hermesPatch(`sessions/${encodeURIComponent(id)}`, { title, profile }),
  getSessionStats: (profile?: string) => hermesGet('sessions/stats', { profile }),
  getEmptySessionsCount: (profile?: string) => hermesGet('sessions/empty/count', { profile }),
  deleteEmptySessions: (profile?: string) => hermesDelete('sessions/empty', { profile }),
  bulkDeleteSessions: (ids: string[], profile?: string) =>
    hermesPost('sessions/bulk-delete', { ids, profile }),
  exportSessionUrl: (id: string, profile?: string) =>
    `${PROXY_BASE}/sessions/${encodeURIComponent(id)}/export${profile ? `?profile=${encodeURIComponent(profile)}` : ''}`,
  importSessions: (sessions: any[], profile?: string) =>
    hermesPost('sessions/import', { sessions, profile }),
  pruneSessions: (older_than_days: number, source?: string, profile?: string) =>
    hermesPost('sessions/prune', { older_than_days, source, profile }),
  searchSessions: (q: string, opts?: { limit?: number; offset?: number; order?: string; source?: string; sources?: string; exclude_sources?: string; profile?: string }) =>
    hermesGet('sessions/search', { q, ...opts }),

  // ── Models ─────────────────────────────────────
  getModelInfo: (profile?: string) => hermesGet('model/info', { profile }),
  setModel: (model: string, provider?: string) =>
    hermesPost('model/set', { model, provider }),
  setModelAssignment: (body: { scope: 'main' | 'auxiliary'; provider: string; model: string; base_url?: string; task?: string; confirm_expensive_model?: boolean }, profile?: string) =>
    hermesPost('model/set', { ...body, profile }),
  getModelOptions: (profile?: string, refresh?: boolean) =>
    hermesGet('model/options', { profile, ...(refresh ? { refresh: 1 } : {}), include_unconfigured: 1 }),
  getModelRecommended: () => hermesGet('model/recommended-default'),
  getAuxiliaryModels: (profile?: string) => hermesGet('model/auxiliary', { profile }),
  setAuxiliaryModels: (data: any) => hermesPut('model/auxiliary', data),
  getMoa: () => hermesGet('model/moa'),
  setMoa: (data: any) => hermesPut('model/moa', data),
  getMoaModels: () => hermesGet('model/moa'),
  saveMoaModels: (data: any) => hermesPut('model/moa', data),

  // ── Config ─────────────────────────────────────
  getConfig: (profile?: string) => hermesGet('config', { profile }),
  saveConfig: (config: any, profile?: string) => hermesPut('config', { config, profile }),
  getConfigDefaults: () => hermesGet('config/defaults'),
  getDefaults: () => hermesGet('config/defaults'),
  getConfigSchema: () => hermesGet('config/schema'),
  getSchema: () => hermesGet('config/schema'),
  getConfigRaw: (profile?: string) => hermesGet('config/raw', { profile }),
  saveConfigRaw: (yaml_text: string, profile?: string) =>
    hermesPut('config/raw', { yaml_text, profile }),
  setConfig: (data: any) => hermesPut('config', { config: data }),
  runConfigMigrate: () => hermesPost('ops/config-migrate'),

  // ── Env ────────────────────────────────────────
  getEnv: () => hermesGet('env'),
  setEnv: (data: any) => hermesPut('env', data),
  getEnvVars: () => hermesGet('env'),
  setEnvVar: (key: string, value: string) => hermesPut('env', { key, value }),
  deleteEnvVar: (key: string) => hermesDelete('env', { key }),
  revealEnvVar: (key: string) => hermesPost('env/reveal', { key }),
  revealEnv: (key: string) => hermesPost('env/reveal', { key }),

  // ── Files ──────────────────────────────────────
  listFiles: (path?: string) => hermesGet('files', { path }),
  readFile: (path: string) => hermesGet('files/read', { path }),
  uploadFile: (path: string, file: File, overwrite = true) => {
    const form = new FormData()
    form.append('path', path)
    form.append('overwrite', String(overwrite))
    form.append('file', file, file.name)
    return request.post(`${PROXY_BASE}/files/upload-stream`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  createDir: (path: string) => hermesPost('files/mkdir', { path }),
  createDirectory: (path: string) => hermesPost('files/mkdir', { path }),
  deleteFile: (path: string, recursive = false) =>
    hermesDelete('files', { path, recursive }),

  // ── Logs ───────────────────────────────────────
  getLogs: (params: { file?: string; lines?: number; level?: string; component?: string }) =>
    hermesGet('logs', params),

  // ── Analytics ──────────────────────────────────
  getAnalytics: (days: number) => hermesGet('analytics/usage', { days }),
  getModelsAnalytics: (days: number) => hermesGet('analytics/models', { days }),

  // ── Cron + Automation ──────────────────────────
  getCronJobs: (profile: string = 'all') => hermesGet('cron/jobs', { profile }),
  createCronJob: (data: any, profile: string = 'default') =>
    hermesPost(`cron/jobs${profile ? `?profile=${encodeURIComponent(profile)}` : ''}`, data),
  updateCronJob: (id: string, updates: any, profile: string = 'default') =>
    hermesPut(`cron/jobs/${encodeURIComponent(id)}?profile=${encodeURIComponent(profile)}`, { updates }),
  deleteCronJob: (id: string, profile: string = 'default') =>
    hermesDelete(`cron/jobs/${encodeURIComponent(id)}?profile=${encodeURIComponent(profile)}`),
  triggerCronJob: (id: string, profile: string = 'default') =>
    hermesPost(`cron/jobs/${encodeURIComponent(id)}/trigger?profile=${encodeURIComponent(profile)}`),
  pauseCronJob: (id: string, profile: string = 'default') =>
    hermesPost(`cron/jobs/${encodeURIComponent(id)}/pause?profile=${encodeURIComponent(profile)}`),
  resumeCronJob: (id: string, profile: string = 'default') =>
    hermesPost(`cron/jobs/${encodeURIComponent(id)}/resume?profile=${encodeURIComponent(profile)}`),
  getCronBlueprints: () => hermesGet('cron/blueprints'),
  getAutomationBlueprints: () => hermesGet('cron/blueprints'),
  instantiateAutomationBlueprint: (body: { blueprint: string; values: Record<string, string> }, profile: string = 'default') =>
    hermesPost(`cron/blueprints/instantiate?profile=${encodeURIComponent(profile)}`, body),
  getCronDeliveryTargets: () => hermesGet('cron/delivery-targets'),

  // ── Profiles ───────────────────────────────────
  getProfiles: () => hermesGet('profiles'),
  getActiveProfile: () => hermesGet('profiles/active'),
  setActiveProfile: (name: string) =>
    hermesPost('profiles/active', { name }),
  createProfile: (data: any) => hermesPost('profiles', data),
  updateProfileDescription: (name: string, description: string) =>
    hermesPut(`profiles/${encodeURIComponent(name)}/description`, { description }),
  describeProfileAuto: (name: string, overwrite = true) =>
    hermesPost(`profiles/${encodeURIComponent(name)}/describe-auto`, { overwrite }),
  setProfileModel: (name: string, provider: string, model: string) =>
    hermesPut(`profiles/${encodeURIComponent(name)}/model`, { provider, model }),
  renameProfile: (name: string, newName: string) =>
    hermesPatch(`profiles/${encodeURIComponent(name)}`, { new_name: newName }),
  deleteProfile: (name: string) =>
    hermesDelete(`profiles/${encodeURIComponent(name)}`),
  getProfileSetupCommand: (name: string) =>
    hermesGet(`profiles/${encodeURIComponent(name)}/setup-command`),
  getProfileSoul: (name: string) =>
    hermesGet(`profiles/${encodeURIComponent(name)}/soul`),
  updateProfileSoul: (name: string, content: string) =>
    hermesPut(`profiles/${encodeURIComponent(name)}/soul`, { content }),

  // ── Skills + Hub ───────────────────────────────
  getSkills: (profile?: string) => hermesGet('skills', { profile }),
  toggleSkill: (name: string, enabled: boolean, profile?: string) =>
    hermesPut('skills/toggle', { name, enabled, profile }),
  getSkillContent: (name: string, profile?: string) =>
    hermesGet('skills/content', { name, profile }),
  createSkill: (data: { name: string; content: string; category?: string }, profile?: string) =>
    hermesPost('skills', { ...data, profile }),
  updateSkillContent: (name: string, content: string, profile?: string) =>
    hermesPut('skills/content', { name, content, profile }),
  installSkillHub: (identifier: string, profile?: string) =>
    hermesPost('skills/hub/install', { identifier, profile }),
  installSkillFromHub: (identifier: string, profile?: string) =>
    hermesPost('skills/hub/install', { identifier, profile }),
  uninstallSkillHub: (name: string, profile?: string) =>
    hermesPost('skills/hub/uninstall', { name, profile }),
  uninstallSkillFromHub: (name: string, profile?: string) =>
    hermesPost('skills/hub/uninstall', { name, profile }),
  updateSkillHub: (profile?: string) =>
    hermesPost('skills/hub/update', { profile }),
  updateSkillsFromHub: (profile?: string) =>
    hermesPost('skills/hub/update', { profile }),
  searchSkillHub: (q: string, source: string = 'all', limit: number = 20, profile?: string) =>
    hermesGet('skills/hub/search', { q, source, limit, profile }),
  searchSkillsHub: (q: string, source: string = 'all', limit: number = 20, profile?: string) =>
    hermesGet('skills/hub/search', { q, source, limit, profile }),
  getSkillHubSources: (profile?: string) => hermesGet('skills/hub/sources', { profile }),
  previewSkillFromHub: (identifier: string) =>
    hermesGet('skills/hub/preview', { identifier }),
  scanSkillFromHub: (identifier: string) =>
    hermesGet('skills/hub/scan', { identifier }),

  // ── Toolsets ───────────────────────────────────
  getToolsets: (profile?: string) => hermesGet('tools/toolsets', { profile }),
  toggleToolset: (name: string, enabled: boolean, profile?: string) =>
    hermesPut(`tools/toolsets/${encodeURIComponent(name)}`, { enabled, profile }),
  getToolsetConfig: (name: string, profile?: string) =>
    hermesGet(`tools/toolsets/${encodeURIComponent(name)}/config`, { profile }),
  selectToolsetProvider: (name: string, provider: string, profile?: string) =>
    hermesPut(`tools/toolsets/${encodeURIComponent(name)}/provider`, { provider, profile }),
  saveToolsetEnv: (name: string, env: Record<string, string>, profile?: string) =>
    hermesPut(`tools/toolsets/${encodeURIComponent(name)}/env`, { env, profile }),
  runToolsetPostSetup: (name: string, key: string, profile?: string) =>
    hermesPost(`tools/toolsets/${encodeURIComponent(name)}/post-setup`, { key, profile }),

  // ── MCP ────────────────────────────────────────
  getMcpServers: (profile?: string) => hermesGet('mcp/servers', { profile }),
  addMcpServer: (data: any) => hermesPost('mcp/servers', data),
  authMcpServer: (name: string) =>
    hermesPost(`mcp/servers/${encodeURIComponent(name)}/auth`),
  getMcpOAuthFlow: (flowId: string) =>
    hermesGet(`mcp/oauth/flows/${encodeURIComponent(flowId)}`),
  removeMcpServer: (name: string) =>
    hermesDelete(`mcp/servers/${encodeURIComponent(name)}`),
  testMcpServer: (name: string) =>
    hermesPost(`mcp/servers/${encodeURIComponent(name)}/test`),
  setMcpServerEnabled: (name: string, enabled: boolean) =>
    hermesPut(`mcp/servers/${encodeURIComponent(name)}/enabled`, { enabled }),
  getMcpCatalog: () => hermesGet('mcp/catalog'),
  installMcpCatalogEntry: (name: string, env: Record<string, string> = {}, enable = true) =>
    hermesPost('mcp/catalog/install', { name, env, enable }),

  // ── OAuth（AI 提供商登录）───────────────────────
  getOAuthProviders: (profile?: string) => hermesGet('providers/oauth', { profile }),
  disconnectOAuthProvider: (providerId: string) =>
    hermesDelete(`providers/oauth/${encodeURIComponent(providerId)}`),
  startOAuthLogin: (providerId: string) =>
    hermesPost(`providers/oauth/${encodeURIComponent(providerId)}/start`),
  submitOAuthCode: (providerId: string, sessionId: string, code: string) =>
    hermesPost(`providers/oauth/${encodeURIComponent(providerId)}/submit`, { session_id: sessionId, code }),
  pollOAuthSession: (providerId: string, sessionId: string) =>
    hermesGet(`providers/oauth/${encodeURIComponent(providerId)}/poll/${encodeURIComponent(sessionId)}`),
  cancelOAuthSession: (sessionId: string) =>
    hermesDelete(`providers/oauth/sessions/${encodeURIComponent(sessionId)}`),

  // ── Messaging Platforms（Channels）──────────────
  getMessagingPlatforms: () => hermesGet('messaging/platforms'),
  getPlatforms: () => hermesGet('messaging/platforms'),
  updateMessagingPlatform: (id: string, body: { enabled?: boolean; env?: Record<string, string>; clear_env?: string[] }) =>
    hermesPut(`messaging/platforms/${encodeURIComponent(id)}`, body),
  testMessagingPlatform: (id: string) =>
    hermesPost(`messaging/platforms/${encodeURIComponent(id)}/test`),
  // Telegram onboarding 四件套
  startTelegramOnboarding: (body: { bot_name?: string } = {}) =>
    hermesPost('messaging/telegram/onboarding/start', body),
  getTelegramOnboardingStatus: (pairingId: string) =>
    hermesGet(`messaging/telegram/onboarding/${encodeURIComponent(pairingId)}`),
  applyTelegramOnboarding: (pairingId: string, body: { allowed_user_ids: string[]; profile?: string }) =>
    hermesPost(`messaging/telegram/onboarding/${encodeURIComponent(pairingId)}/apply`, body),
  cancelTelegramOnboarding: (pairingId: string) =>
    hermesDelete(`messaging/telegram/onboarding/${encodeURIComponent(pairingId)}`),
  // WhatsApp onboarding 四件套
  startWhatsAppOnboarding: (body: { mode?: 'bot' | 'self-chat'; allowed_users?: string[] } = {}) =>
    hermesPost('messaging/whatsapp/onboarding/start', body),
  getWhatsAppOnboardingStatus: (pairingId: string) =>
    hermesGet(`messaging/whatsapp/onboarding/${encodeURIComponent(pairingId)}`),
  applyWhatsAppOnboarding: (pairingId: string, body: { mode?: string; allowed_users?: string[]; profile?: string }) =>
    hermesPost(`messaging/whatsapp/onboarding/${encodeURIComponent(pairingId)}/apply`, body),
  cancelWhatsAppOnboarding: (pairingId: string) =>
    hermesDelete(`messaging/whatsapp/onboarding/${encodeURIComponent(pairingId)}`),

  // ── Gateway / Hermes / Actions ─────────────────
  getGateway: () => hermesGet('status'),
  restartGateway: () => hermesPost('gateway/restart'),
  startGateway: () => hermesPost('gateway/start'),
  stopGateway: () => hermesPost('gateway/stop'),
  drainGateway: () => hermesPost('gateway/drain'),
  getGatewayMigratePlan: () => hermesGet('gateway/migrate/plan'),
  migrateGatewayToMultiplex: () => hermesPost('gateway/migrate'),
  updateHermes: () => hermesPost('hermes/update'),
  checkHermesUpdate: (force = false) =>
    hermesGet('hermes/update/check', force ? { force: 'true' } : undefined),
  getActionStatus: (name: string, lines = 200) =>
    hermesGet(`actions/${encodeURIComponent(name)}/status`, { lines }),

  // ── Dashboard Plugins（插件中心）────────────────
  getPlugins: () => hermesGet('dashboard/plugins'),
  rescanPlugins: () => hermesGet('dashboard/plugins/rescan'),
  getPluginsHub: () => hermesGet('dashboard/plugins/hub'),
  getPluginsCatalog: () => hermesGet('dashboard/plugins/catalog'),
  installAgentPlugin: (body: { identifier: string; force?: boolean; enable?: boolean; catalog_name?: string }) =>
    hermesPost('dashboard/agent-plugins/install', body),
  enableAgentPlugin: (name: string) =>
    hermesPost(`dashboard/agent-plugins/${pluginPath(name)}/enable`),
  disableAgentPlugin: (name: string) =>
    hermesPost(`dashboard/agent-plugins/${pluginPath(name)}/disable`),
  updateAgentPlugin: (name: string) =>
    hermesPost(`dashboard/agent-plugins/${pluginPath(name)}/update`),
  removeAgentPlugin: (name: string) =>
    hermesDelete(`dashboard/agent-plugins/${pluginPath(name)}`),
  savePluginProviders: (body: { memory_provider?: string; context_engine?: string }) =>
    hermesPut('dashboard/plugin-providers', body),
  setPluginVisibility: (name: string, hidden: boolean) =>
    hermesPost(`dashboard/plugins/${pluginPath(name)}/visibility`, { hidden }),
  // 兼容旧名（MCP 页历史用法）
  getDashboardPlugins: () => hermesGet('dashboard/plugins'),
  getDashboardPluginsCatalog: () => hermesGet('dashboard/plugins/catalog'),
  rescanDashboardPlugins: () => hermesGet('dashboard/plugins/rescan'),

  // ── Themes / Font ──────────────────────────────
  getThemes: () => hermesGet('dashboard/themes'),
  setTheme: (name: string) => hermesPut('dashboard/theme', { name }),
  getFontPref: () => hermesGet('dashboard/font'),
  setFontPref: (font: string) => hermesPut('dashboard/font', { font }),

  // ── Pairing（配对审批）─────────────────────────
  getPairing: () => hermesGet('pairing'),
  approvePairing: (platform: string, request_id: string, profile?: string) =>
    hermesPost('pairing/approve', { platform, request_id, profile }),
  revokePairing: (platform: string, user_id: string, profile?: string) =>
    hermesPost('pairing/revoke', { platform, user_id, profile }),
  clearPendingPairing: () => hermesPost('pairing/clear-pending'),

  // ── Webhooks ───────────────────────────────────
  getWebhooks: () => hermesGet('webhooks'),
  enableWebhooks: () => hermesPost('webhooks/enable'),
  createWebhook: (body: { name: string; description?: string; events?: string[]; deliver: string; deliver_only?: boolean; prompt?: string }) =>
    hermesPost('webhooks', body),
  setWebhookEnabled: (name: string, enabled: boolean) =>
    hermesPut(`webhooks/${encodeURIComponent(name)}/enabled`, { enabled }),
  deleteWebhook: (name: string) =>
    hermesDelete(`webhooks/${encodeURIComponent(name)}`),

  // ── Credentials / Pool ─────────────────────────
  getCredentials: () => hermesGet('credentials/pool'),
  getCredentialPool: () => hermesGet('credentials/pool'),
  setCredential: (data: any) => hermesPost('credentials/pool', data),
  addCredentialPoolEntry: (provider: string, api_key: string, label?: string) =>
    hermesPost('credentials/pool', { provider, api_key, label }),
  removeCredentialPoolEntry: (provider: string, index: number) =>
    hermesDelete(`credentials/pool/${encodeURIComponent(provider)}/${index}`),

  // ── Memory / Providers ─────────────────────────
  getMemory: () => hermesGet('memory'),
  getMemoryProviderConfig: (provider: string) =>
    hermesGet(`memory/providers/${encodeURIComponent(provider)}/config`),
  updateMemoryProviderConfig: (provider: string, values: Record<string, any>) =>
    hermesPut(`memory/providers/${encodeURIComponent(provider)}/config`, { values }),
  setupMemoryProvider: (provider: string, values: Record<string, any> = {}) =>
    hermesPost(`memory/providers/${encodeURIComponent(provider)}/setup`, { values }),
  setMemoryProvider: (provider: string) =>
    hermesPut('memory/provider', { provider }),
  resetMemory: (target: 'all' | 'memory' | 'user' = 'memory') =>
    hermesPost('memory/reset', { target }),

  // ── Curator ────────────────────────────────────
  getCurator: () => hermesGet('curator'),
  runCurator: () => hermesPost('curator/run'),
  pauseCurator: () => hermesPost('curator/paused'),
  setCuratorPaused: (paused: boolean) => hermesPut('curator/paused', { paused }),

  // ── Portal ─────────────────────────────────────
  getPortal: () => hermesGet('portal'),

  // ── Ops：备份/导入/Hooks/检查点/调试 ─────────────
  runDoctor: () => hermesPost('ops/doctor'),
  runSecurityAudit: () => hermesPost('ops/security-audit'),
  runBackup: (output?: string) => hermesPost('ops/backup', { output }),
  downloadBackupUrl: (archive: string) =>
    `${PROXY_BASE}/ops/backup/download?archive=${encodeURIComponent(archive)}`,
  runImport: (archive: string, force = false) =>
    hermesPost('ops/import', { archive, force }),
  runImportUpload: (file: File, force = false) => {
    const form = new FormData()
    form.append('force', String(force))
    form.append('file', file, file.name)
    return request.post(`${PROXY_BASE}/ops/import-upload`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  getHooks: () => hermesGet('ops/hooks'),
  createHook: (body: { event: string; command: string; matcher?: string; timeout?: number; approve?: boolean }) =>
    hermesPost('ops/hooks', body),
  deleteHook: (event: string, command: string) =>
    hermesDelete('ops/hooks', { event, command }),
  getCheckpoints: () => hermesGet('ops/checkpoints'),
  pruneCheckpoints: () => hermesPost('ops/checkpoints/prune'),
  runPromptSize: () => hermesPost('ops/prompt-size'),
  runDump: () => hermesPost('ops/dump'),
  runDebugShare: (body: { redact?: boolean; lines?: number } = {}) =>
    hermesPost('ops/debug-share', { redact: true, lines: 200, ...body }),

  // ── 聊天图片上传（PTY 图链路）────────────────────
  uploadChatImage: (data_url: string, filename: string, profile?: string) =>
    hermesPost('chat/image-upload', { data_url, filename, profile }),
}
