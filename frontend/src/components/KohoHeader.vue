<template>
  <header class="koho-header" :class="{ 'close-icon': collapsed }">
    <div class="header-wrapper">
      <!-- Search -->
      <div class="left-header">
        <div class="search-box">
          <input class="search-input" type="text" placeholder="点击这里搜索........" v-model="keyword" @keyup.enter="onSearch" />
          <span class="search-icon"><el-icon :size="16"><Search /></el-icon></span>
        </div>
      </div>

      <!-- Right icons -->
      <div class="nav-right">
        <ul class="nav-menus">
          <!-- Language -->
          <li class="icon-item language-nav" @click="langVisible = !langVisible">
            <span class="flag-icon"></span>
            <span class="lang-txt">中文</span>
          </li>

          <!-- Theme toggle -->
          <li class="icon-item" @click="$emit('toggle-theme')">
            <el-icon :size="18"><Moon v-if="!isDark" /><Sunny v-else /></el-icon>
          </li>

          <!-- Bookmark -->
          <li class="icon-item" @click="bookmarkVisible = !bookmarkVisible">
            <el-icon :size="18"><Star /></el-icon>
          </li>

          <!-- Notifications -->
          <li class="icon-item has-badge" @click="notifVisible = !notifVisible">
            <el-icon :size="18"><Bell /></el-icon>
            <span class="badge-num">{{ notifications.length }}</span>
            <div v-if="notifVisible" class="dropdown-panel notif-panel">
              <div class="dropdown-head"><el-icon :size="16"><Bell /></el-icon><h3>通知</h3></div>
              <ul>
                <li v-for="(n, i) in notifications" :key="i">
                  <p><span class="dot" :style="{ background: n.color }"></span>{{ n.text }}<em>{{ n.time }}</em></p>
                </li>
              </ul>
              <a class="check-all">查看全部通知</a>
            </div>
          </li>

          <!-- Messages -->
          <li class="icon-item" @click="msgVisible = !msgVisible">
            <el-icon :size="18"><ChatDotRound /></el-icon>
          </li>

          <!-- Fullscreen -->
          <li class="icon-item" @click="toggleFullscreen">
            <el-icon :size="18"><FullScreen /></el-icon>
          </li>

          <!-- Profile -->
          <li class="profile-nav" @click="profileVisible = !profileVisible">
            <div class="profile-media">
              <el-avatar :size="38" class="profile-avatar">{{ avatarText }}</el-avatar>
              <div class="profile-info">
                <span class="profile-name">{{ userStore.nickname || userStore.username || 'Admin' }}</span>
                <p class="profile-role">{{ roleText }} <el-icon :size="12"><ArrowDown /></el-icon></p>
              </div>
            </div>
            <ul v-if="profileVisible" class="profile-dropdown">
              <li><a @click="$emit('profile')"><el-icon :size="16"><User /></el-icon><span>个人中心</span></a></li>
              <li><a @click="$emit('settings')"><el-icon :size="16"><Setting /></el-icon><span>系统设置</span></a></li>
              <li><a @click="handleLogout"><el-icon :size="16"><SwitchButton /></el-icon><span>退出登录</span></a></li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const props = defineProps<{
  isDark?: boolean
  collapsed?: boolean
}>()
const emit = defineEmits<{
  (e: 'toggle-theme'): void
  (e: 'profile'): void
  (e: 'settings'): void
  (e: 'logout'): void
}>()

const router = useRouter()
const userStore = useUserStore()

const keyword = ref('')
const langVisible = ref(false)
const bookmarkVisible = ref(false)
const notifVisible = ref(false)
const msgVisible = ref(false)
const profileVisible = ref(false)

const notifications = [
  { text: '系统健康检查完成', time: '10 分钟', color: '#5A67F5' },
  { text: 'MCP 插件加载成功', time: '1 小时', color: '#67C23A' },
  { text: '新用户注册', time: '3 小时', color: '#E6A23C' },
  { text: '数据库备份完成', time: '6 小时', color: '#F56C6C' },
]

const avatarText = computed(() => (userStore.nickname || userStore.username || 'A').charAt(0).toUpperCase())
const profileText = computed(() => userStore.roles?.[0] || 'Admin')
const roleText = computed(() => (profileText.value === 'admin' ? '超级管理员' : profileText.value))

function onSearch() {
  if (keyword.value.trim()) {
    ElMessage.info(`搜索：${keyword.value}`)
  }
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

async function handleLogout() {
  await userStore.logout()
  ElMessage.success('已退出登录')
  emit('logout')
  router.push('/login')
}
</script>

<style scoped>
/* ===== Koho 1:1 Header ===== */
.koho-header {
  position: fixed;
  top: 0;
  left: 258px;
  right: 0;
  height: 64px;
  background: #ffffff;
  box-shadow: 0 0 20px rgba(89, 102, 122, 0.1);
  z-index: 8;
  transition: left 0.3s ease;
}
.koho-header.close-icon {
  left: 86px;
}

.header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 100%;
}

