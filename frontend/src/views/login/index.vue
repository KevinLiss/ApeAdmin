<template>
  <!-- ApeAdmin 登录页 -->
  <div class="login-card" :style="loginBgStyle">
    <div>
      <div class="login-logo">
        <img v-if="settingsStore.logo_url" :src="settingsStore.logo_url" alt="Logo" class="login-logo-icon" />
        <img v-else src="/assets/images/logo-icon.png" alt="Logo" class="login-logo-icon" />
        <span class="login-logo-text">{{ settingsStore.site_name }}</span>
      </div>
      <div class="login-main">
        <form class="theme-form" @submit.prevent="handleLogin">
          <h2 class="text-center">登录</h2>
          <p class="text-center">请输入账号和密码登录</p>

          <div class="form-group">
            <label class="col-form-label">账号</label>
            <input class="form-control" type="text" v-model="form.username" placeholder="admin" required />
          </div>

          <div class="form-group">
            <label class="col-form-label">密码</label>
            <div class="form-input position-relative">
              <input class="form-control" type="password" v-model="form.password" placeholder="*********" required />
              <div class="show-hide" @click="togglePwd"><span class="show"></span></div>
            </div>
          </div>

          <div class="form-group mb-0">
            <div class="checkbox p-0">
              <input id="checkbox1" type="checkbox" v-model="remember" />
              <label class="text-muted" for="checkbox1">记住密码</label>
            </div>
            <a class="link" href="javascript:void(0)">忘记密码？</a>
            <div class="text-end mt-3">
              <button class="btn btn-primary btn-block w-100" type="submit" :disabled="loading">
                {{ loading ? '登录中...' : '登 录' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'
import { getPublicSettings } from '@/api'

const router = useRouter()
const userStore = useUserStore()
const settingsStore = useSettingsStore()

const loading = ref(false)
const remember = ref(true)
const pwdType = ref<'password' | 'text'>('password')

// 登录页背景：后台品牌定制里配置的 login_bg（可自定义 CSS 值或图片 URL）
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

// 登录页在布局之外、可能直接刷新进入，需自行拉取公开设置（主题色/品牌）
onMounted(async () => {
  if (!settingsStore.loaded) {
    await settingsStore.fetchPublicSettings()
  }
  settingsStore.applyThemeColor()
})

const form = reactive({
  username: 'admin',
  password: '',
})

function togglePwd() {
  pwdType.value = pwdType.value === 'password' ? 'text' : 'password'
}

async function handleLogin() {
  if (loading.value) return
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard-monitor')
  } catch (e: any) {
    // Error message already shown by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ===== ApeAdmin Login ===== */
.login-card {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  background: var(--el-color-primary-light-9, rgba(90, 103, 245, 0.14));
  background-position: center;
  padding: 30px 12px;
}
.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
}
.login-logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
}
.login-logo-text {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-color-primary, #2b2b2b);
  letter-spacing: 0.5px;
}

/* 自定义背景图时登录卡片略增投影，保证可读性 */
.login-card[style*="url"] .login-main {
  box-shadow: 0 8px 40px rgba(8, 21, 66, 0.16);
}
.login-card .login-main {
  width: 450px;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 0 37px rgba(8, 21, 66, 0.05);
  margin: 0 auto;
  background-color: #ffffff;
}
.login-card .login-main .theme-form h2 {
  margin: 0 0 5px;
  font-size: 24px;
  font-weight: 600;
  color: #2b2b2b;
}
.login-card .login-main .theme-form p {
  margin-bottom: 25px;
  font-size: 14px;
  color: #898989;
}
.login-card .login-main .theme-form label {
  font-size: 15px;
  letter-spacing: 0.4px;
  color: #2b2b2b;
}
.login-card .login-main .theme-form .form-group {
  margin-bottom: 10px;
  position: relative;
}
.login-card .login-main .theme-form input.form-control {
  width: 100%;
  height: 46px;
  padding: 6px 12px;
  font-size: 14px;
  color: #2b2b2b;
  background-color: #fff;
  border: 1px solid #eff3f9;
  border-radius: 4px;
  outline: none;
  transition: all 0.3s ease;
}
.login-card .login-main .theme-form input.form-control::-webkit-input-placeholder {
  color: #9993b4;
}
.login-card .login-main .theme-form input.form-control:hover,
.login-card .login-main .theme-form input.form-control:focus {
  box-shadow: none !important;
  border-color: var(--el-color-primary, #5A67F5);
  transition: all 0.3s ease;
}
.login-card .login-main .theme-form .form-input .show-hide {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
}
.login-card .login-main .theme-form .checkbox label::before {
  background-color: #f9f9fa;
  border: 1px solid var(--el-color-primary-light-7, rgba(90, 103, 245, 0.1));
}
.login-card .login-main .theme-form .checkbox {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.login-card .login-main .theme-form .link {
  position: absolute;
  top: 10px;
  right: 0;
  color: var(--el-color-primary, #5A67F5);
  text-decoration: none;
}
.login-card .login-main .theme-form .btn-primary {
  display: inline-block;
  height: 46px;
  border: none;
  border-radius: 4px;
  background-color: var(--el-color-primary, #5A67F5);
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.login-card .login-main .theme-form .btn-primary:hover {
  background-color: var(--el-color-primary-dark-2, #4755E6);
}
.login-card .login-main .theme-form .btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.login-card .login-main .theme-form .text-center {
  text-align: center;
}
.login-card .login-main .theme-form .text-end {
  text-align: right;
}
.login-card .login-main .theme-form .mt-3 {
  margin-top: 1rem;
}
.login-card .login-main .theme-form .mb-0 {
  margin-bottom: 0;
}
.login-card .login-main .theme-form .w-100 {
  width: 100%;
}
</style>
