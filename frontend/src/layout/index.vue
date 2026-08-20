<template>
  <div class="layout">
    <!-- Koho 1:1 Sidebar -->
    <KohoSidebar :collapsed="collapsed" @toggle="toggleCollapse" @upgrade="onUpgrade" />

    <!-- Main column: header + content, offset by sidebar width -->
    <div class="layout-main" :class="{ 'is-collapsed': collapsed }">
      <KohoHeader :is-dark="isDark" @toggle-theme="toggleTheme" @profile="onProfile" @settings="onSettings" @logout="onLogout" />

      <main class="main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import KohoSidebar from '@/components/KohoSidebar.vue'
import KohoHeader from '@/components/KohoHeader.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const collapsed = ref(false)
const isDark = ref(false)

function toggleCollapse() {
  collapsed.value = !collapsed.value
}

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
}
.layout-main {
  min-height: 100vh;
  margin-left: 258px;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}
.layout-main.is-collapsed {
  margin-left: 86px;
}
.main {
  flex: 1;
  background-color: var(--theme-body-bg, #eff3f9);
  padding: 20px;
  overflow: auto;
  margin-top: 64px;
}
</style>