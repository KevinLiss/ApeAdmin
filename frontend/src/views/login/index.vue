<template>
  <!-- ApeAdmin 登录页 -->
  <div class="login-page" :style="loginBgStyle">
    <div class="login-container">
      <!-- 左侧品牌展示区 -->
      <div class="login-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <img v-if="settingsStore.logo_url" :src="settingsStore.logo_url" alt="Logo" class="brand-logo-icon" />
            <img v-else src="/assets/images/logo-icon.png" alt="Logo" class="brand-logo-icon" />
            <span class="brand-logo-text">{{ settingsStore.site_name }}</span>
          </div>
          <h1 class="brand-title">欢迎使用</h1>
          <p class="brand-subtitle">{{ settingsStore.site_name || 'ApeAdmin' }} 管理后台</p>
          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-dot"></div>
              <span>权限管理</span>
            </div>
            <div class="feature-item">
              <div class="feature-dot"></div>
              <span>插件生态</span>
            </div>
            <div class="feature-item">
              <div class="feature-dot"></div>
              <span>AI 助手</span>
            </div>
            <div class="feature-item">
              <div class="feature-dot"></div>
              <span>MCP 集成</span>
            </div>
          </div>
        </div>
        <div class="brand-footer">
          <p>© 2026 {{ settingsStore.site_name || 'ApeAdmin' }}. All rights reserved.</p>
        </div>
      </div>

      <!-- 右侧登录表单区 -->
      <div class="login-form-wrapper">
        <div class="login-form-card">
          <div class="form-header">
            <h2>账号登录</h2>
            <p>请输入您的账号和密码</p>
          </div>

          <form class="login-form" @submit.prevent="handleLogin">
            <!-- 用户名 -->
            <div class="input-group" :class="{ 'has-error': errors.username }">
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </div>
                <input
                  v-model.trim="form.username"
                  type="text"
                  placeholder="请输入用户名"
                  :class="['form-input', { error: errors.username }]"
                  @input="errors.username = ''"
                  @keyup.enter="focusPassword"
                />
              </div>
              <transition name="slide-down">
                <span v-if="errors.username" class="input-error-msg">{{ errors.username }}</span>
              </transition>
            </div>

            <!-- 密码 -->
            <div class="input-group" :class="{ 'has-error': errors.password }">
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                </div>
                <input
                  ref="passwordRef"
                  v-model.trim="form.password"
                  :type="pwdVisible ? 'text' : 'password'"
                  placeholder="请输入密码"
                  :class="['form-input', { error: errors.password }]"
                  @input="errors.password = ''"
                  @keyup.enter="handleLogin"
                />
                <div class="input-action" @click="pwdVisible = !pwdVisible">
                  <svg v-if="!pwdVisible" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                </div>
              </div>
              <transition name="slide-down">
                <span v-if="errors.password" class="input-error-msg">{{ errors.password }}</span>
              </transition>
            </div>

            <!-- 滑块验证码 -->
            <div class="captcha-section">
            <Verify
              :key="captchaKey"
              type="slide"
              :width="310"
              :height="40"
              :theme="captchaTheme"
              @success="onCaptchaSuccess"
              @error="onCaptchaError"
            />
            </div>

            <!-- 记住密码 & 忘记密码 -->
            <div class="form-options">
              <label class="remember-me">
                <input type="checkbox" v-model="remember" />
                <span>记住密码</span>
              </label>
              <a class="forgot-link" @click="handleForgotPassword">忘记密码？</a>
            </div>

            <!-- 登录按钮 -->
            <button
              type="submit"
              class="login-btn"
              :class="{ ready: captchaPassed && !loading }"
              :disabled="loading || !captchaPassed"
            >
              <span v-if="loading" class="btn-loading">
                <span class="loading-spinner"></span>
                登录中...
              </span>
              <span v-else-if="!captchaPassed">请先完成验证</span>
              <span v-else>登 录</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElNotification } from 'element-plus'
import { Verify } from 'vue3-verify'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { getPublicSettings } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const settingsStore = useSettingsStore()

