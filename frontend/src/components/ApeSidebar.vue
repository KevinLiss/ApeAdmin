<template>
  <aside
    class="ape-sidebar"
    :class="{
      'close-icon': collapsed && !isMobile,
      'mobile-open': isMobile && mobileOpen,
      'mobile-hidden': isMobile && !mobileOpen
    }"
  >
    <!-- Logo + toggle -->
    <div class="logo-wrapper" :class="{ 'logo-collapsed': collapsed && !isMobile }" @click="(collapsed && !isMobile) && $emit('toggle')">
      <div class="logo-inner">
        <img src="/assets/images/logo-icon.png" alt="Logo" class="brand-logo" />
        <span class="brand-text">ApeAdmin</span>
      </div>
      <!-- Desktop: toggle button -->
      <div v-if="!isMobile" class="toggle-sidebar" @click.stop="$emit('toggle')">
        <el-icon :size="18"><Expand v-if="collapsed" /><Fold v-else /></el-icon>
      </div>
      <!-- Mobile: close button -->
      <div v-else class="toggle-sidebar mobile-close-btn" @click.stop="$emit('close-mobile')">
        <el-icon :size="18"><Close /></el-icon>
      </div>
    </div>

    <!-- Menu -->
    <nav class="sidebar-main">
      <!-- 动态菜单渲染 -->
      <template v-for="menu in menuTree" :key="menu.id">
        <!-- 顶级菜单 (type=C, 直接在根级别): 直接渲染 -->
        <ul v-if="menu.type === 'C' && menu.component" class="sidebar-links">
          <li class="sidebar-list">
            <router-link :to="resolvePath('', menu.path)" class="sidebar-link" :class="{ active: activeMenu === resolvePath('', menu.path) }">
              <el-icon class="menu-icon"><component :is="menu.icon || 'Menu'" /></el-icon>
              <span>{{ menu.name }}</span>
            </router-link>
          </li>
        </ul>

        <!-- 顶级目录 (type=M): 渲染为可折叠分组 -->
        <ul v-else-if="menu.type === 'M' && menu.children?.length" class="sidebar-links">
          <li class="sidebar-main-title sidebar-group-toggle" @click="toggleTopMenu(menu.id)">
            <div>
              <h4>{{ menu.name }}</h4>
              <el-icon class="sub-arrow" :class="{ open: isTopMenuOpen(menu.id) }"><ArrowDown /></el-icon>
            </div>
          </li>
          <li
            v-for="child in menu.children.filter((c: any) => c.type !== 'F')"
            v-show="isTopMenuOpen(menu.id)"
            :key="child.id"
            class="sidebar-list"
            @mouseenter="collapsed && !isMobile && (hoverSub = child.id)"
            @mouseleave="collapsed && !isMobile && (hoverSub = null)"
          >
            <!-- 有子菜单的 C 类型菜单（如未来扩展三级菜单） -->
            <template v-if="child.children?.some((c: any) => c.type !== 'F')">
              <a class="sidebar-link sidebar-title" href="javascript:void(0)" @click="toggleSub(child.id)">
                <el-icon class="menu-icon"><component :is="child.icon || 'Menu'" /></el-icon>
                <span>{{ child.name }}</span>
                <el-icon class="sub-arrow" :class="{ open: openedSub === child.id }"><ArrowDown /></el-icon>
              </a>
              <!-- Expanded: inline submenu -->
              <ul class="sidebar-submenu" v-show="openedSub === child.id">
                <li v-for="grandchild in child.children.filter((c: any) => c.type !== 'F')" :key="grandchild.id">
                  <router-link :to="resolvePath(menu.path, child.path, grandchild.path)" :class="{ active: route.path === resolvePath(menu.path, child.path, grandchild.path) }">
                    {{ grandchild.name }}
                  </router-link>
                </li>
              </ul>
              <!-- Collapsed: flyout submenu -->
              <div class="flyout-submenu" v-if="collapsed && !isMobile && hoverSub === child.id">
                <h6>{{ child.name }}</h6>
                <ul>
                  <li v-for="grandchild in child.children.filter((c: any) => c.type !== 'F')" :key="grandchild.id">
                    <router-link :to="resolvePath(menu.path, child.path, grandchild.path)" :class="{ active: route.path === resolvePath(menu.path, child.path, grandchild.path) }">
                      {{ grandchild.name }}
                    </router-link>
                  </li>
                </ul>
              </div>
            </template>
            <!-- 无子菜单的菜单项 (type=C, 只有 F 类按钮子节点) -->
            <template v-else>
              <router-link :to="resolvePath(menu.path, child.path)" class="sidebar-link" :class="{ active: activeMenu === resolvePath(menu.path, child.path) }">
                <el-icon class="menu-icon"><component :is="child.icon || 'Menu'" /></el-icon>
                <span>{{ child.name }}</span>
              </router-link>
            </template>
          </li>
        </ul>
      </template>
    </nav>

    <!-- Bottom upgrade card -->
    <div class="sidebar-footer">
      <div class="upgrade-card">
        <img class="upgrade-img" src="/assets/images/sidebar/2.png" alt="" />
        <h5>全能助手</h5>
        <p>告别传统，AI全面接管系统</p>
        <button class="upgrade-btn" @click="goAiChat">前往体验</button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const props = defineProps<{
  collapsed: boolean
  isMobile?: boolean
  mobileOpen?: boolean
}>()
defineEmits<{
  (e: 'toggle'): void
  (e: 'upgrade'): void
  (e: 'close-mobile'): void
}>()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const activeMenu = computed(() => route.path)
const openedSub = ref<string | number | null>(null)
const hoverSub = ref<string | number | null>(null)
// 顶级 M 目录的折叠状态（key=菜单 id，value=是否展开）
const openedTopMenus = ref<Record<string | number, boolean>>({})

