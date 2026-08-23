<template>
  <header class="ape-header" :class="{ 'close-icon': collapsed && !isMobile, 'is-mobile': isMobile }">
    <div class="header-wrapper">
      <!-- Mobile hamburger -->
      <div v-if="isMobile" class="hamburger-btn" @click="$emit('toggle-mobile-sidebar')">
        <el-icon :size="22"><Menu /></el-icon>
      </div>

      <!-- Search -->
      <div class="left-header">
        <!-- Desktop: inline search -->
        <div v-if="!isMobile" class="search-box">
          <input class="search-input" type="text" placeholder="搜索页面，如：用户、角色、菜单..." v-model="keyword" @input="onSearchInput" @keyup.enter="onSearch" @focus="onSearchInput" @keydown.down.prevent="moveHighlight(1)" @keydown.up.prevent="moveHighlight(-1)" />
          <span class="search-icon" @click="onSearch"><el-icon :size="16"><Search /></el-icon></span>
          <!-- 搜索结果下拉面板 -->
          <div v-if="keyword.trim() && searchResults.length" class="search-dropdown">
            <div class="search-dropdown-head">搜索结果（{{ searchResults.length }}）</div>
            <ul class="search-dropdown-list">
              <li v-for="(item, i) in searchResults" :key="item.path" :class="{ active: i === highlightIndex }" @click="goToPage(item)" @mouseenter="highlightIndex = i">
                <el-icon class="search-item-icon" :size="16"><component :is="item.icon || 'Document'" /></el-icon>
                <span class="search-item-title" v-html="item.titleHighlighted"></span>
                <span class="search-item-path">{{ item.path }}</span>
              </li>
            </ul>
          </div>
        </div>
        <!-- Mobile: icon search -->
        <div v-else class="mobile-search" @click="mobileSearchOpen = !mobileSearchOpen">
          <el-icon :size="20"><Search /></el-icon>
          <Transition name="search-slide">
            <input v-if="mobileSearchOpen" class="mobile-search-input" type="text" placeholder="搜索..." v-model="keyword" @input="onSearchInput" @keyup.enter="onSearch" ref="mobileSearchRef" />
          </Transition>
          <!-- 移动端搜索结果 -->
          <div v-if="keyword.trim() && searchResults.length" class="search-dropdown mobile-search-dropdown">
            <ul class="search-dropdown-list">
              <li v-for="(item, i) in searchResults" :key="item.path" @click="goToPage(item); mobileSearchOpen = false">
                <span class="search-item-title" v-html="item.titleHighlighted"></span>
                <span class="search-item-path">{{ item.path }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Right icons -->
      <div class="nav-right">
        <ul class="nav-menus">
          <!-- Theme toggle -->
          <li class="icon-item" @click="$emit('toggle-theme')">
            <el-icon :size="18"><Moon v-if="!isDark" /><Sunny v-else /></el-icon>
          </li>

          <!-- Bookmark (hidden on mobile ≤575px) -->
          <li v-if="!isMobile || windowWidth > 575" class="icon-item" @click="bookmarkVisible = !bookmarkVisible">
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

          <!-- Messages (hidden on mobile ≤767px) -->
          <li v-if="!isMobile || windowWidth > 767" class="icon-item" @click="msgVisible = !msgVisible">
            <el-icon :size="18"><ChatDotRound /></el-icon>
          </li>

          <!-- Fullscreen (hidden on mobile) -->
          <li v-if="!isMobile" class="icon-item" @click="toggleFullscreen">
            <el-icon :size="18"><FullScreen /></el-icon>
          </li>

          <!-- Profile -->
          <li class="profile-nav" @click="profileVisible = !profileVisible">
            <div class="profile-media">
              <el-avatar :size="38" class="profile-avatar">{{ avatarText }}</el-avatar>
              <div v-if="!isMobile || windowWidth > 810" class="profile-info">
                <span class="profile-name">{{ userStore.username || userStore.nickname || 'Admin' }}</span>
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
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const props = defineProps<{
  isDark?: boolean
  collapsed?: boolean
  isMobile?: boolean
}>()
const emit = defineEmits<{
  (e: 'toggle-theme'): void
  (e: 'profile'): void
  (e: 'settings'): void
  (e: 'logout'): void
  (e: 'toggle-mobile-sidebar'): void
}>()

const router = useRouter()
const userStore = useUserStore()

const keyword = ref('')
const bookmarkVisible = ref(false)
const notifVisible = ref(false)
const msgVisible = ref(false)
const profileVisible = ref(false)
const mobileSearchOpen = ref(false)
const mobileSearchRef = ref<HTMLInputElement>()
const windowWidth = ref(window.innerWidth)

// Watch mobile search open state to auto-focus
import { watch } from 'vue'
watch(mobileSearchOpen, async (val) => {
  if (val) {
    await nextTick()
    mobileSearchRef.value?.focus()
  }
})

// Close dropdowns on outside click
function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.has-badge')) notifVisible.value = false
  if (!target.closest('.profile-nav')) profileVisible.value = false
}

