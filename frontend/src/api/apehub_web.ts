/**
 * ApeHub 官网/管理 API 封装
 * 全部接口走 /api/v1/apehub-web/*
 */
import request from './request'

// The shared interceptor unwraps the standard response envelope at runtime.
// Keep the plugin client aligned with that contract instead of exposing AxiosResponse.
const api: any = request

// ---------- 公开（免登录） ----------
export const getPublicConfig = () => api.get('/apehub-web/site/public/config')
export const getPublicContent = () => api.get('/apehub-web/site/public/content')

export const getDocCategories = () => api.get('/apehub-web/site/public/docs/categories')
export const getPublicDocs = (params: any) => api.get('/apehub-web/site/public/docs', { params })
export const getPublicDocDetail = (id: number) => api.get(`/apehub-web/site/public/docs/${id}`)

export const getPublicPlugins = (params: any) => api.get('/apehub-web/site/public/plugins', { params })
export const getPublicPluginCategories = () => api.get('/apehub-web/site/public/plugins/categories')
export const getPublicPluginDetail = (id: number) => api.get(`/apehub-web/site/public/plugins/${id}`)

export const siteRegister = (data: any) => api.post('/apehub-web/site/auth/register', data)
export const siteLogin = (data: any) => api.post('/auth/login', data)

// ---------- 用户（登录） ----------
export const getProfile = () => api.get('/apehub-web/profile')
export const updateProfile = (data: any) => api.put('/apehub-web/profile', data)
export const getWallet = () => api.get('/apehub-web/wallet')
export const updateWallet = (data: any) => api.put('/apehub-web/wallet', data)

export const submitPlugin = (data: any) => api.post('/apehub-web/developer/plugins', data)
export const getMyPlugins = () => api.get('/apehub-web/developer/plugins')
export const getMyPluginDetail = (id: number) => api.get(`/apehub-web/developer/plugins/${id}`)
export const updateMyPlugin = (id: number, data: any) => api.put(`/apehub-web/developer/plugins/${id}`, data)
export const uploadPluginFile = (id: number, formData: FormData, fileType: string) =>
  api.post(`/apehub-web/developer/plugins/${id}/files`, formData, { params: { file_type: fileType } })
export const deletePluginFile = (id: number, fileId: number) =>
  api.delete(`/apehub-web/developer/plugins/${id}/files/${fileId}`)
export const getPluginVersions = (id: number) => api.get(`/apehub-web/developer/plugins/${id}/versions`)
export const createPluginVersion = (id: number, data: any) => api.post(`/apehub-web/developer/plugins/${id}/versions`, data)
export const updatePluginVersion = (id: number, versionId: number, data: any) => api.put(`/apehub-web/developer/plugins/${id}/versions/${versionId}`, data)
export const uploadPluginMedia = (id: number, formData: FormData, params: any) => api.post(`/apehub-web/developer/plugins/${id}/media/upload`, formData, { params })
export const deletePluginMedia = (id: number, mediaId: number) => api.delete(`/apehub-web/developer/plugins/${id}/media/${mediaId}`)
export const analyzePluginVersion = (id: number, versionId: number) => api.post(`/apehub-web/developer/plugins/${id}/versions/${versionId}/analyze`)
export const getPluginAnalysis = (id: number, versionId: number) => api.get(`/apehub-web/developer/plugins/${id}/versions/${versionId}/analysis`)
export const submitPluginVersion = (id: number, versionId: number) => api.post(`/apehub-web/developer/plugins/${id}/versions/${versionId}/submit`)

export const createOrder = (data: any) => api.post('/apehub-web/orders/create', data)
export const getMyOrders = () => api.get('/apehub-web/orders/my')
export const getMyPaidPlugins = () => api.get('/apehub-web/orders/my/paid')
export const getDownloadUrl = (fileId: number) => `/api/v1/apehub-web/files/${fileId}/download`

export const createWithdrawal = (data: any) => api.post('/apehub-web/withdrawals', data)
export const getMyWithdrawals = () => api.get('/apehub-web/withdrawals')
export const getMyIncomes = () => api.get('/apehub-web/incomes')

