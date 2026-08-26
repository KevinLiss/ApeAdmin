<template>
  <!-- ApeAdmin 1:1 登录页 -->
  <div class="login-card">
    <div>
      <div class="login-logo">
        <img src="/assets/images/logo-icon.png" alt="Logo" class="login-logo-icon" />
        <span class="login-logo-text">ApeAdmin</span>
      </div>
      <div class="login-main">
        <form class="theme-form" @submit.prevent="handleLogin">
          <h2 class="text-center">Sign in to account</h2>
          <p class="text-center">Enter your email &amp; password to login</p>

          <div class="form-group">
            <label class="col-form-label">Username</label>
            <input class="form-control" type="text" v-model="form.username" placeholder="admin" required />
          </div>

          <div class="form-group">
            <label class="col-form-label">Password</label>
            <div class="form-input position-relative">
              <input class="form-control" type="password" v-model="form.password" placeholder="*********" required />
              <div class="show-hide" @click="togglePwd"><span class="show"></span></div>
            </div>
          </div>

          <div v-if="captchaEnabled" class="form-group">
            <label class="col-form-label">Captcha</label>
            <div class="captcha-input-row">
              <input class="form-control" type="text" v-model="form.captcha_code" maxlength="4" placeholder="Enter captcha" required />
              <button class="captcha-image" type="button" @click="loadCaptcha" :disabled="captchaLoading">{{ captchaCode || '----' }}</button>
            </div>
          </div>

          <div class="form-group mb-0">
            <div class="checkbox p-0">
              <input id="checkbox1" type="checkbox" v-model="remember" />
              <label class="text-muted" for="checkbox1">Remember password</label>
            </div>
            <a class="link" href="javascript:void(0)">Forgot password?</a>
            <div class="text-end mt-3">
              <button class="btn btn-primary btn-block w-100" type="submit" :disabled="loading">
                {{ loading ? 'Signing in...' : 'Sign in' }}
              </button>
            </div>
          </div>

          <div class="login-social-title">
            <h3>Or Sign in with</h3>
          </div>
          <div class="form-group">
            <ul class="login-social">
              <li>
                <a href="javascript:void(0)" aria-label="Facebook">
                  <svg viewBox="0 0 320 512" width="16" height="16" fill="currentColor"><path d="M279.14 288l14.22-92.66h-88.91v-60.13c0-25.35 12.42-50.06 52.24-50.06h40.42V6.26S260.43 0 225.36 0c-73.22 0-121.08 44.38-121.08 124.72v70.62H22.89V288h81.39v224h100.17V288z"/></svg>
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" aria-label="LinkedIn">
                  <svg viewBox="0 0 448 512" width="16" height="16" fill="currentColor"><path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"/></svg>
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" aria-label="Twitter">
                  <svg viewBox="0 0 512 512" width="16" height="16" fill="currentColor"><path d="M459.37 151.716c.325 4.548.325 9.097.325 13.645 0 138.72-105.583 298.558-298.558 298.558-59.452 0-114.68-17.219-161.137-47.106 8.447.974 16.568 1.299 25.34 1.299 49.055 0 94.213-16.568 130.274-44.832-46.132-.975-84.792-31.188-98.112-72.772 6.498.974 12.995 1.624 19.818 1.624 9.421 0 18.843-1.3 27.614-3.573-48.081-9.747-84.408-52.315-84.408-104.226v-1.607c9.421 6.49 24.588 11.364 38.664 11.364-6.568-4.457-17.095-13.544-22.107-21.419-14.617-22.524-10.563-54.287 3.381-73.552 29.365 44.479 82.009 73.729 137.389 76.792-1.866-3.515-2.953-7.04-2.953-10.796 0-25.731 20.868-46.601 46.603-46.601 13.69 0 25.358 5.588 33.79 14.415 9.194-1.801 18.108-5.182 27.07-10.019-3.219 9.944-9.983 18.183-18.426 23.314 8.559-1.146 16.568-3.033 24.114-6.012-5.669 8.713-13.461 15.187-22.001 21.46-1.462 2.233-2.196 4.608-2.196 6.982v32.07c0 6.983-.455 13.295-1.135 20.055C436.855 312.283 509.49 242.76 509.49 149.92 493.7 162.121 473.51 171.621 451.9 175.304z"/></svg>
                </a>
              </li>
              <li>
                <a href="javascript:void(0)" aria-label="Instagram">
                  <svg viewBox="0 0 448 512" width="16" height="16" fill="currentColor"><path d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.4-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.4 9 132.1s2.7 102.7-9 132.1z"/></svg>
                </a>
              </li>
            </ul>
          </div>

          <p class="mt-4 mb-0 text-center">
            ApeAdmin 默认账号: admin / admin123
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getLoginCaptcha } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const remember = ref(true)
const pwdType = ref<'password' | 'text'>('password')

