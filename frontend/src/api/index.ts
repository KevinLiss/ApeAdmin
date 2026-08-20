import request from './request'

// ---- Auth ----
export const login = (data: { username: string; password: string }) =>
  request.post('/auth/login', data)

export const getUserInfo = () => request.get('/auth/userinfo')

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

// ---- MCP ----
export const getMcpTools = () => request.get('/mcp/tools')
export const callMcpTool = (name: string, arguments_: any) =>
  request.post('/mcp/tools/call', { name, arguments: arguments_ })
export const getMcpResources = () => request.get('/mcp/resources')
export const getMcpResourcesRead = (params: any) =>
  request.get('/mcp/resources/read', { params })
export const getMcpPrompts = () => request.get('/mcp/prompts')