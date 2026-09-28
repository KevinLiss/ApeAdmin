import axios from 'axios'
import { ElMessage } from 'element-plus'

// Create axios instance
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// Request interceptor: attach token + Accept-Language header
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('apeadmin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Attach locale for backend message i18n
    const locale = localStorage.getItem('locale') || 'zh-CN'
    config.headers['Accept-Language'] = locale
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle standard envelope { code, msg, data }
request.interceptors.response.use(
  (response) => {
    const res = response.data
    // Standard envelope: code=200 means success
    if (res && typeof res === 'object' && 'code' in res) {
      if (res.code === 200) {
        return res.data
      }
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(new Error(res.msg || '请求失败'))
    }
    return res
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('apeadmin_token')
      // 如果已在登录页，不跳转也不弹消息，由调用方（如 handleLogin）处理错误提示
      if (!window.location.pathname.includes('/login')) {
        ElMessage.error('登录已过期，请重新登录')
        // 保留当前 admin_path 前缀（可能被用户修改过，不是默认 /admin）
        const currentPath = window.location.pathname
        const loginPath = currentPath.replace(/\/[^/]*$/, '/login') || '/admin/login'
        window.location.href = loginPath
      }
    } else {
      const msg = error.response?.data?.msg || error.message || '网络错误'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request