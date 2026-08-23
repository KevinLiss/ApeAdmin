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
      <!-- 系统仪表盘（独立一级菜单，置顶） -->
      <ul class="sidebar-links">
        <li class="sidebar-list">
          <router-link to="/dashboard-monitor" class="sidebar-link" :class="{ active: activeMenu === '/dashboard-monitor' }">
            <el-icon class="menu-icon"><Monitor /></el-icon>
            <span>系统仪表盘</span>
          </router-link>
        </li>
      </ul>

      <!-- APEUI 组件库（静态菜单，分组作为可折叠二级菜单，不走后端） -->
      <template v-for="group in apeuiMenuGroups" :key="group.title">
        <ul class="sidebar-links">
          <li
            class="sidebar-list"
            @mouseenter="collapsed && !isMobile && (hoverSub = group.title)"
            @mouseleave="collapsed && !isMobile && (hoverSub = null)"
          >
            <!-- 分组标题：点击折叠/展开二级菜单 -->
            <a class="sidebar-link sidebar-title" href="javascript:void(0)" @click="toggleSub(group.title)">
              <el-icon class="menu-icon"><component :is="group.icon || 'Menu'" /></el-icon>
              <span>{{ group.title }}</span>
              <el-icon class="sub-arrow" :class="{ open: openedSub === group.title }"><ArrowDown /></el-icon>
            </a>
            <!-- Expanded: inline submenu -->
            <ul class="sidebar-submenu" v-show="openedSub === group.title">
              <template v-for="sub in group.subgroups" :key="sub.title">
                <li class="submenu-title">{{ sub.title }}</li>
                <li v-for="item in sub.items" :key="item.path">
                  <router-link :to="item.path" :class="{ active: route.path === item.path }">
                    {{ item.title }}
                  </router-link>
                </li>
              </template>
            </ul>
            <!-- Collapsed: flyout submenu -->
            <div class="flyout-submenu" v-if="collapsed && !isMobile && hoverSub === group.title">
              <h6>{{ group.title }}</h6>
              <template v-for="sub in group.subgroups" :key="sub.title">
                <div class="flyout-subgroup-title">{{ sub.title }}</div>
                <ul>
                  <li v-for="item in sub.items" :key="item.path">
                    <router-link :to="item.path" :class="{ active: route.path === item.path }">
                      {{ item.title }}
                    </router-link>
                  </li>
                </ul>
              </template>
            </div>
          </li>
        </ul>
      </template>

      <!-- 动态菜单渲染 -->
      <template v-for="menu in menuTree" :key="menu.id">
        <!-- 顶级目录 (type=M): 渲染为带子菜单的分组 -->
        <ul v-if="menu.type === 'M' && menu.children?.length" class="sidebar-links">
          <li class="sidebar-main-title">
            <div><h4>{{ menu.name }}</h4></div>
          </li>
          <li
            v-for="child in menu.children.filter(c => c.type !== 'F')"
            :key="child.id"
            class="sidebar-list"
            @mouseenter="collapsed && !isMobile && (hoverSub = child.id)"
            @mouseleave="collapsed && !isMobile && (hoverSub = null)"
          >
            <!-- 有子菜单的 C 类型菜单（如未来扩展三级菜单） -->
            <template v-if="child.children?.some(c => c.type !== 'F')">
              <a class="sidebar-link sidebar-title" href="javascript:void(0)" @click="toggleSub(child.id)">
                <el-icon class="menu-icon"><component :is="child.icon || 'Menu'" /></el-icon>
                <span>{{ child.name }}</span>
                <el-icon class="sub-arrow" :class="{ open: openedSub === child.id }"><ArrowDown /></el-icon>
              </a>
              <!-- Expanded: inline submenu -->
              <ul class="sidebar-submenu" v-show="openedSub === child.id">
                <li v-for="grandchild in child.children.filter(c => c.type !== 'F')" :key="grandchild.id">
                  <router-link :to="resolvePath(menu.path, child.path, grandchild.path)" :class="{ active: route.path === resolvePath(menu.path, child.path, grandchild.path) }">
                    {{ grandchild.name }}
                  </router-link>
                </li>
              </ul>
              <!-- Collapsed: flyout submenu -->
              <div class="flyout-submenu" v-if="collapsed && !isMobile && hoverSub === child.id">
                <h6>{{ child.name }}</h6>
                <ul>
                  <li v-for="grandchild in child.children.filter(c => c.type !== 'F')" :key="grandchild.id">
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

        <!-- 顶级菜单 (type=C, 直接在根级别): 直接渲染 -->
        <ul v-else-if="menu.type === 'C' && menu.component" class="sidebar-links">
          <li class="sidebar-list">
            <router-link :to="resolvePath('', menu.path)" class="sidebar-link" :class="{ active: activeMenu === resolvePath('', menu.path) }">
              <el-icon class="menu-icon"><component :is="menu.icon || 'Menu'" /></el-icon>
              <span>{{ menu.name }}</span>
            </router-link>
          </li>
        </ul>
      </template>
    </nav>

    <!-- Bottom upgrade card -->
    <div class="sidebar-footer">
      <div class="upgrade-card">
        <img class="upgrade-img" src="/assets/images/sidebar/2.png" alt="" />
        <h5>全能助手</h5>
        <p>告别传统，AI全面管理系统</p>
        <button class="upgrade-btn" @click="goAiChat">前往体验</button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Monitor } from '@element-plus/icons-vue'

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