/* Search */
.left-header {
  flex: 1;
  max-width: 480px;
}
.input-group {
  position: relative;
  display: flex;
  align-items: center;
}
.search-input {
  width: 100%;
  height: 42px;
  border: 1px solid #eef0f4;
  border-radius: 8px;
  padding: 0 42px 0 16px;
  font-size: 14px;
  background: #f8fafc;
  color: #2b2b2b;
  outline: none;
  transition: all 0.25s;
}
.search-input::placeholder {
  color: #9aa3b2;
}
.search-input:focus {
  border-color: var(--theme-default, #5A67F5);
  background: #fff;
  box-shadow: 0 0 0 3px rgba(90, 103, 245, 0.12);
}
.search-icon {
  position: absolute;
  right: 14px;
  color: #909399;
  cursor: pointer;
}

/* Right */
.nav-right {
  display: flex;
  align-items: center;
}
.nav-menus {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  padding: 0;
}

.icon-item {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: #59667a;
  cursor: pointer;
  transition: all 0.2s;
}
.icon-item:hover {
  background: #eff3f9;
  color: var(--theme-default, #5A67F5);
}

/* Language */
.icon-item.lang-item {
  width: auto;
  padding: 0 10px;
  gap: 6px;
  border-radius: 8px;
}
.flag-icon {
  width: 18px;
  height: 13px;
  border-radius: 2px;
  background: linear-gradient(135deg, #de2910 33%, #ffde00 33%, #ffde00 66%, #de2910 66%);
  display: inline-block;
}
.lang-txt {
  font-size: 13px;
  font-weight: 500;
}

/* Badge */
.has-badge {
  position: relative;
}
.badge-num {
  position: absolute;
  top: 2px;
  right: 4px;
  min-width: 17px;
  height: 17px;
  border-radius: 50%;
  background: var(--theme-default, #5A67F5);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  line-height: 17px;
  text-align: center;
  padding: 0 4px;
}

/* Dropdown panels */
.dropdown-panel {
  position: absolute;
  top: 48px;
  right: 0;
  width: 300px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(89, 102, 122, 0.18);
  overflow: hidden;
  z-index: 100;
  animation: slideDown 0.25s ease;
}
.dropdown-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(90, 103, 245, 0.08), rgba(90, 103, 245, 0.02));
  border-bottom: 1px solid #f0f2f5;
}
.dropdown-head h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1f2d3d;
}
.dropdown-panel ul {
  list-style: none;
  margin: 0;
  padding: 8px 0;
}
.dropdown-panel ul li {
  padding: 10px 16px;
  font-size: 13px;
  color: #5a6273;
  cursor: pointer;
  transition: background 0.2s;
}
.dropdown-panel ul li:hover {
  background: #f5f8ff;
}
.dropdown-panel ul li em {
  float: right;
  font-style: normal;
  font-size: 12px;
  color: #c0c4cc;
}
.dropdown-panel ul li .dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.check-all {
  display: block;
  text-align: center;
  padding: 12px;
  font-size: 13px;
  color: var(--theme-default, #5A67F5);
  border-top: 1px solid #f0f2f5;
  cursor: pointer;
}
.check-all:hover {
  background: #f5f8ff;
}

/* Profile */
.profile-item {
  position: relative;
  margin-left: 8px;
  cursor: pointer;
}
.profile-media {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px;
  border-radius: 10px;
  transition: background 0.2s;
}
.profile-media:hover {
  background: #f5f8ff;
}
.profile-avatar {
  background: linear-gradient(135deg, #5A67F5, #47A8FF);
  color: #fff;
  font-weight: 600;
}
.profile-info {
  line-height: 1.3;
}
.profile-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #2b2b2b;
}
.profile-role {
  margin: 0;
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.profile-dropdown {
  position: absolute;
  top: 52px;
  right: 0;
  width: 180px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(89, 102, 122, 0.15);
  list-style: none;
  margin: 0;
  padding: 8px;
  z-index: 100;
  animation: slideDown 0.25s ease;
}
.profile-dropdown li a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: #5a6273;
  cursor: pointer;
  transition: all 0.2s;
}
.profile-dropdown li a:hover {
  background: #f5f8ff;
  color: var(--theme-default, #5A67F5);
}
.profile-dropdown li a span {
  flex: 1;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* collapsed state */
@media (max-width: 768px) {
  .koho-header {
    left: 0;
  }
}
</style>