const loading = ref(false)
const remember = ref(true)
const pwdVisible = ref(false)
const captchaPassed = ref(false)
const passwordRef = ref<HTMLInputElement | null>(null)

const form = reactive({
  username: remember.value ? localStorage.getItem('apeadmin_remember_user') || 'admin' : 'admin',
  password: remember.value ? localStorage.getItem('apeadmin_remember_pwd') || '' : '',
})

const errors = reactive({
  username: '',
  password: '',
})

// 验证码主题色跟随品牌色
const captchaTheme = computed(() => ({
  primaryColor: settingsStore.primary_color || '#5A67F5',
  successColor: '#67c23a',
  errorColor: '#f56c6c',
  borderRadius: '6px',
}))

// 登录页背景
const loginBgStyle = computed(() => {
  if (settingsStore.login_bg) {
    const v = settingsStore.login_bg
    if (v.startsWith('http') || v.startsWith('/')) {
      return { background: `url(${v}) center/cover no-repeat` }
    }
    return { background: v }
  }
  return {}
})

onMounted(async () => {
  if (!settingsStore.loaded) {
    await settingsStore.fetchPublicSettings()
  }
  settingsStore.applyThemeColor()
})

// 验证码通过
function onCaptchaSuccess() {
  captchaPassed.value = true
  ElNotification({
    title: '验证成功',
    message: '请点击登录按钮继续',
    type: 'success',
    duration: 2000,
  })
}

// 验证码失败
function onCaptchaError() {
  captchaPassed.value = false
}

// 聚焦密码框
function focusPassword() {
  passwordRef.value?.focus()
}

// 表单校验
function validateForm(): boolean {
  let valid = true
  if (!form.username) {
    errors.username = '请输入用户名'
    valid = false
  }
  if (!form.password) {
    errors.password = '请输入密码'
    valid = false
  }
  if (!captchaPassed.value) {
    ElNotification({
      title: '请先验证',
      message: '请完成滑块验证后再登录',
      type: 'warning',
      duration: 2500,
    })
    valid = false
  }
  return valid
}

// 登录
async function handleLogin() {
  if (loading.value) return
  if (!validateForm()) return

  loading.value = true
  try {
    await userStore.login(form.username, form.password)

    // 记住密码
    if (remember.value) {
      localStorage.setItem('apeadmin_remember_user', form.username)
      localStorage.setItem('apeadmin_remember_pwd', form.password)
    } else {
      localStorage.removeItem('apeadmin_remember_user')
      localStorage.removeItem('apeadmin_remember_pwd')
    }

    ElNotification({
      title: '登录成功',
      message: `欢迎回来，${userStore.nickname || form.username}！`,
      type: 'success',
      duration: 2000,
    })

    // 延迟跳转，确保弹窗能被看到
    setTimeout(() => {
      router.push('/dashboard-monitor')
    }, 500)
  } catch (e: any) {
    // 从 axios 错误中提取后端返回的错误信息
    const msg = e?.response?.data?.msg || e?.message || '登录失败，请检查用户名和密码'
    ElNotification({
      title: '登录失败',
      message: msg,
      type: 'error',
      duration: 3500,
    })
    // 验证码重置
    captchaPassed.value = false
    // 刷新验证码组件（通过 key 重新挂载）
    captchaKey.value++
  } finally {
    loading.value = false
  }
}

// 忘记密码提示
function handleForgotPassword() {
  ElNotification({
    title: '忘记密码',
    message: '请联系系统管理员重置密码',
    type: 'info',
    duration: 3000,
  })
}

// 验证码刷新 key
const captchaKey = ref(0)
</script>

<style scoped>
/* ===== ApeAdmin Login Page ===== */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  display: flex;
  width: 880px;
  max-width: 100%;
  min-height: 480px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  background: #fff;
}

