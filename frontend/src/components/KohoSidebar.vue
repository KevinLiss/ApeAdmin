<template>
  <aside
    class="koho-sidebar"
    :class="{
      'close-icon': collapsed && !isMobile,
      'mobile-open': isMobile && mobileOpen,
      'mobile-hidden': isMobile && !mobileOpen
    }"
  >
    <!-- Logo + toggle -->
    <div class="logo-wrapper" :class="{ 'logo-collapsed': collapsed && !isMobile }" @click="(collapsed && !isMobile) && $emit('toggle')">
      <div class="logo-inner">
        <el-icon :size="28" color="#5A67F5"><Platform /></el-icon>
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
      <ul class="sidebar-links">
        <!-- 仪表盘 -->
        <li class="sidebar-list">
          <router-link to="/dashboard-1" class="sidebar-link" :class="{ active: activeMenu === '/dashboard-1' }">
            <el-icon class="menu-icon"><Odometer /></el-icon>
            <span>仪表盘1</span>
          </router-link>
        </li>
        <li class="sidebar-list">
          <router-link to="/dashboard-2" class="sidebar-link" :class="{ active: activeMenu === '/dashboard-2' }">
            <el-icon class="menu-icon"><DataAnalysis /></el-icon>
            <span>仪表盘2</span>
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

        <!-- Group: APEUI库 -->
        <li class="sidebar-main-title">
          <div><h4>APEUI库</h4></div>
        </li>

        <!-- Dashboards -->
        <li
          class="sidebar-list submenu-item"
          v-for="grp in apeuiMenus"
          :key="grp.title"
          @mouseenter="collapsed && !isMobile && (hoverSub = grp.title)"
          @mouseleave="collapsed && !isMobile && (hoverSub = '')"
        >
          <a class="sidebar-link sidebar-title" href="javascript:void(0)" @click="toggleSub(grp.title)">
            <el-icon class="menu-icon"><component :is="grp.icon" /></el-icon>
            <span>{{ grp.title }}</span>
            <el-icon class="sub-arrow" :class="{ open: openedSub === grp.title }"><ArrowDown /></el-icon>
          </a>
          <!-- Expanded mode: inline submenu -->
          <ul class="sidebar-submenu" v-show="openedSub === grp.title">
            <li v-for="item in grp.items" :key="item.path">
              <router-link :to="item.path" :class="{ active: route.path === item.path }">
                {{ item.title }}
              </router-link>
            </li>
          </ul>
          <!-- Collapsed mode: flyout submenu -->
          <div
            class="flyout-submenu"
            v-if="collapsed && !isMobile && hoverSub === grp.title"
          >
            <h6>{{ grp.title }}</h6>
            <ul>
              <li v-for="item in grp.items" :key="item.path">
                <router-link :to="item.path" :class="{ active: route.path === item.path }">
                  {{ item.title }}
                </router-link>
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </nav>

    <!-- Bottom upgrade card (Koho sidebar-img-content) -->
    <div class="sidebar-footer">
      <div class="upgrade-card">
        <img class="upgrade-img" src="/assets/images/sidebar/2.png" alt="" />
        <h5>体验更多功能</h5>
        <p>升级插件体系，解锁 AI 能力</p>
        <button class="upgrade-btn" @click="$emit('upgrade')">现在查看</button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

