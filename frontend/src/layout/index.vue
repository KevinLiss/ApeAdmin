<template>
  <div class="layout">
    <!-- Mobile overlay -->
    <Transition name="overlay-fade">
      <div v-if="isMobile && mobileSidebarOpen" class="sidebar-overlay" @click="closeMobileSidebar"></div>
    </Transition>

    <!-- ApeAdmin 1:1 Sidebar -->
    <ApeSidebar
      :collapsed="collapsed"
      :isMobile="isMobile"
      :mobileOpen="mobileSidebarOpen"
      @toggle="toggleCollapse"
      @upgrade="onUpgrade"
      @close-mobile="closeMobileSidebar"
    />

    <!-- Main column: header + content, offset by sidebar width -->
    <div class="layout-main" :class="{ 'is-collapsed': collapsed && !isMobile, 'is-mobile': isMobile }">
      <ApeHeader
        :isDark="isDark"
        :collapsed="collapsed"
        :isMobile="isMobile"
        @toggle-theme="toggleTheme"
        @profile="onProfile"
        @settings="onSettings"
        @logout="onLogout"
        @toggle-mobile-sidebar="toggleMobileSidebar"
      />

      <main class="main" :class="{ 'apeui-content': isApeui }">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import ApeSidebar from '@/components/ApeSidebar.vue'
import ApeHeader from '@/components/ApeHeader.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const collapsed = ref(false)
const isDark = ref(false)
const isMobile = ref(false)
const mobileSidebarOpen = ref(false)

// 检测当前是否在 APEUI 库路由下
const isApeui = computed(() => route.path.startsWith('/apeui'))

// 响应式检测：≤1199px 为移动端
function checkMobile() {
  const w = window.innerWidth
  isMobile.value = w <= 1199
  if (isMobile.value) {
    mobileSidebarOpen.value = false
    collapsed.value = false
  } else if (w <= 1600) {
    // 1200-1600px：桌面端图标折叠模式，为内容区腾出更多空间
    collapsed.value = true
  } else {
    // >1600px：完全展开
    collapsed.value = false
  }
}

function toggleCollapse() {
  collapsed.value = !collapsed.value
}

function toggleMobileSidebar() {
  mobileSidebarOpen.value = !mobileSidebarOpen.value
}

function closeMobileSidebar() {
  mobileSidebarOpen.value = false
}

// 路由变化时自动关闭移动端侧边栏
watch(() => route.path, () => {
  if (isMobile.value) mobileSidebarOpen.value = false
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

function toggleTheme() {
  isDark.value = !isDark.value
  ElMessage.info(isDark.value ? '已切换深色模式（占位）' : '已切换浅色模式')
}

function onUpgrade() {
  ElMessage.info('升级功能开发中，敬请期待')
}

function onProfile() {
  router.push('/profile')
}

function onSettings() {
  router.push('/system/settings')
}

async function onLogout() {
  await userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: row;
  overflow: hidden;
}
.layout-main {
  height: 100vh;
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding-left: 258px;
  transition: padding-left 0.3s ease;
}
.layout-main.is-collapsed {
  padding-left: 86px;
}
.layout-main.is-mobile {
  padding-left: 0;
}
.main {
  flex: 1;
  background-color: var(--theme-body-bg, #eff3f9);
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  margin-top: 64px;
  min-height: 0;
}

/* Mobile overlay */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  z-index: 8;
  cursor: pointer;
}
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.25s ease;
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}

/* Responsive: content area */
@media (max-width: 991px) {
  .main {
    padding: 15px;
  }
}
@media (max-width: 575px) {
  .main {
    padding: 12px;
    margin-top: 56px;
  }
}
</style>