/* ===== 左侧品牌区 ===== */
.login-brand {
  flex: 0 0 42%;
  background: linear-gradient(135deg, var(--el-color-primary, #5A67F5) 0%, var(--el-color-primary-dark-2, #4755E6) 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px 36px;
  position: relative;
  overflow: hidden;
}

.login-brand::before {
  content: '';
  position: absolute;
  top: -60px;
  right: -60px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.login-brand::after {
  content: '';
  position: absolute;
  bottom: -40px;
  left: -40px;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.brand-content {
  position: relative;
  z-index: 1;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 60px;
}

.brand-logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
}

.brand-logo-text {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.brand-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px;
}

.brand-subtitle {
  font-size: 15px;
  opacity: 0.85;
  margin: 0 0 40px;
}

.brand-features {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.9;
}

.feature-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
}

.brand-footer {
  position: relative;
  z-index: 1;
  font-size: 12px;
  opacity: 0.5;
}

.brand-footer p {
  margin: 0;
}

/* ===== 右侧登录表单区 ===== */
.login-form-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-form-card {
  width: 100%;
  max-width: 360px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px;
}

.form-header p {
  font-size: 14px;
  color: #8a8a9a;
  margin: 0;
}

/* ===== 输入框组 ===== */
.input-group {
  margin-bottom: 20px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 12px;
  display: flex;
  align-items: center;
  color: #b0b0c0;
  pointer-events: none;
  z-index: 1;
}

.input-action {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  color: #b0b0c0;
  cursor: pointer;
  z-index: 1;
  transition: color 0.2s;
}

.input-action:hover {
  color: var(--el-color-primary, #5A67F5);
}

.form-input {
  width: 100%;
  height: 46px;
  padding: 0 40px;
  font-size: 14px;
  color: #1a1a2e;
  background: #f8f9fc;
  border: 2px solid transparent;
  border-radius: 8px;
  outline: none;
  transition: all 0.25s ease;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: #b0b0c0;
}

.form-input:hover {
  background: #f0f1f8;
}

.form-input:focus {
  background: #fff;
  border-color: var(--el-color-primary, #5A67F5);
  box-shadow: 0 0 0 3px rgba(var(--el-color-primary-rgb, 90, 103, 245), 0.1);
}

.form-input.error {
  border-color: #f56c6c;
  background: #fef0f0;
}

.has-error .input-icon {
  color: #f56c6c;
}

.input-error-msg {
  display: block;
  margin-top: 6px;
  padding-left: 4px;
  font-size: 12px;
  color: #f56c6c;
}

/* ===== 验证码区 ===== */
.captcha-section {
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
}

.captcha-section :deep(.verify-container) {
  border-radius: 6px;
  overflow: hidden;
}

/* ===== 选项行 ===== */
.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #8a8a9a;
  cursor: pointer;
  user-select: none;
}

.remember-me input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--el-color-primary, #5A67F5);
  cursor: pointer;
}

.forgot-link {
  font-size: 14px;
  color: var(--el-color-primary, #5A67F5);
  text-decoration: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.forgot-link:hover {
  opacity: 0.8;
}

/* ===== 登录按钮 ===== */
.login-btn {
  width: 100%;
  height: 46px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #d0d0e0;
  color: #fff;
}

.login-btn.ready {
  background: var(--el-color-primary, #5A67F5);
  box-shadow: 0 4px 12px rgba(var(--el-color-primary-rgb, 90, 103, 245), 0.3);
}

.login-btn.ready:hover {
  background: var(--el-color-primary-dark-2, #4755E6);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(var(--el-color-primary-rgb, 90, 103, 245), 0.4);
}

.login-btn.ready:active {
  transform: translateY(0);
}

.login-btn:disabled {
  cursor: not-allowed;
}

/* ===== Loading 动画 ===== */
.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== 过渡动画 ===== */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-4px);
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  max-height: 20px;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    width: 100%;
    max-width: 420px;
  }

  .login-brand {
    flex: none;
    padding: 28px 24px;
  }

  .brand-logo {
    margin-bottom: 20px;
  }

  .brand-title {
    font-size: 22px;
  }

  .brand-subtitle {
    margin-bottom: 20px;
  }

  .brand-features {
    gap: 10px 18px;
    margin-bottom: 0;
  }

  .login-form-wrapper {
    padding: 28px 24px;
  }
}

/* 自定义背景图时加遮罩保证可读性 */
.login-page[style*="url"] .login-container {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}
</style>
