<template>
  <el-card shadow="never">
    <template #header>
      <div class="card-header">
        <span>官网配置</span>
      </div>
    </template>

    <el-tabs v-model="activeTab">
      <!-- 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <el-form :model="form" label-width="140px" style="max-width: 600px" v-loading="loading">
          <el-form-item label="站点名称">
            <el-input v-model="form.site_name" placeholder="ApeHub" />
          </el-form-item>
          <el-form-item label="站点域名">
            <el-input v-model="form.site_domain" placeholder="apehub.cn" />
          </el-form-item>
          <el-form-item label="入口前缀">
            <el-input v-model="form.site_prefix" placeholder="/site" />
            <div class="form-hint">官网路由前缀，默认 /site，必须以 / 开头</div>
          </el-form-item>
          <el-form-item label="SEO 标题">
            <el-input v-model="form.seo_title" placeholder="ApeHub - ApeAdmin 插件市场" />
          </el-form-item>
          <el-form-item label="SEO 描述">
            <el-input v-model="form.seo_description" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item label="SEO 关键词">
            <el-input v-model="form.seo_keywords" placeholder="逗号分隔" />
          </el-form-item>
          <el-form-item label="默认服务费率">
            <el-input-number v-model="form.service_fee_rate" :precision="1" :min="0" :max="100" />
            <span class="form-hint">%</span>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 邮件配置 -->
      <el-tab-pane label="邮件配置" name="mail">
        <el-form :model="form" label-width="140px" style="max-width: 600px" v-loading="loading">
          <el-form-item label="发信邮箱">
            <el-input v-model="form.mail_user" placeholder="xxx@qq.com" />
          </el-form-item>
          <el-form-item label="邮箱授权码">
            <el-input v-model="form.mail_code" type="password" show-password placeholder="SMTP 授权码" />
          </el-form-item>
          <el-form-item label="SMTP 主机">
            <el-input v-model="form.mail_host" placeholder="smtp.qq.com" />
          </el-form-item>
          <el-form-item label="SMTP 端口">
            <el-input-number v-model="form.mail_port" :min="1" :max="65535" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 支付配置 -->
      <el-tab-pane label="支付配置" name="lempay">
        <el-form :model="form" label-width="140px" style="max-width: 600px" v-loading="loading">
          <el-form-item label="LemPay 商户ID">
            <el-input-number v-model="form.lempay_pid" :min="0" />
          </el-form-item>
          <el-form-item label="LemPay 密钥">
            <el-input v-model="form.lempay_key" type="password" show-password />
          </el-form-item>
          <el-form-item label="API 查询地址">
            <el-input v-model="form.lempay_api_url" placeholder="https://api.lempay.com" />
          </el-form-item>
          <el-form-item label="支付提交地址">
            <el-input v-model="form.lempay_submit_url" placeholder="https://api.lempay.com/submit" />
          </el-form-item>
          <el-form-item label="异步通知地址">
            <el-input v-model="form.lempay_notify_url" placeholder="https://your-domain/api/v1/apehub-web/notify" />
          </el-form-item>
          <el-form-item label="同步跳转地址">
            <el-input v-model="form.lempay_return_url" placeholder="https://your-domain/site/plugins" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAdminConfig, updateAdminConfig } from '@/api/apehub_web'

const activeTab = ref('basic')
const loading = ref(false)
const saving = ref(false)

const form = ref<any>({
  site_name: '', site_domain: '', site_prefix: '/site',
  seo_title: '', seo_description: '', seo_keywords: '',
  service_fee_rate: 30,
  mail_user: '', mail_code: '', mail_host: '', mail_port: 465,
  lempay_pid: 0, lempay_key: '', lempay_api_url: '',
  lempay_submit_url: '', lempay_notify_url: '', lempay_return_url: '',
})

const loadConfig = async () => {
  loading.value = true
  try {
    const data = await getAdminConfig()
    form.value = { ...form.value, ...data }
  } finally { loading.value = false }
}

const handleSave = async () => {
  saving.value = true
  try {
    await updateAdminConfig(form.value)
    ElMessage.success('配置已保存')
  } finally { saving.value = false }
}

onMounted(loadConfig)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.form-hint { font-size: 12px; color: #909399; margin-left: 8px; }
</style>
