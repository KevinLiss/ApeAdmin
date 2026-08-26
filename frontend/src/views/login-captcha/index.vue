<template>
  <el-card shadow="never" class="page-card">
    <template #header>登录验证码插件</template>
    <el-alert
      title="这是一个独立插件页面，用于验证接口和菜单是否能随插件实时启停。"
      type="info"
      :closable="false"
      show-icon
      class="mb-4"
    />
    <div class="captcha-row">
      <div class="captcha-code">{{ captcha?.code || '点击生成' }}</div>
      <el-button type="primary" :loading="loading" @click="generate">生成验证码</el-button>
    </div>
    <el-divider />
    <el-form inline @submit.prevent="verify">
      <el-form-item label="验证码 ID">
        <el-input v-model="captchaId" placeholder="生成后自动填充" style="width: 280px" />
      </el-form-item>
      <el-form-item label="验证码">
        <el-input v-model="code" maxlength="4" style="width: 140px" />
      </el-form-item>
      <el-form-item>
        <el-button type="success" :loading="verifying" @click="verify">校验</el-button>
      </el-form-item>
    </el-form>
    <el-result v-if="result !== null" :icon="result ? 'success' : 'error'" :title="result ? '验证码正确' : '验证码错误或已过期'" />
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const loading = ref(false)
const verifying = ref(false)
const captcha = ref<{ captcha_id: string; code: string } | null>(null)
const captchaId = ref('')
const code = ref('')
const result = ref<boolean | null>(null)

async function generate() {
  loading.value = true
  try {
    const data: any = await request.get('/login-captcha/captcha')
    captcha.value = data
    captchaId.value = data.captcha_id
    code.value = data.code
    result.value = null
  } finally {
    loading.value = false
  }
}

async function verify() {
  if (!captchaId.value || !code.value) return ElMessage.warning('请先生成并填写验证码')
  verifying.value = true
  try {
    const data: any = await request.post('/login-captcha/verify', { captcha_id: captchaId.value, code: code.value })
    result.value = Boolean(data.valid)
  } finally {
    verifying.value = false
  }
}
</script>

<style scoped>
.captcha-row { display: flex; align-items: center; gap: 16px; }
.captcha-code { min-width: 160px; padding: 14px 20px; border: 1px dashed var(--el-color-primary); border-radius: 6px; color: var(--el-color-primary); font-size: 24px; font-weight: 700; letter-spacing: 4px; text-align: center; }
.mb-4 { margin-bottom: 16px; }
</style>
