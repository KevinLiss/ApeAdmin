<template>
  <el-card shadow="never">
    <template #header><div class="card-header"><span>官网配置</span></div></template>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="basic">
        <el-form :model="form" label-width="120px" class="form-width" v-loading="loading">
          <el-form-item label="站点名称"><el-input v-model="form.site_name" /></el-form-item>
          <el-form-item label="站点域名"><el-input v-model="form.site_domain" placeholder="apehub.example.com" /></el-form-item>
          <el-form-item label="入口前缀"><el-input v-model="form.site_prefix" placeholder="/apehub-web" /></el-form-item>
          <el-form-item label="SEO 标题"><el-input v-model="form.seo_title" /></el-form-item>
          <el-form-item label="SEO 描述"><el-input v-model="form.seo_description" type="textarea" :rows="2" /></el-form-item>
          <el-form-item label="SEO 关键词"><el-input v-model="form.seo_keywords" /></el-form-item>
          <el-form-item label="官网默认主题">
            <el-radio-group v-model="form.theme_mode">
              <el-radio value="light">浅色</el-radio>
              <el-radio value="dark">深色</el-radio>
            </el-radio-group>
            <div class="field-tip">官网访问者首次打开时的默认主题，访问者可在页面上手动切换（仅影响当前浏览器）。</div>
          </el-form-item>
          <el-form-item label="服务费率"><el-input-number v-model="form.service_fee_rate" :precision="1" :min="0" :max="100" />%</el-form-item>
          <el-form-item><el-button type="primary" :loading="saving" @click="saveConfig">保存配置</el-button></el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="图片与图标" name="assets">
        <el-alert title="默认 Logo 和首页图片来自插件内置资源。上传新图片后保存即可替换，未上传字段继续使用默认图片。" type="info" :closable="false" show-icon class="asset-tip" />
        <el-form :model="form" label-width="120px" class="form-width" v-loading="loading">
          <el-form-item label="站点 Logo"><AssetField v-model="form.site_logo" /></el-form-item>
          <el-form-item label="浏览器图标"><AssetField v-model="form.site_icon" /></el-form-item>
          <el-form-item label="首页图片"><AssetField v-model="heroImage" /></el-form-item>
          <el-form-item><el-button type="primary" :loading="saving" @click="saveAssets">保存图片设置</el-button></el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="导航菜单" name="navigation">
        <div class="toolbar"><el-button type="primary" @click="openNavDialog()">新增导航</el-button></div>
        <el-table :data="navigation" v-loading="navLoading" stripe>
          <el-table-column prop="sort" label="排序" width="72" />
          <el-table-column prop="title" label="名称" width="140" />
          <el-table-column label="图标" width="86"><template #default="{ row }"><el-image v-if="row.icon_url" :src="row.icon_url" class="nav-icon" fit="contain" /><span v-else>无</span></template></el-table-column>
          <el-table-column prop="link" label="链接" min-width="280" show-overflow-tooltip />
          <el-table-column label="打开方式" width="100"><template #default="{ row }">{{ row.open_mode === 'new' ? '新窗口' : '当前页' }}</template></el-table-column>
          <el-table-column label="状态" width="90"><template #default="{ row }"><el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '停用' }}</el-tag></template></el-table-column>
          <el-table-column label="操作" width="150"><template #default="{ row }"><el-button text type="primary" @click="openNavDialog(row)">编辑</el-button><el-button text type="danger" @click="removeNavigation(row)">删除</el-button></template></el-table-column>
          <template #empty><el-empty description="暂无导航项" /></template>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="邮件配置" name="mail">
        <el-form :model="form" label-width="120px" class="form-width" v-loading="loading">
          <el-form-item label="发信邮箱"><el-input v-model="form.mail_user" placeholder="xxx@qq.com" /></el-form-item>
          <el-form-item label="邮箱授权码"><el-input v-model="form.mail_code" type="password" show-password placeholder="留空则保持原授权码" /></el-form-item>
          <el-form-item label="SMTP 主机"><el-input v-model="form.mail_host" /></el-form-item>
          <el-form-item label="SMTP 端口"><el-input-number v-model="form.mail_port" :min="1" :max="65535" /></el-form-item>
          <el-form-item><el-button type="primary" :loading="saving" @click="saveConfig">保存配置</el-button></el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="支付与结算" name="payment">
        <el-alert :title="form.lempay_configured ? 'LemPay 密钥已配置' : 'LemPay 密钥尚未配置'" :type="form.lempay_configured ? 'success' : 'warning'" :closable="false" show-icon class="asset-tip" />
        <el-form :model="form" label-width="140px" class="form-wide" v-loading="loading">
          <div class="form-grid">
            <el-form-item label="计价币种"><el-input model-value="USDT" disabled /></el-form-item>
            <el-form-item label="支付方式"><el-input model-value="USDT" disabled /></el-form-item>
            <el-form-item label="商户 ID"><el-input-number v-model="form.lempay_pid" :min="0" controls-position="right" /></el-form-item>
            <el-form-item label="商户密钥"><el-input v-model="form.lempay_key" type="password" show-password :placeholder="form.lempay_configured ? '已配置，留空保持不变' : '请输入商户密钥'" /></el-form-item>
            <el-form-item label="支付提交地址"><el-input v-model="form.lempay_submit_url" placeholder="https://.../submit.php" /></el-form-item>
            <el-form-item label="商户 API 地址"><el-input v-model="form.lempay_api_url" placeholder="https://.../api.php" /></el-form-item>
            <el-form-item label="异步通知地址"><el-input v-model="form.lempay_notify_url" placeholder="https://your-domain/api/v1/apehub-web/notify" /></el-form-item>
            <el-form-item label="支付返回地址"><el-input v-model="form.lempay_return_url" placeholder="https://your-domain/apehub-web/profile.html" /></el-form-item>
            <el-form-item label="默认服务费"><el-input-number v-model="form.service_fee_rate" :precision="2" :min="0" :max="100" />%</el-form-item>
            <el-form-item label="收益结算期"><el-input-number v-model="form.settlement_days" :min="0" :max="365" /> 天</el-form-item>
            <el-form-item label="退款期限"><el-input-number v-model="form.refund_days" :min="0" :max="365" /> 天</el-form-item>
            <el-form-item label="最低提现额"><el-input-number v-model="form.min_withdrawal" :precision="2" :min="0" /> USDT</el-form-item>
            <el-form-item label="提现费方式"><el-radio-group v-model="form.withdrawal_fee_type"><el-radio value="fixed">固定金额</el-radio><el-radio value="percent">百分比</el-radio></el-radio-group></el-form-item>
            <el-form-item label="提现手续费"><el-input-number v-model="form.withdrawal_fee_value" :precision="4" :min="0" /> {{ form.withdrawal_fee_type === 'percent' ? '%' : 'USDT' }}</el-form-item>
          </div>
          <el-form-item><el-button type="primary" :loading="saving" @click="saveConfig">保存支付与结算配置</el-button></el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="AI 文档" name="ai">
        <el-alert :title="aiConfigured ? 'AI API Key 已配置' : 'AI API Key 尚未配置'" :type="aiConfigured ? 'success' : 'warning'" :closable="false" show-icon class="asset-tip" />
        <el-form :model="form" label-width="140px" class="form-width" v-loading="loading">
          <el-form-item label="模型供应商">
            <el-radio-group v-model="form.ai_provider">
              <el-radio value="deepseek">DeepSeek</el-radio>
              <el-radio value="qwen">千问（Qwen）</el-radio>
            </el-radio-group>
          </el-form-item>
          <template v-if="form.ai_provider === 'deepseek'">
            <el-form-item label="API 地址"><el-input v-model="form.deepseek_base_url" /></el-form-item>
            <el-form-item label="分析模型"><el-input v-model="form.deepseek_model" /></el-form-item>
            <el-form-item label="API Key"><el-input v-model="form.deepseek_api_key" type="password" show-password :placeholder="form.deepseek_configured ? '已配置，留空保持不变' : '请输入 DeepSeek API Key'" /></el-form-item>
          </template>
          <template v-else>
            <el-form-item label="API 地址"><el-input v-model="form.qwen_base_url" /></el-form-item>
            <el-form-item label="分析模型"><el-input v-model="form.qwen_model" placeholder="qwen3.7-plus / qwen3.8-max / qwen3.8-flash" /></el-form-item>
            <el-form-item label="API Key"><el-input v-model="form.qwen_api_key" type="password" show-password :placeholder="form.qwen_configured ? '已配置，留空保持不变' : '请输入千问 API Key（DashScope 兼容模式）'" /></el-form-item>
          </template>
          <el-form-item><el-button type="primary" :loading="saving" @click="saveConfig">保存 AI 配置</el-button></el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="插件详情页" name="plugin_detail">
        <el-alert title="以下配置控制官网插件详情页的布局、文案、Tab 与按钮，保存后官网页面立即生效。" type="info" :closable="false" show-icon class="asset-tip" />
        <div class="detail-config" v-loading="loading">
          <div class="cfg-grid">
            <!-- 板块显隐 -->
            <el-card shadow="never" class="cfg-card">
              <template #header>板块显隐</template>
              <div v-for="key in ['hero', 'intro', 'docs', 'demo', 'changelog']" :key="key" class="cfg-row">
                <span class="cfg-label">{{ sectionNames[key] }}</span>
                <el-switch v-model="detailCfg.sections[key].enabled" />
              </div>
            </el-card>

            <!-- 板块文案 -->
            <el-card shadow="never" class="cfg-card">
              <template #header>板块文案</template>
              <template v-for="key in ['intro', 'docs', 'demo', 'changelog']" :key="key">
                <div class="cfg-field">
                  <div class="cfg-sub">{{ sectionNames[key] }}</div>
                  <el-input v-model="detailCfg.sections[key].title" size="small" placeholder="标题" />
                  <el-input v-model="detailCfg.sections[key].title_em" size="small" placeholder="强调词（渐变高亮）" class="mt8" />
                  <el-input v-model="detailCfg.sections[key].description" size="small" type="textarea" :rows="2" placeholder="描述" />
                </div>
              </template>
            </el-card>

            <!-- Tab 标签 -->
            <el-card shadow="never" class="cfg-card">
              <template #header>Tab 标签</template>
              <div v-for="key in ['intro', 'docs', 'demo', 'changelog']" :key="key" class="cfg-row">
                <el-input v-model="detailCfg.tabs[key].label" size="small" class="flex-1" />
                <el-input-number v-model="detailCfg.tabs[key].sort" :min="1" size="small" controls-position="right" class="sort-input" />
                <el-switch v-model="detailCfg.tabs[key].enabled" />
              </div>
            </el-card>

            <!-- 按钮 -->
            <el-card shadow="never" class="cfg-card">
              <template #header>按钮</template>
              <div class="cfg-field">
                <div class="cfg-sub">Demo 按钮</div>
                <el-input v-model="detailCfg.buttons.demo.label" size="small" placeholder="按钮文案" />
                <div class="cfg-row mt8">
                  <el-select v-model="detailCfg.buttons.demo.style" size="small" class="flex-1">
                    <el-option label="幽灵描边 (ghost)" value="ghost" />
                    <el-option label="主色实心 (primary)" value="primary" />
                    <el-option label="成功绿 (success)" value="success" />
                    <el-option label="警告橙 (warning)" value="warning" />
                  </el-select>
                  <el-switch v-model="detailCfg.buttons.demo.enabled" />
                </div>
              </div>
              <div class="cfg-field">
                <div class="cfg-sub">购买按钮</div>
                <el-input v-model="detailCfg.buttons.buy.label_free" size="small" placeholder="免费版文案" />
                <el-input v-model="detailCfg.buttons.buy.label_paid" size="small" class="mt8" placeholder="付费版文案" />
                <div class="cfg-row mt8">
                  <el-select v-model="detailCfg.buttons.buy.style" size="small" class="flex-1">
                    <el-option label="主色实心 (primary)" value="primary" />
                    <el-option label="幽灵描边 (ghost)" value="ghost" />
                    <el-option label="成功绿 (success)" value="success" />
                    <el-option label="警告橙 (warning)" value="warning" />
                  </el-select>
                  <el-switch v-model="detailCfg.buttons.buy.enabled" />
                </div>
              </div>
            </el-card>

            <!-- 文案标签 -->
            <el-card shadow="never" class="cfg-card">
              <template #header>文案标签</template>
              <div class="cfg-field">
                <div class="cfg-sub">元信息文案</div>
                <el-input v-model="detailCfg.labels.content" size="small" placeholder="下载" />
                <el-input v-model="detailCfg.labels.author" size="small" class="mt8" placeholder="开发者" />
                <el-input v-model="detailCfg.labels.rating" size="small" class="mt8" placeholder="评分" />
                <el-input v-model="detailCfg.labels.version" size="small" class="mt8" placeholder="版本" />
              </div>
              <div class="cfg-field">
                <div class="cfg-sub">精选标签</div>
                <el-input v-model="detailCfg.sections.hero.star_tag_text" size="small" placeholder="⭐ 精选插件" />
              </div>
            </el-card>

            <!-- 悬浮操作 -->
            <el-card shadow="never" class="cfg-card">
              <template #header>悬浮操作</template>
              <div v-for="key in ['contact', 'docs', 'top']" :key="key" class="cfg-row">
                <el-input v-model="detailCfg.float_actions[key].icon" size="small" class="icon-input" />
                <el-input v-model="detailCfg.float_actions[key].title" size="small" class="flex-1" />
                <el-switch v-model="detailCfg.float_actions[key].enabled" />
              </div>
            </el-card>
          </div>
          <div class="cfg-actions">
            <el-button type="primary" :loading="saving" @click="saveDetailConfig">保存插件详情页配置</el-button>
            <el-button @click="resetDetailConfig">恢复默认</el-button>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </el-card>

  <el-dialog v-model="navDialog" :title="editingNav.id ? '编辑导航' : '新增导航'" width="560px">
    <el-form :model="editingNav" label-width="90px">
      <el-form-item label="名称"><el-input v-model="editingNav.title" maxlength="64" /></el-form-item>
      <el-form-item label="链接"><el-input v-model="editingNav.link" placeholder="/apehub-web/plugins.html 或 https://..." /></el-form-item>
      <el-form-item label="导航图标"><AssetField v-model="editingNav.icon_url" /></el-form-item>
      <el-form-item label="打开方式"><el-radio-group v-model="editingNav.open_mode"><el-radio value="same">当前页</el-radio><el-radio value="new">新窗口</el-radio></el-radio-group></el-form-item>
      <el-form-item label="排序"><el-input-number v-model="editingNav.sort" :min="0" /></el-form-item>
      <el-form-item label="启用"><el-switch v-model="editingNav.enabled" /></el-form-item>
    </el-form>
    <template #footer><el-button @click="navDialog = false">取消</el-button><el-button type="primary" :loading="navSaving" @click="saveNavigation">保存</el-button></template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { ElButton, ElImage, ElInput, ElMessage, ElMessageBox } from 'element-plus'