// ---------- 管理（管理员） ----------
export const getAdminConfig = () => api.get('/apehub-web/admin/config')
export const updateAdminConfig = (data: any) => api.put('/apehub-web/admin/config', data)
export const uploadSiteAsset = (formData: FormData) => api.post('/apehub-web/admin/assets/upload', formData)
export const getAdminNavigation = () => api.get('/apehub-web/admin/navigation')
export const createAdminNavigation = (data: any) => api.post('/apehub-web/admin/navigation', data)
export const updateAdminNavigation = (id: number, data: any) => api.put(`/apehub-web/admin/navigation/${id}`, data)
export const deleteAdminNavigation = (id: number) => api.delete(`/apehub-web/admin/navigation/${id}`)
export const getAdminContent = () => api.get('/apehub-web/admin/content')
export const createAdminContent = (data: any) => api.post('/apehub-web/admin/content', data)
export const updateAdminContent = (id: number, data: any) => api.put(`/apehub-web/admin/content/${id}`, data)
export const deleteAdminContent = (id: number) => api.delete(`/apehub-web/admin/content/${id}`)

export const getAdminDocCategories = () => api.get('/apehub-web/admin/doc-categories')
export const createAdminDocCategory = (data: any) => api.post('/apehub-web/admin/doc-categories', data)
export const updateAdminDocCategory = (id: number, data: any) => api.put(`/apehub-web/admin/doc-categories/${id}`, data)
export const deleteAdminDocCategory = (id: number) => api.delete(`/apehub-web/admin/doc-categories/${id}`)

export const getAdminDocs = (params: any) => api.get('/apehub-web/admin/docs', { params })
export const getAdminDocDetail = (id: number) => api.get(`/apehub-web/admin/docs/${id}`)
export const createAdminDoc = (data: any) => api.post('/apehub-web/admin/docs', data)
export const updateAdminDoc = (id: number, data: any) => api.put(`/apehub-web/admin/docs/${id}`, data)
export const deleteAdminDoc = (id: number) => api.delete(`/apehub-web/admin/docs/${id}`)

export const getAdminPlugins = (params: any) => api.get('/apehub-web/admin/plugins', { params })
export const getAdminPluginDetail = (id: number) => api.get(`/apehub-web/admin/plugins/${id}`)
export const reviewPlugin = (id: number, data: any) => api.post(`/apehub-web/admin/plugins/${id}/review`, data)
export const offlinePlugin = (id: number) => api.post(`/apehub-web/admin/plugins/${id}/offline`)
export const onlinePlugin = (id: number) => api.post(`/apehub-web/admin/plugins/${id}/online`)
export const deleteAdminPlugin = (id: number) => api.delete(`/apehub-web/admin/plugins/${id}`)
export const getAdminPluginFileDownloadUrl = (pluginId: number, fileId: number) =>
  `/api/v1/apehub-web/admin/plugins/${pluginId}/files/${fileId}/download`
export const reviewPluginVersion = (pluginId: number, versionId: number, data: any) => api.post(`/apehub-web/admin/plugins/${pluginId}/versions/${versionId}/review`, data)
export const publishPluginVersion = (pluginId: number, versionId: number) => api.post(`/apehub-web/admin/plugins/${pluginId}/versions/${versionId}/publish`)
export const getAdminVersionSourceTree = (pluginId: number, versionId: number) => api.get(`/apehub-web/admin/plugins/${pluginId}/versions/${versionId}/source-tree`)
export const getAdminVersionSource = (pluginId: number, versionId: number, path: string) => api.get(`/apehub-web/admin/plugins/${pluginId}/versions/${versionId}/source`, { params: { path } })
export const refundAdminOrder = (orderId: number, data: any) => api.post(`/apehub-web/admin/orders/${orderId}/refund`, data)

export const getAdminWithdrawals = (params: any) => api.get('/apehub-web/admin/withdrawals', { params })
export const handleWithdrawal = (id: number, data: any) =>
  api.post(`/apehub-web/admin/withdrawals/${id}/handle`, data)

export const getAdminUsers = (params: any) => api.get('/apehub-web/admin/users', { params })
export const getAdminOrders = (params: any) => api.get('/apehub-web/admin/orders', { params })
export const getAdminIncomes = (params: any) => api.get('/apehub-web/admin/incomes', { params })