defineProps<{
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
const activeMenu = computed(() => route.path)
const openedSub = ref<string>('')
const hoverSub = ref<string>('')

function toggleSub(title: string) {
  openedSub.value = openedSub.value === title ? '' : title
}

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

  // APEUI库 - 四大模块 (数据看板已提升为顶级仪表盘1/2)
const apeuiMenus = [
  {
    title: '应用中心',
    icon: 'Grid',
    items: [
      { title: '项目列表', path: '/apeui/app/projects' },
      { title: '新建项目', path: '/apeui/app/project-create' },
      { title: '文件管理', path: '/apeui/app/file-manager' },
      { title: '看板视图', path: '/apeui/app/kanban' },
      { title: '书签管理', path: '/apeui/app/bookmark' },
      { title: '通讯录', path: '/apeui/app/contacts' },
      { title: '任务列表', path: '/apeui/app/tasks' },
      { title: '日历', path: '/apeui/app/calendar' },
      { title: '社交应用', path: '/apeui/app/social' },
      { title: '待办事项', path: '/apeui/app/todo' },
      { title: '搜索结果', path: '/apeui/app/search' },
      { title: '聊天应用', path: '/apeui/app/chat' },
      { title: '视频聊天', path: '/apeui/app/chat-video' },
    ],
  },
  {
    title: '电商模块',
    icon: 'ShoppingCart',
    items: [
      { title: '商品管理', path: '/apeui/ecommerce/product' },
      { title: '商品详情页', path: '/apeui/ecommerce/product-page' },
      { title: '添加商品', path: '/apeui/ecommerce/add-product' },
      { title: '商品列表', path: '/apeui/ecommerce/product-list' },
      { title: '支付详情', path: '/apeui/ecommerce/payment' },
      { title: '订单历史', path: '/apeui/ecommerce/order-history' },
      { title: '发票模板', path: '/apeui/ecommerce/invoice' },
      { title: '购物车', path: '/apeui/ecommerce/cart' },
      { title: '心愿单', path: '/apeui/ecommerce/wishlist' },
      { title: '结算页面', path: '/apeui/ecommerce/checkout' },
      { title: '定价方案', path: '/apeui/ecommerce/pricing' },
    ],
  },
  {
    title: '用户中心',
    icon: 'UserFilled',
    items: [
      { title: '用户资料', path: '/apeui/users/profile' },
      { title: '编辑资料', path: '/apeui/users/edit-profile' },
      { title: '用户卡片', path: '/apeui/users/cards' },
    ],
  },
  {
    title: '组件示例',
    icon: 'Box',
    items: [
      { title: '状态颜色', path: '/apeui/components/state-color' },
      { title: '排版样式', path: '/apeui/components/typography' },
      { title: '头像', path: '/apeui/components/avatars' },
      { title: '栅格布局', path: '/apeui/components/grid' },
      { title: '标签与胶囊', path: '/apeui/components/tag-pills' },
      { title: '进度条', path: '/apeui/components/progress-bar' },
      { title: '模态框', path: '/apeui/components/modal' },
      { title: '警告提示', path: '/apeui/components/alert' },
      { title: '气泡卡片', path: '/apeui/components/popover' },
      { title: '文字提示', path: '/apeui/components/tooltip' },
      { title: '下拉菜单', path: '/apeui/components/dropdown' },
      { title: '折叠面板', path: '/apeui/components/accordion' },
      { title: 'Bootstrap 标签页', path: '/apeui/components/tabs-bootstrap' },
      { title: '线型标签页', path: '/apeui/components/tabs-line' },
      { title: '阴影效果', path: '/apeui/components/box-shadow' },
      { title: '列表', path: '/apeui/components/list' },
      { title: '滚动区域', path: '/apeui/components/scrollable' },
      { title: '树形视图', path: '/apeui/components/tree' },
      { title: '评分', path: '/apeui/components/rating' },
      { title: '弹窗提示', path: '/apeui/components/sweet-alert2' },
      { title: '分页', path: '/apeui/components/pagination' },
      { title: '面包屑', path: '/apeui/components/breadcrumb' },
      { title: '范围滑块', path: '/apeui/components/range-slider' },
      { title: '基础卡片', path: '/apeui/components/basic-card' },
      { title: '创意卡片', path: '/apeui/components/creative-card' },
      { title: '标签页卡片', path: '/apeui/components/tabbed-card' },
      { title: '可拖拽卡片', path: '/apeui/components/dragable-card' },
      { title: '时间轴一', path: '/apeui/components/timeline-1' },
      { title: '时间轴二', path: '/apeui/components/timeline-2' },
      { title: '按钮', path: '/apeui/components/buttons' },
      { title: '按钮组', path: '/apeui/components/button-group' },
      { title: 'Apex 图表', path: '/apeui/components/chart-apex' },
      { title: 'Google 图表', path: '/apeui/components/chart-google' },
      { title: '迷你走势图', path: '/apeui/components/chart-sparkline' },
      { title: 'Flot 图表', path: '/apeui/components/chart-flot' },
      { title: '旋钮图表', path: '/apeui/components/chart-knob' },
      { title: 'Morris 图表', path: '/apeui/components/chart-morris' },
      { title: 'Chart.js 图表', path: '/apeui/components/chartjs' },
      { title: 'Chartist 图表', path: '/apeui/components/chartist' },
      { title: 'Peity 图表', path: '/apeui/components/chart-peity' },
      { title: '国旗图标', path: '/apeui/components/flag-icon' },
      { title: 'Font Awesome 图标', path: '/apeui/components/font-awesome' },
      { title: 'Ico 图标', path: '/apeui/components/ico-icon' },
      { title: 'Themify 图标', path: '/apeui/components/themify-icon' },
      { title: 'Feather 图标', path: '/apeui/components/feather-icon' },
    ],
  },
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
/* Collapsed mode: allow flyout to overflow */
.koho-sidebar.close-icon {
  overflow: visible;
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
/* Collapsed mode: allow flyout to overflow */
.koho-sidebar.close-icon .sidebar-main {
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

/* Footer upgrade card (Koho sidebar-img-content 1:1) */
.sidebar-footer {
  padding: 0 22px;
  margin-bottom: 24px;
}
.upgrade-card {
  background-color: #eff3f9;
  border-radius: 20px;
  text-align: center;
  padding-top: 20px;
  padding-bottom: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.upgrade-img {
  height: 80px;
  display: block;
  margin: 0 auto 4px;
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
  background: var(--theme-default, #5A67F5);
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
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
.koho-sidebar.close-icon .submenu-item .sidebar-submenu,
.koho-sidebar.close-icon .submenu-item .sub-arrow {
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

/* Mobile: drawer mode (≤1199px) */
.koho-sidebar.mobile-hidden {
  transform: translateX(-285px);
}
.koho-sidebar.mobile-open {
  transform: translateX(0);
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.15);
}
/* Mobile close button styling */
.mobile-close-btn {
  background: rgba(90, 103, 245, 0.1);
  color: var(--theme-default, #5A67F5);
}
.mobile-close-btn:hover {
  background: rgba(90, 103, 245, 0.2);
}

.upgrade-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(90, 103, 245, 0.3);
}
</style>