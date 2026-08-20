import axios from 'axios'
import { ElMessage } from 'element-plus'

// Create axios instance
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// Request interceptor: attach token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('apeadmin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
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
      ElMessage.error('登录已过期，请重新登录')
      window.location.href = '/login'
    } else {
      const msg = error.response?.data?.msg || error.message || '网络错误'
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  }
)

export default request