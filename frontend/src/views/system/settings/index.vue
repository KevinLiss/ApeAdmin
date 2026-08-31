<template>
  <div class="settings-page">
    <!-- 页面标题 -->
    <div class="page-head">
      <div>
        <h3>系统设置</h3>
        <span class="breadcrumb">系统管理 / 站点配置与品牌定制</span>
      </div>
      <div class="head-actions">
        <el-button type="warning" :loading="restarting" @click="handleRestart">
          <el-icon v-if="!restarting"><RefreshRight /></el-icon>重启后端
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon>保存设置
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左栏：品牌设置 -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="settings-card">
          <template #header>
            <div class="card-title">
              <el-icon><Brush /></el-icon>
              <span>品牌定制</span>
            </div>
          </template>

          <el-form label-width="120px" label-position="right">
            <el-form-item label="站点名称">
              <el-input v-model="form.site_name" placeholder="如 ApeAdmin" />
            </el-form-item>

            <el-form-item label="Logo URL">
              <div class="logo-row">
                <el-input v-model="form.logo_url" placeholder="留空使用默认图标" />
                <div class="logo-preview">
                  <img v-if="form.logo_url" :src="form.logo_url" alt="Logo" class="preview-img" />
                  <img v-else src="/assets/images/logo-icon.png" alt="Logo" class="preview-img" />
                </div>
              </div>
            </el-form-item>

            <el-form-item label="主题色">
              <div class="color-row">
                <el-color-picker v-model="form.primary_color" @change="onColorChange" />
                <el-input v-model="form.primary_color" style="width: 140px" placeholder="#5A67F5" />
                <div class="color-presets">
                  <span
                    v-for="c in colorPresets"
                    :key="c"
                    class="color-dot"
                    :style="{ background: c }"
                    @click="form.primary_color = c; onColorChange(c)"
                  ></span>
                </div>
              </div>
            </el-form-item>

            <el-form-item label="登录页背景">
              <el-input v-model="form.login_bg" placeholder="背景图 URL（留空使用默认）" />
            </el-form-item>

            <el-form-item label="页脚文字">
              <el-input v-model="form.footer_text" placeholder="如 ApeAdmin © 2026" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右栏：系统配置 -->
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="settings-card">
          <template #header>
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              <span>系统配置</span>
            </div>
          </template>

          <el-form label-width="120px" label-position="right">
            <el-form-item label="后台访问路径">
              <el-input v-model="form.admin_path" placeholder="/admin">
                <template #prepend>域名 +</template>
              </el-input>
              <div class="form-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>管理后台将挂载在此路径下，主域名留给插件服务使用。修改后需<span class="tip-highlight">重启后端</span>生效。</span>
              </div>
            </el-form-item>

            <el-form-item label="侧边栏主题">
              <el-radio-group v-model="form.sidebar_theme">
                <el-radio-button label="light">浅色</el-radio-button>
                <el-radio-button label="dark">深色</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-form>

          <!-- 实时预览 -->
          <el-divider content-position="center">实时预览</el-divider>
          <div class="preview-box" :style="{ '--preview-color': form.primary_color }">
            <div class="preview-sidebar" :class="{ 'preview-dark': form.sidebar_theme === 'dark' }">
              <div class="preview-logo">
                <img v-if="form.logo_url" :src="form.logo_url" alt="" class="preview-logo-img" />
                <img v-else src="/assets/images/logo-icon.png" alt="" class="preview-logo-img" />
                <span>{{ form.site_name || 'ApeAdmin' }}</span>
              </div>
              <div class="preview-menu-item active">
                <span>系统设置</span>
              </div>
              <div class="preview-menu-item">
                <span>用户管理</span>
              </div>
            </div>
            <div class="preview-content" :class="{ 'preview-content-dark': form.sidebar_theme === 'dark' }">
              <div class="preview-header">
                <span>{{ form.footer_text || 'ApeAdmin © 2026' }}</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 个人偏好 -->
        <el-card shadow="never" class="settings-card" style="margin-top: 20px">
          <template #header>
            <div class="card-title">
              <el-icon><User /></el-icon>
              <span>个人偏好</span>
            </div>
          </template>
          <el-form label-width="120px" label-position="right">
            <el-form-item label="深色模式">
              <el-switch v-model="prefs.darkMode" @change="onDarkChange" />
            </el-form-item>
            <el-form-item label="侧边栏折叠">
              <el-switch v-model="prefs.collapsedSidebar" @change="savePrefs" />
            </el-form-item>
            <el-form-item label="界面语言">
              <el-select v-model="prefs.language" style="width: 140px">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Brush, Setting, Check, RefreshRight, InfoFilled, User } from '@element-plus/icons-vue'
import { useTheme } from '@/composables/useTheme'
import { useSettingsStore } from '@/stores/settings'
import { getSettings, updateSettings, restartServer } from '@/api'

const { isDark, applyDark } = useTheme()
const settingsStore = useSettingsStore()

const saving = ref(false)
const restarting = ref(false)