// 子菜单数量超过该值则默认收起（避免大量子菜单平铺过长）
const DEFAULT_COLLAPSE_THRESHOLD = 12

// 过滤掉 F 类型（按钮），只保留 M/C 用于侧边栏渲染
const menuTree = computed(() => {
  return (userStore.menus || []).filter((m: any) => m.type !== 'F')
})

// 判断当前路由是否命中某顶级目录下的菜单
function topMenuHasActive(menu: any): boolean {
  if (menu.type === 'C' && menu.component) {
    return activeMenu.value === resolvePath('', menu.path)
  }
  if (menu.type !== 'M') return false
  const children = menu.children || []
  // 直接子项
  for (const child of children) {
    if (child.type === 'F') continue
    if (child.children?.some((c: any) => c.type !== 'F')) {
      // 三级子菜单
      for (const grandchild of child.children) {
        if (grandchild.type === 'F') continue
        if (resolvePath(menu.path, child.path, grandchild.path) === activeMenu.value) return true
      }
    } else {
      if (resolvePath(menu.path, child.path) === activeMenu.value) return true
    }
  }
  return false
}

// 初始化顶级菜单默认展开状态：子菜单少的展开，多的收起；命中当前路由的强制展开
watch(
  menuTree,
  (tree) => {
    const next: Record<string | number, boolean> = {}
    for (const menu of tree) {
      if (menu.type !== 'M' || !menu.children?.length) continue
      const visibleChildren = (menu.children || []).filter((c: any) => c.type !== 'F')
      const hasActive = topMenuHasActive(menu)
      const shouldOpen = hasActive || visibleChildren.length <= DEFAULT_COLLAPSE_THRESHOLD
      next[menu.id] = shouldOpen
    }
    openedTopMenus.value = next
  },
  { immediate: true }
)

// 顶级目录展开/收起
function isTopMenuOpen(id: string | number): boolean {
  return openedTopMenus.value[id] !== false
}
function toggleTopMenu(id: string | number) {
  // 折叠侧边栏模式下由 hover flyout 接管，不展开 inline 子菜单
  if (props.collapsed && !props.isMobile) return
  openedTopMenus.value = {
    ...openedTopMenus.value,
    [id]: !isTopMenuOpen(id),
  }
}