import { createAdminContent, createAdminNavigation, deleteAdminNavigation, getAdminConfig, getAdminContent, getAdminNavigation, updateAdminConfig, updateAdminContent, updateAdminNavigation, uploadSiteAsset } from '@/api/apehub_web'

const AssetField = defineComponent({
  props: { modelValue: { type: String, default: '' } }, emits: ['update:modelValue'],
  setup(props, { emit }) {
    const fileInput = ref<HTMLInputElement | null>(null)
    const uploading = ref(false)
    const pickFile = () => {
      // 原生 label 触发 input[type=file]，绕开 ElUpload 的 JS 手势链路，
      // 避免部分浏览器/扩展拦截 JS 触发的文件选择器导致"点了没反应"
      fileInput.value?.click()
    }
    const onFileChange = async (event: Event) => {
      const input = event.target as HTMLInputElement
      const file = input.files?.[0]
      input.value = '' // 允许重复选择同一文件
      if (!file) return
      uploading.value = true
      try {
        const data = new FormData(); data.append('file', file)
        const res = await uploadSiteAsset(data)
        emit('update:modelValue', res.url)
        ElMessage.success('图片上传成功')
      } catch (error: any) {
        ElMessage.error(error.message || '图片上传失败')
      } finally {
        uploading.value = false
      }
    }
    return () => h('div', { class: 'asset-field' }, [
      props.modelValue ? h(ElImage, { src: props.modelValue, fit: 'contain', class: 'asset-preview' }) : null,
      h(ElInput, { modelValue: props.modelValue, placeholder: '上传图片或输入图片 URL', 'onUpdate:modelValue': (value: string) => emit('update:modelValue', value) }),
      h('label', { class: 'asset-upload-btn' }, [
        h('input', { ref: fileInput, type: 'file', accept: 'image/png,image/jpeg,image/gif,image/webp', class: 'asset-file-input', onChange: onFileChange }),
        h(ElButton, { type: 'primary', plain: true, loading: uploading.value, onClick: pickFile }, () => uploading.value ? '上传中' : '上传'),
      ]),
    ])
  },
})

