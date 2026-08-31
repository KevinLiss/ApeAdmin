import request from './request'

// ---- Auth ----
export const login = (data: { username: string; password: string; captcha_id?: string; captcha_code?: string }) =>
  request.post('/auth/login', data)
export const getLoginCaptcha = () => request.get('/login-captcha/captcha')

export const getUserInfo = () => request.get('/auth/userinfo')

// 个人中心
export const getProfile = () => request.get('/auth/profile')
export const updateProfile = (data: any) => request.put('/auth/profile', data)
export const changePassword = (data: any) => request.put('/auth/profile/password', data)

export const logout = () => request.post('/auth/logout')

// ---- Users ----
export const getUsers = (params: any) => request.get('/users', { params })
export const createUser = (data: any) => request.post('/users', data)
export const updateUser = (id: number, data: any) => request.put(`/users/${id}`, data)
export const deleteUser = (id: number) => request.delete(`/users/${id}`)
export const resetUserPassword = (id: number, newPassword: string) =>
  request.put(`/users/${id}/reset-password?new_password=${encodeURIComponent(newPassword)}`)

// ---- Roles ----
export const getRoles = (params: any = {}) => request.get('/roles', { params })
export const createRole = (data: any) => request.post('/roles', data)
export const updateRole = (id: number, data: any) => request.put(`/roles/${id}`, data)
export const deleteRole = (id: number) => request.delete(`/roles/${id}`)
export const getAllRoles = () => request.get('/roles/all')

// ---- Menus ----
export const getMenuTree = () => request.get('/menus/tree')
export const createMenu = (data: any) => request.post('/menus', data)
export const updateMenu = (id: number, data: any) => request.put(`/menus/${id}`, data)
export const deleteMenu = (id: number) => request.delete(`/menus/${id}`)

// ---- Depts ----
export const getDeptTree = () => request.get('/depts/tree')
export const createDept = (data: any) => request.post('/depts', data)
export const updateDept = (id: number, data: any) => request.put(`/depts/${id}`, data)
export const deleteDept = (id: number) => request.delete(`/depts/${id}`)

// ---- Plugins ----
export const getPlugins = (params: any = {}) => request.get('/plugins', { params })
export const togglePlugin = (id: number, enabled: boolean) =>
  request.put(`/plugins/${id}/toggle`, { enabled })
export const getPluginConfig = (id: number) => request.get(`/plugins/${id}/config`)
export const updatePluginConfig = (id: number, config: any) =>
  request.put(`/plugins/${id}/config`, { config })
export const uploadPlugin = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/plugins/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const restartServer = () => request.post('/plugins/restart')
export const deletePlugin = (id: number) => request.delete(`/plugins/${id}`)

// ---- MCP ----
export const getMcpTools = () => request.get('/mcp/tools')
export const callMcpTool = (name: string, arguments_: any) =>
  request.post('/mcp/tools/call', { name, arguments: arguments_ })
export const getMcpResources = () => request.get('/mcp/resources')
export const getMcpResourcesRead = (params: any) =>
  request.get('/mcp/resources/read', { params })
export const getMcpPrompts = () => request.get('/mcp/prompts')
export const renderMcpPrompt = (name: string, arguments_: any) =>
  request.post('/mcp/prompts/render', { name, arguments: arguments_ })
export const getMcpAuditLogs = (params: any = {}) => request.get('/mcp/audit-logs', { params })

// ---- AI 模型密钥管理 ----
export const getProviders = (params: any = {}) => request.get('/ai/providers', { params })
export const getAllProviders = () => request.get('/ai/providers/all')
export const createProvider = (data: any) => request.post('/ai/providers', data)
export const updateProvider = (id: number, data: any) => request.put(`/ai/providers/${id}`, data)
export const deleteProvider = (id: number) => request.delete(`/ai/providers/${id}`)
export const testProvider = (id: number) => request.post(`/ai/providers/${id}/test`)

// ---- AI 对话 ----
export const chat = (data: any) => request.post('/ai/chat', data)

// ---- 系统日志 ----
export const getLogs = (params: any = {}) => request.get('/logs', { params })
export const getLogDetail = (id: number) => request.get(`/logs/${id}`)
export const deleteLog = (id: number) => request.delete(`/logs/${id}`)
export const clearLogs = () => request.delete('/logs')

// ---- 仪表盘统计 ----
export const getDashboardStats = () => request.get('/dashboard/stats')
export const getDashboardSystem = () => request.get('/dashboard/system')

// ---- System files ----
export const getFileFolders = () => request.get('/files/folders/tree')
export const getFiles = (params: any = {}) => request.get('/files', { params })
export const createFileFolder = (data: any) => request.post('/files/folders', data)
export const renameFileFolder = (id: number, data: any) => request.put(`/files/folders/${id}`, data)
export const deleteFileFolder = (id: number) => request.delete(`/files/folders/${id}`)
export const uploadSystemFile = (file: File, folderId: number) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/files/upload?folder_id=${folderId}`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export const deleteSystemFile = (id: number) => request.delete(`/files/${id}`)
export const downloadSystemFileUrl = (id: number) => `/api/v1/files/${id}/download`

// ---- 系统设置 ----
export const getPublicSettings = () => request.get('/settings/public')
export const getSettings = () => request.get('/settings')
export const updateSettings = (items: Record<string, string>) => request.put('/settings', { items })
export const updateSetting = (key: string, value: string) => request.put(`/settings/${key}`, { value })

/**
 * SSE 流式对话 —— 使用 fetch + ReadableStream 解析 SSE
 * @param data  ChatStreamRequest body
 * @param onChunk  每收到一个 SSE event JSON 调用
 * @returns AbortController（可用于中止请求）
 */
export function chatStream(
  data: any,
  onChunk: (event: any) => void
): AbortController {
  const controller = new AbortController()
  const token = localStorage.getItem('apeadmin_token')

  fetch('/api/v1/ai/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : '',
    },
    body: JSON.stringify(data),
    signal: controller.signal,
  })
    .then(async (resp) => {
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const reader = resp.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const chunk = line.slice(6).trim()
            if (!chunk) continue
            try {
              onChunk(JSON.parse(chunk))
            } catch {
              // skip invalid JSON
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onChunk({ type: 'error', message: err.message || '请求失败' })
      }
    })

  return controller
}