onMounted(() => {
  window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

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
  if (keyword.value.trim() && searchResults.value.length) {
    goToPage(searchResults.value[0])
  }
}

// ===== 搜索功能 =====
const searchResults = ref<any[]>([])
const highlightIndex = ref(-1)

// 获取所有可搜索的路由
function getSearchableRoutes(): any[] {
  const routes = router.getRoutes()
  const results: any[] = []
  for (const route of routes) {
    const title = route.meta?.title as string
    const path = route.path
    // 只搜索 Layout 的子路由（有 title 的实际页面），排除 404 / 登录等
    if (title && !path.startsWith('/login') && !path.startsWith('/404') && path !== '/' && !path.includes(':pathMatch')) {
      results.push({
        title,
        path,
        icon: route.meta?.icon || 'Document',
      })
    }
  }
  return results
}

function onSearchInput() {
  highlightIndex.value = -1
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) {
    searchResults.value = []
    return
  }
  const allRoutes = getSearchableRoutes()
  const matched = allRoutes
    .filter(r => r.title.toLowerCase().includes(kw) || r.path.toLowerCase().includes(kw))
    .slice(0, 8)
  // 高亮关键词
  searchResults.value = matched.map(r => ({
    ...r,
    titleHighlighted: r.title.replace(
      new RegExp(`(${kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'),
      '<mark>$1</mark>'
    ),
  }))
}

function moveHighlight(direction: number) {
  if (!searchResults.value.length) return
  highlightIndex.value = Math.max(-1, Math.min(searchResults.value.length - 1, highlightIndex.value + direction))
}

function goToPage(item: any) {
  keyword.value = ''
  searchResults.value = []
  highlightIndex.value = -1
  router.push(item.path)
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
/* ===== ApeAdmin 1:1 Header ===== */
.ape-header {
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
.ape-header.close-icon {
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
.search-box {
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

/* Search dropdown */
.search-dropdown {
  position: absolute;
  top: 48px;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(89, 102, 122, 0.18);
  overflow: hidden;
  z-index: 100;
  animation: slideDown 0.2s ease;
}
.search-dropdown-head {
  padding: 10px 16px;
  font-size: 12px;
  color: #909399;
  border-bottom: 1px solid #f0f2f5;
}
.search-dropdown-list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
  max-height: 320px;
  overflow-y: auto;
}
.search-dropdown-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.15s;
}
.search-dropdown-list li:hover,
.search-dropdown-list li.active {
  background: #f5f8ff;
}
.search-item-icon {
  color: #5A67F5;
  flex-shrink: 0;
}
.search-item-title {
  font-size: 14px;
  color: #2b2b2b;
  flex: 1;
}
.search-item-title mark {
  background: rgba(90, 103, 245, 0.15);
  color: #5A67F5;
  border-radius: 2px;
  padding: 0 2px;
}
.search-item-path {
  font-size: 11px;
  color: #c0c4cc;
  white-space: nowrap;
}
.mobile-search-dropdown {
  top: 38px;
  width: 100%;
  min-width: 260px;
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

/* ===== Mobile responsive ===== */

/* Hamburger button (mobile only) */
.hamburger-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  color: #59667a;
  background: #eff3f9;
  margin-right: 10px;
  flex-shrink: 0;
  transition: all 0.2s;
}
.hamburger-btn:hover {
  background: rgba(90, 103, 245, 0.1);
  color: var(--theme-default, #5A67F5);
}

/* Mobile search */
.mobile-search {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #59667a;
  flex: 1;
}
.mobile-search:hover {
  color: var(--theme-default, #5A67F5);
}
.mobile-search-input {
  flex: 1;
  height: 38px;
  border: 1px solid #eef0f4;
  border-radius: 8px;
  padding: 0 12px;
  font-size: 14px;
  background: #f8fafc;
  outline: none;
  max-width: 200px;
}
.mobile-search-input:focus {
  border-color: var(--theme-default, #5A67F5);
  box-shadow: 0 0 0 3px rgba(90, 103, 245, 0.12);
}
.search-slide-enter-active,
.search-slide-leave-active {
  transition: all 0.25s ease;
}
.search-slide-enter-from,
.search-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* ≤1199px: mobile header */
@media (max-width: 1199px) {
  .ape-header {
    left: 0;
  }
  .ape-header.is-mobile .header-wrapper {
    padding: 0 12px;
  }
  .ape-header.is-mobile .left-header {
    max-width: none;
  }
  .ape-header.is-mobile .icon-item {
    width: 36px;
    height: 36px;
  }
  .ape-header.is-mobile .nav-menus {
    gap: 4px;
  }
}

/* ≤991px: tablet */
@media (max-width: 991px) {
  .ape-header.is-mobile .icon-item {
    width: 34px;
    height: 34px;
  }
  .ape-header.is-mobile .dropdown-panel {
    width: 280px;
  }
}

/* ≤767px: large phone */
@media (max-width: 767px) {
  .ape-header.is-mobile .header-wrapper {
    padding: 0 10px;
  }
  .ape-header.is-mobile .icon-item {
    width: 32px;
    height: 32px;
  }
  .ape-header.is-mobile .profile-avatar {
    --el-avatar-size: 34px;
  }
  .ape-header.is-mobile .dropdown-panel {
    position: fixed;
    width: calc(100vw - 20px);
    right: 10px;
  }
}

/* ≤575px: small phone */
@media (max-width: 575px) {
  .ape-header.is-mobile .header-wrapper {
    padding: 0 8px;
  }
  .ape-header.is-mobile .icon-item {
    width: 30px;
    height: 30px;
  }
  .ape-header.is-mobile .profile-dropdown {
    position: fixed;
    width: calc(100vw - 20px);
    right: 10px;
  }
  .ape-header.is-mobile .badge-num {
    min-width: 15px;
    height: 15px;
    font-size: 10px;
    line-height: 15px;
  }
}

</style>

<style>
/* ===== 深色模式适配（非 scoped，避免 Vite 压缩拆分选择器） ===== */
html.dark .ape-header {
  background: #232838;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.35);
}
html.dark .search-input {
  background: #2e3344;
  border-color: #3a3f52;
  color: #e6e8f0;
}
html.dark .search-input:focus {
  background: #2e3344;
  border-color: #7F8AF8;
  box-shadow: 0 0 0 3px rgba(127, 138, 248, 0.15);
}
html.dark .icon-item {
  color: #b8bdd0;
}
html.dark .icon-item:hover {
  background: #2e3344;
  color: #7F8AF8;
}
html.dark .profile-name {
  color: #e6e8f0;
}
html.dark .profile-role {
  color: #8a90a8;
}
html.dark .dropdown-panel,
html.dark .profile-dropdown {
  background: #262b3d;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.45);
}
html.dark .dropdown-head {
  background: linear-gradient(135deg, rgba(127, 138, 248, 0.12), rgba(127, 138, 248, 0.03));
  border-bottom-color: #36394a;
}
html.dark .dropdown-head h3 {
  color: #e6e8f0;
}
html.dark .dropdown-panel ul li {
  color: #b8bdd0;
}
html.dark .dropdown-panel ul li:hover {
  background: #2e3344;
}
html.dark .dropdown-panel ul li em {
  color: #6b7089;
}
html.dark .check-all {
  border-top-color: #36394a;
}
html.dark .check-all:hover {
  background: #2e3344;
}
html.dark .profile-media:hover {
  background: #2e3344;
}
html.dark .profile-dropdown li a {
  color: #b8bdd0;
}
html.dark .profile-dropdown li a:hover {
  background: #2e3344;
  color: #7F8AF8;
}
html.dark .hamburger-btn {
  background: #2e3344;
  color: #b8bdd0;
}
html.dark .hamburger-btn:hover {
  background: rgba(127, 138, 248, 0.15);
  color: #7F8AF8;
}
html.dark .search-dropdown {
  background: #262b3d;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.45);
}
html.dark .search-dropdown-head {
  color: #8a90a8;
  border-bottom-color: #36394a;
}
html.dark .search-dropdown-list li:hover,
html.dark .search-dropdown-list li.active {
  background: #2e3344;
}
html.dark .search-item-icon {
  color: #7F8AF8;
}
html.dark .search-item-title {
  color: #e6e8f0;
}
html.dark .search-item-title mark {
  background: rgba(127, 138, 248, 0.2);
  color: #7F8AF8;
}
html.dark .search-item-path {
  color: #6b7089;
}
</style>