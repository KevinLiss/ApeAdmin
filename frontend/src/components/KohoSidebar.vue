<template>
  <aside class="koho-sidebar" :class="{ 'close-icon': collapsed }">
    <!-- Logo + toggle -->
    <div class="logo-wrapper" :class="{ 'logo-collapsed': collapsed }" @click="collapsed && $emit('toggle')">
      <div class="logo-inner">
        <el-icon :size="28" color="#409EFF"><Platform /></el-icon>
        <span class="brand-text">ApeAdmin</span>
      </div>
      <div class="toggle-sidebar" @click.stop="$emit('toggle')">
        <el-icon :size="18"><Expand v-if="collapsed" /><Fold v-else /></el-icon>
      </div>
    </div>

    <!-- Menu -->
    <nav class="sidebar-main">
      <ul class="sidebar-links">
        <!-- Dashboard -->
        <li class="sidebar-list">
          <router-link to="/dashboard" class="sidebar-link" :class="{ active: activeMenu === '/dashboard' }">
            <el-icon class="menu-icon"><Odometer /></el-icon>
            <span>仪表盘</span>
          </router-link>
        </li>

        <!-- Group: 系统管理 -->
        <li class="sidebar-main-title">
          <div><h4>系统管理</h4></div>
        </li>
        <li class="sidebar-list" v-for="item in systemMenus" :key="item.path">
          <router-link :to="item.path" class="sidebar-link" :class="{ active: activeMenu.startsWith(item.path) }">
            <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </router-link>
        </li>

        <!-- Group: MCP -->
        <li class="sidebar-main-title">
          <div><h4>MCP 体系</h4></div>
        </li>
        <li class="sidebar-list" v-for="item in mcpMenus" :key="item.path">
          <router-link :to="item.path" class="sidebar-link" :class="{ active: activeMenu.startsWith(item.path) }">
            <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
            <span>{{ item.title }}</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Bottom upgrade card (Koho sidebar-img-content) -->
    <div class="sidebar-footer">
      <div class="upgrade-card">
        <img class="upgrade-img" src="/koho/images/2.png" alt="" />
        <h5>体验更多功能</h5>
        <p>升级插件体系，解锁 AI 能力</p>
        <button class="upgrade-btn" @click="$emit('upgrade')">现在查看</button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

defineProps<{
  collapsed: boolean
}>()
defineEmits<{
  (e: 'toggle'): void
  (e: 'upgrade'): void
}>()

const route = useRoute()
const activeMenu = computed(() => route.path)

const systemMenus = [
  { title: '用户管理', path: '/system/user', icon: 'User' },
  { title: '角色管理', path: '/system/role', icon: 'UserFilled' },
  { title: '菜单管理', path: '/system/menu', icon: 'Menu' },
  { title: '部门管理', path: '/system/dept', icon: 'OfficeBuilding' },
]

const mcpMenus = [
  { title: '工具列表', path: '/mcp/tools', icon: 'Tools' },
  { title: '资源列表', path: '/mcp/resources', icon: 'FolderOpened' },
]
</script>

<style scoped>
/* ===== Koho 1:1 Sidebar ===== */
.koho-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 258px;
  background: #ffffff;
  z-index: 9;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 21px 0 rgba(89, 102, 122, 0.1);
  transition: width 0.3s ease;
  overflow: hidden;
}
/* Koho 1:1 collapsed: 86px icon-only mode */
.koho-sidebar.close-icon {
  width: 86px;
}
.koho-sidebar.close-icon .brand-text,
.koho-sidebar.close-icon .toggle-sidebar {
  display: none;
}
.koho-sidebar.close-icon .logo-wrapper {
  cursor: pointer;
  justify-content: center;
  padding: 22px 0;
}
.koho-sidebar.close-icon .logo-inner {
  justify-content: center;
}
.koho-sidebar.close-icon .sidebar-main-title,
.koho-sidebar.close-icon .sidebar-footer {
  display: none;
}
.koho-sidebar.close-icon .sidebar-link {
  justify-content: center;
  padding: 11px 0;
  margin: 2px 10px;
}
.koho-sidebar.close-icon .sidebar-link span {
  display: none;
}
.koho-sidebar.close-icon .sidebar-link.active::before {
  display: none;
}

/* Logo */
.logo-wrapper {
  padding: 22px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f3ff;
}
.logo-inner {
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand-text {
  font-size: 19px;
  font-weight: 700;
  color: #2b2b2b;
  letter-spacing: 0.3px;
}
.toggle-sidebar {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  color: #59667a;
  transition: all 0.2s;
}
.toggle-sidebar:hover {
  background: #eff3f9;
  color: var(--theme-default);
}

/* Menu container */
.sidebar-main {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
}
.sidebar-main::-webkit-scrollbar {
  width: 4px;
}
.sidebar-main::-webkit-scrollbar-thumb {
  background: #d8dde6;
  border-radius: 4px;
}
.sidebar-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Group title */
.sidebar-main-title {
  padding: 14px 16px 6px;
}
.sidebar-main-title > div {
  background-color: #eff3f9;
  padding: 8px 14px;
  border-radius: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sidebar-main-title h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.4px;
  color: var(--theme-default, #409eff);
}

/* Menu item */
.sidebar-list {
  position: relative;
  margin: 2px 0;
}
.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 20px;
  margin: 2px 12px;
  border-radius: 8px;
  color: #5a6273;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.25s ease;
  position: relative;
}
.sidebar-link .menu-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  color: #9993b4;
  transition: color 0.25s;
}
.sidebar-link:hover {
  background: #eff3f9;
  color: var(--theme-default, #409eff);
}
.sidebar-link:hover .menu-icon {
  color: var(--theme-default, #409eff);
}
.sidebar-link.active {
  background: var(--theme-default, #409eff);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}
.sidebar-link.active .menu-icon {
  color: #ffffff;
}
.sidebar-link.active::before {
  content: "";
  position: absolute;
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  border-radius: 3px;
  background: var(--theme-default, #409eff);
}

/* Footer upgrade card (Koho sidebar-img-content 1:1) */
.sidebar-footer {
  padding: 0 22px;
  margin-bottom: 24px;
}
.upgrade-card {
  background-color: #eff3f9;
  border-radius: 20px;
  text-align: center;
  padding-bottom: 20px;
  overflow: hidden;
}
.upgrade-img {
  margin-top: -18px;
  height: 92px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}
.upgrade-card h5 {
  margin: 6px 0 6px;
  font-size: 16px;
  font-weight: 500;
  line-height: 1.4;
  color: #2b2b2b;
}
.upgrade-card p {
  margin: 0 0 14px;
  font-size: 12px;
  color: #909399;
}
.upgrade-btn {
  border: none;
  background: var(--theme-default, #409eff);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.upgrade-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}
</style>