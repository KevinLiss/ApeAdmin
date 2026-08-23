<template>
  <div class="settings-page">
    <!-- 页面标题 -->
    <div class="page-head">
      <h3>系统设置</h3>
      <span class="breadcrumb">系统设置 / 偏好与基本信息</span>
    </div>

    <el-row :gutter="20">
      <!-- 左栏：基本信息 -->
      <el-col :xs="24" :md="10">
        <el-card shadow="never" class="settings-card">
          <template #header>
            <div class="card-title">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="当前用户">
              {{ userStore.nickname || userStore.username || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="登录账号">
              {{ userStore.username || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="角色">
              <el-tag v-for="r in userStore.roles" :key="r" size="small" class="role-tag">{{ r }}</el-tag>
              <span v-if="!userStore.roles?.length">—</span>
            </el-descriptions-item>
            <el-descriptions-item label="权限数量">
              {{ userStore.permissions?.length || 0 }} 项
            </el-descriptions-item>
            <el-descriptions-item label="应用名称">ApeAdmin</el-descriptions-item>
            <el-descriptions-item label="前端版本">v0.1.0</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右栏：偏好设置 -->
      <el-col :xs="24" :md="14">
        <el-card shadow="never" class="settings-card">
          <template #header>
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              <span>偏好设置</span>
            </div>
          </template>

          <div class="pref-item">
            <div class="pref-left">
              <span class="pref-title">深色模式</span>
              <span class="pref-desc">切换全局深色配色（自动保存到本地）</span>
            </div>
            <el-switch v-model="prefs.darkMode" @change="onDarkChange" />
          </div>

          <div class="pref-item">
            <div class="pref-left">
              <span class="pref-title">消息通知</span>
              <span class="pref-desc">接收系统通知与待办提醒</span>
            </div>
            <el-switch v-model="prefs.notifications" />
          </div>

          <div class="pref-item">
            <div class="pref-left">
              <span class="pref-title">侧边栏折叠</span>
              <span class="pref-desc">默认收起侧边栏，为内容区腾出空间</span>
            </div>
            <el-switch v-model="prefs.collapsedSidebar" @change="onCollapsedChange" />
          </div>

          <div class="pref-item">
            <div class="pref-left">
              <span class="pref-title">语言</span>
              <span class="pref-desc">界面显示语言</span>
            </div>
            <el-select v-model="prefs.language" style="width: 140px">
              <el-option label="简体中文" value="zh-CN" />
              <el-option label="English" value="en-US" />
            </el-select>
          </div>

          <div class="pref-item">
            <div class="pref-left">
              <span class="pref-title">界面密度</span>
              <span class="pref-desc">控制表格与表单的紧凑程度</span>
            </div>
            <el-radio-group v-model="prefs.density">
              <el-radio-button label="comfortable">舒适</el-radio-button>
              <el-radio-button label="compact">紧凑</el-radio-button>
            </el-radio-group>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Setting } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useTheme } from '@/composables/useTheme'

const userStore = useUserStore()
const { isDark, applyDark } = useTheme()

const STORAGE_KEY = 'apeadmin_prefs'

const prefs = reactive({
  darkMode: false,
  notifications: true,
  collapsedSidebar: false,
  language: 'zh-CN',
  density: 'comfortable',
})

function loadPrefs() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) Object.assign(prefs, JSON.parse(raw))
  } catch {
    // ignore corrupted prefs
  }
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

function onCollapsedChange(val: boolean) {
  savePrefs()
  ElMessage.success(val ? '已启用侧边栏折叠' : '已关闭侧边栏折叠')
}

onMounted(loadPrefs)
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
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: #2b2b2b;
}
.breadcrumb {
  font-size: 13px;
  color: #909399;
}

.settings-card {
  border-radius: 16px;
  margin-bottom: 20px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.card-title .el-icon {
  color: #5A67F5;
}
.role-tag {
  background: rgba(90, 103, 245, 0.08);
  border-color: rgba(90, 103, 245, 0.2);
  color: #5A67F5;
  margin-right: 6px;
}

.pref-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid #f1f3ff;
}
.pref-item:last-child {
  border-bottom: none;
}
.pref-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.pref-title {
  font-size: 14px;
  font-weight: 500;
  color: #2b2b2b;
}
.pref-desc {
  font-size: 12px;
  color: #909399;
}
</style>