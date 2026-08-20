<template>
  <el-container class="layout">
    <!-- Sidebar -->
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon :size="22" color="#409EFF"><Platform /></el-icon>
        <span class="logo-text">ApeAdmin</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="menu"
        background-color="#001529"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>

        <el-sub-menu index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/user">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/system/role">
            <el-icon><UserFilled /></el-icon>
            <span>角色管理</span>
          </el-menu-item>
          <el-menu-item index="/system/menu">
            <el-icon><Menu /></el-icon>
            <span>菜单管理</span>
          </el-menu-item>
          <el-menu-item index="/system/dept">
            <el-icon><OfficeBuilding /></el-icon>
            <span>部门管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="mcp">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>MCP 管理</span>
          </template>
          <el-menu-item index="/mcp/tools">
            <el-icon><Tools /></el-icon>
            <span>工具列表</span>
          </el-menu-item>
          <el-menu-item index="/mcp/resources">
            <el-icon><FolderOpened /></el-icon>
            <span>资源列表</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- Main -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Expand v-if="collapsed" />
            <Fold v-else />
          </el-icon>
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="30" class="avatar">{{ userStore.nickname?.charAt(0) || 'A' }}</el-avatar>
              <span class="username">{{ userStore.nickname || userStore.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const collapsed = ref(false)

const pageTitle = computed(() => (route.meta.title as string) || 'ApeAdmin')

const activeMenu = computed(() => route.path)

function toggleCollapse() {
  collapsed.value = !collapsed.value
}

async function handleCommand(command: string) {
  if (command === 'logout') {
    await userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}
</script>

<style scoped>
.layout {
  height: 100%;
}
.aside {
  background-color: #001529;
  overflow-x: hidden;
  transition: width 0.2s;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}
.menu {
  border-right: none;
  --el-menu-item-height: 46px;
}
.menu :deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary);
}
.header {
  height: 60px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 1;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #666;
}
.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
}
.avatar {
  background-color: var(--el-color-primary);
  color: #fff;
}
.main {
  background-color: #f0f2f5;
  padding: 16px;
  overflow: auto;
}
</style>