const colorPresets = [
  '#5A67F5', // 靛蓝紫
  '#4f46e5', // 靛蓝
  '#7c3aed', // 紫
  '#0ea5e9', // 天蓝
  '#10b981', // 绿
  '#f59e0b', // 橙
  '#ef4444', // 红
  '#6366f1', // 蓝紫
]

const form = reactive({
  site_name: 'ApeAdmin',
  logo_url: '',
  primary_color: '#5A67F5',
  admin_path: '/admin',
  footer_text: 'ApeAdmin © 2026',
  login_bg: '',
  sidebar_theme: 'light',
})

const prefs = reactive({
  darkMode: false,
  collapsedSidebar: false,
  language: 'zh-CN',
})

const STORAGE_KEY = 'apeadmin_prefs'

function loadPrefs() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) Object.assign(prefs, JSON.parse(raw))
  } catch { /* ignore */ }
  prefs.darkMode = isDark.value
}

function savePrefs() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...prefs }))
}

function onDarkChange(val: boolean) {
  applyDark(val)
  savePrefs()
  ElMessage.success(val ? '已切换深色模式' : '已切换浅色模式')
}

function onColorChange(color: string) {
  // Live preview: apply to CSS variables immediately
  settingsStore.primary_color = color
  settingsStore.applyThemeColor()
}

async function loadSettings() {
  try {
    const data: any = await getSettings()
    if (Array.isArray(data)) {
      for (const item of data) {
        if (item.key in form) {
          ;(form as any)[item.key] = item.value
        }
      }
    }
  } catch {
    ElMessage.warning('加载设置失败，使用默认值')
  }
}

async function handleSave() {
  saving.value = true
  try {
    const items: Record<string, string> = {}
    for (const [k, v] of Object.entries(form)) {
      items[k] = String(v)
    }
    await updateSettings(items)
    // Sync to store
    settingsStore.site_name = form.site_name
    settingsStore.logo_url = form.logo_url
    settingsStore.primary_color = form.primary_color
    settingsStore.footer_text = form.footer_text
    settingsStore.applyThemeColor()
    ElMessage.success('设置已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleRestart() {
  try {
    await ElMessageBox.confirm(
      '重启后端将短暂中断服务（约 5 秒），确定继续？',
      '重启确认',
      { type: 'warning' }
    )
  } catch {
    return
  }

  restarting.value = true
  try {
    await restartServer()
    ElMessage.success('后端正在重启...')

    // Poll health check
    for (let i = 0; i < 30; i++) {
      await new Promise(r => setTimeout(r, 1000))
      try {
        const resp = await fetch('/api/v1/health', { method: 'GET' })
        if (resp.ok) {
          ElMessage.success('后端已恢复')
          break
        }
      } catch {
        // still restarting
      }
    }
  } catch {
    ElMessage.error('重启请求失败')
  } finally {
    restarting.value = false
    // Reload settings after restart
    await loadSettings()
  }
}

onMounted(async () => {
  loadPrefs()
  await loadSettings()
})
</script>

<style scoped>
.settings-page {
  padding: 0;
}
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9edf3;
}
.page-head h3 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  color: #2b2b2b;
}
.breadcrumb {
  font-size: 13px;
  color: #909399;
}
.head-actions {
  display: flex;
  gap: 10px;
}

.settings-card {
  border-radius: 16px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.card-title .el-icon {
  color: var(--theme-default, #5A67F5);
}

.logo-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}
.logo-preview {
  flex-shrink: 0;
}
.preview-img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  object-fit: cover;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.color-presets {
  display: flex;
  gap: 6px;
}
.color-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}
.color-dot:hover {
  border-color: #fff;
  box-shadow: 0 0 0 2px var(--el-color-primary, #5A67F5);
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}
.tip-highlight {
  color: #e56809;
  font-weight: 600;
}

/* Preview box */
.preview-box {
  display: flex;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e9edf3;
  height: 200px;
}
.preview-sidebar {
  width: 160px;
  background: #fff;
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-right: 1px solid #f1f3ff;
}
.preview-sidebar.preview-dark {
  background: #232838;
  border-right-color: #2e3344;
}
.preview-logo {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px 10px;
  border-bottom: 1px solid #f1f3ff;
}
.preview-dark .preview-logo {
  border-bottom-color: #2e3344;
}
.preview-logo span {
  font-size: 13px;
  font-weight: 700;
  color: #2b2b2b;
}
.preview-dark .preview-logo span {
  color: #e6e8f0;
}
.preview-logo-img {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  object-fit: cover;
}
.preview-menu-item {
  padding: 7px 14px;
  font-size: 12px;
  color: #5a6273;
  margin: 2px 8px;
  border-radius: 6px;
}
.preview-menu-item.active {
  background: var(--preview-color, #5A67F5);
  color: #fff;
}
.preview-dark .preview-menu-item {
  color: #8a90a8;
}
.preview-content {
  flex: 1;
  background: #eff3f9;
  display: flex;
  flex-direction: column;
}
.preview-content-dark {
  background: #1b1f2e;
}
.preview-header {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  color: #909399;
  display: flex;
  justify-content: flex-end;
}
.preview-content-dark .preview-header {
  background: rgba(35, 40, 56, 0.8);
  color: #8a90a8;
}
</style>