const form = reactive({
  username: 'admin',
  password: 'admin123',
  captcha_code: '',
})
const captchaId = ref('')
const captchaCode = ref('')
const captchaEnabled = ref(false)
const captchaLoading = ref(false)

async function loadCaptcha() {
  captchaLoading.value = true
  try {
    const data: any = await getLoginCaptcha()
    captchaEnabled.value = true
    captchaId.value = data.captcha_id
    captchaCode.value = data.code
  } catch {
    captchaEnabled.value = false
  } finally {
    captchaLoading.value = false
  }
}

loadCaptcha()

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
    await userStore.login(form.username, form.password, captchaEnabled.value ? { captcha_id: captchaId.value, captcha_code: form.captcha_code } : undefined)
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
/* ===== ApeAdmin 1:1 Login ===== */
.login-card {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  background: rgba(90, 103, 245, 0.14);
  background-position: center;
  padding: 30px 12px;
}
.captcha-input-row { display: flex; gap: 10px; }
.captcha-image { width: 110px; border: 1px solid #eff3f9; border-radius: 4px; background: #f4f6ff; color: #5A67F5; font-size: 18px; letter-spacing: 3px; cursor: pointer; }
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
  color: #2b2b2b;
  letter-spacing: 0.5px;
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
  border-color: #5A67F5;
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
  border: 1px solid rgba(90, 103, 245, 0.1);
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
  color: #5A67F5;
  text-decoration: none;
}
.login-card .login-main .theme-form .login-social-title {
  position: relative;
  z-index: 1;
  text-align: center;
  margin-top: 30px;
  margin-bottom: 30px;
}
.login-card .login-main .theme-form .login-social-title h3 {
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
  color: #9993b4;
  background-color: #ffffff;
  padding-left: 25px;
  padding-right: 25px;
  font-size: 15px;
  font-weight: 500;
}
.login-card .login-main .theme-form .login-social-title:before {
  content: "";
  position: absolute;
  width: 100%;
  height: 2px;
  background-color: rgba(90, 103, 245, 0.1);
  top: 10px;
  z-index: -1;
  right: 0;
}
.login-card .login-main .theme-form ul.login-social {
  display: flex;
  align-items: center;
  justify-content: center;
  list-style: none;
  padding: 0;
  margin: 0;
}
.login-card .login-main .theme-form ul.login-social li {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(90, 103, 245, 0.1);
  background-color: rgba(90, 103, 245, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-card .login-main .theme-form ul.login-social li a {
  width: auto;
  color: #5A67F5;
  font-size: 15px;
}
.login-card .login-main .theme-form ul.login-social li:nth-child(n + 2) {
  margin-left: 15px;
}
.login-card .login-main .theme-form ul.login-social li:hover {
  background-color: #5A67F5;
}
.login-card .login-main .theme-form ul.login-social li:hover a {
  color: #fff;
}
.login-card .login-main .theme-form .btn-primary {
  display: inline-block;
  height: 46px;
  border: none;
  border-radius: 4px;
  background-color: #5A67F5;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}
.login-card .login-main .theme-form .btn-primary:hover {
  background-color: #4755E6;
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
.login-card .login-main .theme-form .mt-4 {
  margin-top: 1.5rem;
}
.login-card .login-main .theme-form .mb-0 {
  margin-bottom: 0;
}
.login-card .login-main .theme-form .w-100 {
  width: 100%;
}
</style>
