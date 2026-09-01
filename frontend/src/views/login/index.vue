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

          <div v-if="captchaEnabled" class="form-group">
            <label class="col-form-label">验证码</label>
            <div class="captcha-input-row">
              <input class="form-control" type="text" v-model="form.captcha_code" maxlength="4" placeholder="请输入验证码" required />
              <button class="captcha-image" type="button" @click="loadCaptcha" :disabled="captchaLoading">
                <img v-if="captchaImage" :src="captchaImage" alt="验证码" style="height: 100%; border: none; cursor: pointer; border-radius: 4px;" />
                <span v-else>----</span>
              </button>
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const remember = ref(true)
const pwdType = ref<'password' | 'text'>('password')

const form = reactive({
  username: 'admin',
  password: '',
  captcha_code: '',
})
const captchaId = ref('')
const captchaImage = ref('')
const captchaEnabled = ref(false)
const captchaLoading = ref(false)

async function loadCaptcha() {
  captchaLoading.value = true
  try {
    const response = await fetch('/api/v1/login-captcha/captcha')
    if (!response.ok) throw new Error('captcha plugin unavailable')
    const envelope: any = await response.json()
    const data = envelope.data
    captchaEnabled.value = true
    captchaId.value = data.captcha_id
    captchaImage.value = data.image
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