const activeTab = ref('basic'); const loading = ref(false); const saving = ref(false)
const navLoading = ref(false); const navSaving = ref(false); const navigation = ref<any[]>([]); const navDialog = ref(false); const hero = ref<any>(null)
const form = ref<any>({ site_name: '', site_logo: '/apehub-web/assets/logo.png', site_icon: '/apehub-web/assets/logo.png', site_domain: '', site_prefix: '/apehub-web', seo_title: '', seo_description: '', seo_keywords: '', theme_mode: 'light', service_fee_rate: 30, mail_user: '', mail_code: '', mail_host: 'smtp.qq.com', mail_port: 465, lempay_pid: 0, lempay_key: '', lempay_submit_url: '', lempay_api_url: '', lempay_notify_url: '', lempay_return_url: '', lempay_payment_type: 'usdt', deepseek_api_key: '', deepseek_base_url: 'https://api.deepseek.com', deepseek_model: 'deepseek-chat', ai_provider: 'deepseek', qwen_api_key: '', qwen_base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', qwen_model: 'qwen3.7-plus', settlement_days: 7, refund_days: 7, min_withdrawal: 100, withdrawal_fee_type: 'fixed', withdrawal_fee_value: 0 })

/* ---------------- 插件详情页配置 ---------------- */
const defaultDetailConfig = () => ({
  sections: {
    hero: { enabled: true, star_tag_text: '⭐ 精选插件', show_star: false, show_meta: true, show_rating: true, show_icon: true },
    intro: { enabled: true, title: '插件介绍', title_em: '介绍', description: '了解这个插件的核心能力、技术特点与使用场景。', show_features: true, show_screenshots: true, show_parameters: true },
    docs: { enabled: true, title: '技术文档', title_em: '文档', description: '安装配置、接口说明与使用指南。', show_install: true, show_config: true },
    demo: { enabled: true, title: 'Demo 体验', title_em: '体验', description: '选择终端体验方式，直接在线感受插件能力。' },
    changelog: { enabled: true, title: '更新日志', title_em: '日志', description: '插件版本迭代记录与功能变更。' },
  },
  tabs: {
    intro: { label: '📖 介绍', enabled: true, sort: 1 },
    docs: { label: '📄 文档', enabled: true, sort: 2 },
    demo: { label: '🖥 Demo 体验', enabled: true, sort: 3 },
    changelog: { label: '📜 更新日志', enabled: true, sort: 4 },
  },
  buttons: {
    demo: { label: '🖥 立即体验', enabled: true, style: 'ghost' },
    buy: { label_free: '免费下载', label_paid: '🛒 立即购买', enabled: true, style: 'primary' },
  },
  labels: { content: '下载', author: '开发者', rating: '评分', version: '版本', featured: '⭐ 精选插件' },
  float_actions: {
    contact: { enabled: true, icon: '💬', title: '客服咨询' },
    docs: { enabled: true, icon: '📖', title: '帮助文档' },
    top: { enabled: true, icon: '↑', title: '返回顶部' },
  },
})
const deepMerge = (target: any, source: any) => {
  if (!source || typeof source !== 'object') return target
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      target[key] = deepMerge(target[key] || {}, source[key])
    } else if (source[key] !== undefined) {
      target[key] = source[key]
    }
  }
  return target
}
const detailCfg = ref<any>(defaultDetailConfig())
const sectionNames: Record<string, string> = { hero: '头部 Hero', intro: '插件介绍', docs: '技术文档', demo: 'Demo 体验', changelog: '更新日志' }
const loadDetailConfig = () => { detailCfg.value = deepMerge(defaultDetailConfig(), form.value.plugin_detail_config || {}) }
const saveDetailConfig = async () => {
  saving.value = true
  try {
    await updateAdminConfig({ plugin_detail_config: detailCfg.value })
    form.value.plugin_detail_config = JSON.parse(JSON.stringify(detailCfg.value))
    ElMessage.success('插件详情页配置已保存')
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}
const resetDetailConfig = () => { detailCfg.value = defaultDetailConfig() }
const heroImage = computed({ get: () => hero.value?.image || '/apehub-web/assets/screenshot.png', set: (value) => { if (hero.value) hero.value.image = value } })
const aiConfigured = computed(() => (form.value.ai_provider === 'qwen' ? form.value.qwen_configured : form.value.deepseek_configured))
const newNav = () => ({ title: '', link: '', icon_url: '', open_mode: 'same', enabled: true, sort: 0 }); const editingNav = ref<any>(newNav())
const loadConfig = async () => { loading.value = true; try { form.value = { ...form.value, ...(await getAdminConfig()) }; loadDetailConfig(); const content = await getAdminContent(); hero.value = content.find((item: any) => item.block_key === 'hero') || null } catch (error: any) { ElMessage.error(error.message || '配置加载失败') } finally { loading.value = false } }
const loadNavigation = async () => { navLoading.value = true; try { navigation.value = await getAdminNavigation() } catch (error: any) { ElMessage.error(error.message || '导航加载失败') } finally { navLoading.value = false } }
const saveConfig = async () => { saving.value = true; try { const payload = { ...form.value }; delete payload.mail_configured; delete payload.lempay_configured; delete payload.deepseek_configured; delete payload.qwen_configured; delete payload.currency; await updateAdminConfig(payload); form.value.mail_code = ''; form.value.lempay_key = ''; form.value.deepseek_api_key = ''; form.value.qwen_api_key = ''; await loadConfig(); ElMessage.success('配置已保存') } catch (error: any) { ElMessage.error(error.message || '保存失败') } finally { saving.value = false } }
const saveAssets = async () => { saving.value = true; try { await updateAdminConfig({ site_logo: form.value.site_logo, site_icon: form.value.site_icon }); if (hero.value) await updateAdminContent(hero.value.id, hero.value); else await createAdminContent({ block_key: 'hero', title: '', subtitle: '', body: '', image: heroImage.value, sort: 0, enabled: true }); ElMessage.success('图片设置已保存') } catch (error: any) { ElMessage.error(error.message || '图片保存失败') } finally { saving.value = false } }
const openNavDialog = (item?: any) => { editingNav.value = item ? { ...item } : newNav(); navDialog.value = true }
const saveNavigation = async () => { if (!editingNav.value.title || !editingNav.value.link) return ElMessage.warning('请填写导航名称和链接'); navSaving.value = true; try { if (editingNav.value.id) await updateAdminNavigation(editingNav.value.id, editingNav.value); else await createAdminNavigation(editingNav.value); navDialog.value = false; await loadNavigation(); ElMessage.success('导航已保存') } catch (error: any) { ElMessage.error(error.message || '导航保存失败') } finally { navSaving.value = false } }
const removeNavigation = async (item: any) => { await ElMessageBox.confirm(`确认删除导航「${item.title}」？`, '删除导航', { type: 'warning' }); await deleteAdminNavigation(item.id); await loadNavigation(); ElMessage.success('导航已删除') }
onMounted(async () => { await Promise.all([loadConfig(), loadNavigation()]) })
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }.form-width { max-width: 680px; }.form-wide { max-width: 1060px; }.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 20px; }.asset-tip { margin-bottom: 18px; }.toolbar { margin-bottom: 16px; }.nav-icon { width: 32px; height: 32px; }.field-tip { font-size: 12px; color: var(--el-text-color-secondary); line-height: 1.5; margin-top: 4px; width: 100%; }
:deep(.asset-field) { display: flex; align-items: center; gap: 10px; width: 100%; }:deep(.asset-field .el-input) { flex: 1; }:deep(.asset-preview) { width: 48px; height: 48px; flex: 0 0 48px; border: 1px solid var(--el-border-color); }
:deep(.asset-upload-btn) { position: relative; display: inline-flex; cursor: pointer; }
:deep(.asset-file-input) { position: absolute; width: 0; height: 0; opacity: 0; overflow: hidden; pointer-events: none; }
@media (max-width: 900px) { .form-grid { grid-template-columns: 1fr; } }
.detail-config { max-width: 1280px; }.cfg-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-bottom: 20px; }
.cfg-card .el-card__body { padding: 16px; }.cfg-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }.cfg-row:last-child { margin-bottom: 0; }
.cfg-label { width: 110px; flex: 0 0 110px; color: var(--el-text-color-primary); }.cfg-sub { color: var(--el-text-color-secondary); font-size: 13px; margin-bottom: 8px; }
.cfg-field { margin-bottom: 14px; }.cfg-field:last-child { margin-bottom: 0; }.flex-1 { flex: 1; }.mt8 { margin-top: 8px; }
.sort-input { width: 90px; }.icon-input { width: 64px; }.cfg-actions { display: flex; gap: 12px; }
</style>