function toggleSub(id: string | number) {
  // 折叠状态下不展开 inline 子菜单（宽度不足以展示），由 hover flyout 接管
  if (props.collapsed && !props.isMobile) {
    openedSub.value = null
    return
  }
  openedSub.value = openedSub.value === id ? null : id
}

// 点击推广卡片按钮：跳转到 AI 全能助手
function goAiChat() {
  router.push('/ai/chat')
}

/**
 * 拼接路由路径
 * 顶级目录 path 如 "/system"，子菜单 path 如 "user" → "/system/user"
 * 如果子菜单 path 已含 "/" 前缀则直接使用
 */
function resolvePath(parentPath: string, ...childPaths: string[]): string {
  const parts: string[] = []
  if (parentPath && parentPath !== '/') {
    parts.push(parentPath.replace(/^\/+|\/+$/g, ''))
  }
  for (const p of childPaths) {
    if (p) {
      parts.push(p.replace(/^\/+|\/+$/g, ''))
    }
  }
  return '/' + parts.filter(Boolean).join('/')
}
</script>

<style scoped>
/* ===== ApeAdmin 1:1 Sidebar ===== */
.ape-sidebar {
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
.ape-sidebar.close-icon {
  overflow: visible;
  width: 86px;
}
.ape-sidebar.close-icon .brand-text,
.ape-sidebar.close-icon .toggle-sidebar {
  display: none;
}
.ape-sidebar.close-icon .logo-wrapper {
  cursor: pointer;
  justify-content: center;
  padding: 22px 0;
}
.ape-sidebar.close-icon .logo-inner {
  justify-content: center;
}
.ape-sidebar.close-icon .sidebar-main-title,
.ape-sidebar.close-icon .sidebar-footer {
  display: none;
}
.ape-sidebar.close-icon .sidebar-link {
  justify-content: center;
  padding: 11px 0;
  margin: 2px 10px;
}
.ape-sidebar.close-icon .sidebar-link span {
  display: none;
}
.ape-sidebar.close-icon .sidebar-link.active::before {
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
.brand-logo {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 6px;
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
.ape-sidebar.close-icon .sidebar-main {
  overflow: visible;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.sidebar-group-toggle {
  cursor: pointer;
  user-select: none;
}
.sidebar-group-toggle:hover > div {
  background-color: #e6eaf3;
}
.sidebar-main-title h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.4px;
  color: var(--theme-default, #5A67F5);
}
.sidebar-main-title .sub-arrow {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}
.sidebar-main-title .sub-arrow.open {
  transform: rotate(180deg);
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
  color: var(--theme-default, #5A67F5);
}
.sidebar-link:hover .menu-icon {
  color: var(--theme-default, #5A67F5);
}
.sidebar-link.active {
  background: var(--theme-default, #5A67F5);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(90, 103, 245, 0.3);
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
  background: var(--theme-default, #5A67F5);
}

/* Footer upgrade card — 紧凑样式，避免挤占菜单空间 */
.sidebar-footer {
  padding: 0 16px;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.upgrade-card {
  background-color: #eff3f9;
  border-radius: 16px;
  text-align: center;
  padding: 14px 12px 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.upgrade-img {
  height: 56px;
  display: block;
  margin: 0 auto 2px;
}
.upgrade-card h5 {
  margin: 4px 0 2px;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
  color: #2b2b2b;
}
.upgrade-card p {
  margin: 0 0 8px;
  font-size: 11px;
  color: #909399;
  line-height: 1.3;
}
.upgrade-btn {
  border: none;
  background: var(--theme-default, #5A67F5);
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  padding: 6px 18px;
  border-radius: 7px;
  cursor: pointer;
  transition: all 0.2s;
}
.upgrade-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(90, 103, 245, 0.3);
}

/* Submenu title (expandable) */
.sidebar-title {
  cursor: pointer;
  justify-content: space-between;
}
.sub-arrow {
  transition: transform 0.3s ease;
  font-size: 12px;
  color: #909399;
}
.sub-arrow.open {
  transform: rotate(180deg);
}

/* Submenu items */
.sidebar-submenu {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 500px;
  overflow-y: auto;
  transition: max-height 0.3s ease;
}
.sidebar-submenu li a {
  display: block;
  padding: 8px 20px 8px 52px;
  margin: 2px 12px;
  font-size: 13px;
  color: #5a6273;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
}
/* Subgroup title inside expanded submenu */
.sidebar-submenu .submenu-title {
  padding: 12px 16px 2px 36px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--theme-default, #5A67F5);
  text-transform: uppercase;
}
.sidebar-submenu .submenu-title:first-child {
  padding-top: 4px;
}
.sidebar-submenu li a:hover {
  background: #eff3f9;
  color: var(--el-color-primary, #5A67F5);
}
.sidebar-submenu li a.active {
  color: var(--el-color-primary, #5A67F5);
  font-weight: 600;
  background: rgba(90, 103, 245, 0.08);
}

/* Collapsed: hide inline submenus, use flyout instead */
.ape-sidebar.close-icon .sidebar-list .sidebar-submenu,
.ape-sidebar.close-icon .sidebar-list .sub-arrow {
  display: none;
}

/* Flyout submenu (collapsed mode hover) */
.flyout-submenu {
  position: absolute;
  left: 86px;
  top: 0;
  min-width: 180px;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(89, 102, 122, 0.18);
  padding: 10px;
  z-index: 100;
  animation: flyoutIn 0.2s ease;
}
.flyout-submenu::-webkit-scrollbar {
  width: 4px;
}
.flyout-submenu::-webkit-scrollbar-thumb {
  background: #d8dde6;
  border-radius: 4px;
}
.flyout-submenu h6 {
  margin: 0 0 8px;
  padding: 4px 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--theme-default, #5A67F5);
  border-bottom: 1px solid #f0f2f5;
  padding-bottom: 8px;
}
/* Subgroup title inside flyout */
.flyout-subgroup-title {
  margin: 8px 0 2px;
  padding: 4px 12px 2px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
  color: var(--theme-default, #5A67F5);
  text-transform: uppercase;
  border-bottom: 1px solid #f0f2f5;
  padding-bottom: 6px;
}
.flyout-subgroup-title:first-child {
  margin-top: 0;
}
.flyout-submenu ul {
  list-style: none;
  margin: 0;
  padding: 4px 0;
}
.flyout-submenu ul li a {
  display: block;
  padding: 8px 12px;
  font-size: 13px;
  color: #5a6273;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
}
.flyout-submenu ul li a:hover {
  background: #eff3f9;
  color: var(--theme-default, #5A67F5);
}
.flyout-submenu ul li a.active {
  color: var(--theme-default, #5A67F5);
  font-weight: 600;
  background: rgba(90, 103, 245, 0.08);
}
@keyframes flyoutIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}

/* Mobile: drawer mode */
.ape-sidebar.mobile-hidden {
  transform: translateX(-285px);
}
.ape-sidebar.mobile-open {
  transform: translateX(0);
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.15);
}
.mobile-close-btn {
  background: rgba(90, 103, 245, 0.1);
  color: var(--theme-default, #5A67F5);
}
.mobile-close-btn:hover {
  background: rgba(90, 103, 245, 0.2);
}

</style>

<style>
/* ===== 深色模式适配（非 scoped，避免 Vite 压缩拆分选择器） ===== */
html.dark .ape-sidebar {
  background: #232838;
  box-shadow: 0 0 21px 0 rgba(0, 0, 0, 0.35);
}
html.dark .ape-sidebar .brand-text {
  color: #e6e8f0;
}
html.dark .flyout-submenu {
  background: #262b3d;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}
html.dark .flyout-submenu ul li a:hover {
  background: #2e3344;
}
html.dark .flyout-submenu::-webkit-scrollbar-thumb {
  background: #4a5066;
}
html.dark .upgrade-card {
  background-color: #2e3344;
}
html.dark .upgrade-card h5 {
  color: #e6e8f0;
}
html.dark .upgrade-card p {
  color: #8a90a8;
}
</style>