// 点击推广卡片按钮：跳转到 AI 全能助手
function goAiChat() {
  router.push('/ai/chat')
}

// 过滤掉 F 类型（按钮），只保留 M/C 用于侧边栏渲染
const menuTree = computed(() => {
  return (userStore.menus || []).filter((m: any) => m.type !== 'F')
})

// APEUI 组件库静态菜单（合并为 1 个「UI 组件」分组，内部按二级小标题组织，不走后端）
const apeuiMenuGroups = [
  {
    title: 'UI 组件',
    icon: 'Grid',
    subgroups: [
      {
        title: '仪表盘',
        items: [
          { path: '/dashboard-1', title: '仪表盘样式1' },
          { path: '/dashboard-2', title: '仪表盘样式2' },
        ],
      },
      {
        title: '应用',
        items: [
          { path: '/apeui/app/projects', title: '项目列表' },
          { path: '/apeui/app/project-create', title: '新建项目' },
          { path: '/apeui/app/file-manager', title: '文件管理' },
          { path: '/apeui/app/kanban', title: '看板视图' },
          { path: '/apeui/app/bookmark', title: '书签管理' },
          { path: '/apeui/app/contacts', title: '通讯录' },
          { path: '/apeui/app/tasks', title: '任务列表' },
          { path: '/apeui/app/calendar', title: '日历' },
          { path: '/apeui/app/social', title: '社交应用' },
          { path: '/apeui/app/todo', title: '待办事项' },
          { path: '/apeui/app/search', title: '搜索结果' },
          { path: '/apeui/app/chat', title: '聊天应用' },
          { path: '/apeui/app/chat-video', title: '视频聊天' },
        ],
      },
      {
        title: '电商',
        items: [
          { path: '/apeui/ecommerce/product', title: '商品管理' },
          { path: '/apeui/ecommerce/product-page', title: '商品详情页' },
          { path: '/apeui/ecommerce/add-product', title: '添加商品' },
          { path: '/apeui/ecommerce/product-list', title: '商品列表' },
          { path: '/apeui/ecommerce/payment', title: '支付详情' },
          { path: '/apeui/ecommerce/order-history', title: '订单历史' },
          { path: '/apeui/ecommerce/invoice', title: '发票模板' },
          { path: '/apeui/ecommerce/cart', title: '购物车' },
          { path: '/apeui/ecommerce/wishlist', title: '心愿单' },
          { path: '/apeui/ecommerce/checkout', title: '结算页面' },
          { path: '/apeui/ecommerce/pricing', title: '定价方案' },
        ],
      },
      {
        title: '用户',
        items: [
          { path: '/apeui/users/profile', title: '用户资料' },
          { path: '/apeui/users/edit-profile', title: '编辑资料' },
          { path: '/apeui/users/cards', title: '用户卡片' },
        ],
      },
      {
        title: 'UI 组件',
        items: [
          { path: '/apeui/components/state-color', title: '状态颜色' },
          { path: '/apeui/components/typography', title: '排版样式' },
          { path: '/apeui/components/avatars', title: '头像' },
          { path: '/apeui/components/grid', title: '栅格布局' },
          { path: '/apeui/components/box-shadow', title: '阴影效果' },
          { path: '/apeui/components/buttons', title: '按钮' },
          { path: '/apeui/components/button-group', title: '按钮组' },
          { path: '/apeui/components/tag-pills', title: '标签与胶囊' },
          { path: '/apeui/components/progress-bar', title: '进度条' },
          { path: '/apeui/components/modal', title: '模态框' },
          { path: '/apeui/components/alert', title: '警告提示' },
          { path: '/apeui/components/popover', title: '气泡卡片' },
          { path: '/apeui/components/tooltip', title: '文字提示' },
          { path: '/apeui/components/dropdown', title: '下拉菜单' },
          { path: '/apeui/components/accordion', title: '折叠面板' },
          { path: '/apeui/components/tabs-bootstrap', title: 'Bootstrap 标签页' },
          { path: '/apeui/components/tabs-line', title: '线型标签页' },
          { path: '/apeui/components/list', title: '列表' },
          { path: '/apeui/components/scrollable', title: '滚动区域' },
          { path: '/apeui/components/tree', title: '树形视图' },
          { path: '/apeui/components/rating', title: '评分' },
          { path: '/apeui/components/sweet-alert2', title: '弹窗提示' },
          { path: '/apeui/components/pagination', title: '分页' },
          { path: '/apeui/components/breadcrumb', title: '面包屑' },
          { path: '/apeui/components/range-slider', title: '范围滑块' },
          { path: '/apeui/components/basic-card', title: '基础卡片' },
          { path: '/apeui/components/creative-card', title: '创意卡片' },
          { path: '/apeui/components/tabbed-card', title: '标签页卡片' },
          { path: '/apeui/components/dragable-card', title: '可拖拽卡片' },
          { path: '/apeui/components/timeline-1', title: '时间轴一' },
          { path: '/apeui/components/timeline-2', title: '时间轴二' },
          { path: '/apeui/components/chart-apex', title: 'Apex 图表' },
          { path: '/apeui/components/chart-google', title: 'Google 图表' },
          { path: '/apeui/components/chart-sparkline', title: '迷你走势图' },
          { path: '/apeui/components/chart-flot', title: 'Flot 图表' },
          { path: '/apeui/components/chart-knob', title: '旋钮图表' },
          { path: '/apeui/components/chart-morris', title: 'Morris 图表' },
          { path: '/apeui/components/chartjs', title: 'Chart.js 图表' },
          { path: '/apeui/components/chartist', title: 'Chartist 图表' },
          { path: '/apeui/components/chart-peity', title: 'Peity 图表' },
          { path: '/apeui/components/flag-icon', title: '国旗图标' },
          { path: '/apeui/components/font-awesome', title: 'Font Awesome 图标' },
          { path: '/apeui/components/ico-icon', title: 'Ico 图标' },
          { path: '/apeui/components/themify-icon', title: 'Themify 图标' },
          { path: '/apeui/components/feather-icon', title: 'Feather 图标' },
        ],
      },
    ],
  },
]

function toggleSub(id: string | number) {
  // 折叠状态下不展开 inline 子菜单（宽度不足以展示），由 hover flyout 接管
  if (props.collapsed && !props.isMobile) {
    openedSub.value = null
    return
  }
  openedSub.value = openedSub.value === id ? null : id
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
}
.sidebar-main-title h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.4px;
  color: var(--theme-default, #5A67F5);
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
