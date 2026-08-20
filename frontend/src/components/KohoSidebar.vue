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

        <!-- Group: APEUI库 -->
        <li class="sidebar-main-title">
          <div><h4>APEUI库</h4></div>
        </li>

        <!-- Dashboards -->
        <li class="sidebar-list submenu-item" v-for="grp in apeuiMenus" :key="grp.title">
          <a class="sidebar-link sidebar-title" href="javascript:void(0)" @click="toggleSub(grp.title)">
            <el-icon class="menu-icon"><component :is="grp.icon" /></el-icon>
            <span>{{ grp.title }}</span>
            <el-icon class="sub-arrow" :class="{ open: openedSub === grp.title }"><ArrowDown /></el-icon>
          </a>
          <ul class="sidebar-submenu" v-show="openedSub === grp.title">
            <li v-for="item in grp.items" :key="item.path">
              <router-link :to="item.path" :class="{ active: route.path === item.path }">
                {{ item.title }}
              </router-link>
            </li>
          </ul>
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
import { computed, ref } from 'vue'
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
const openedSub = ref<string>('')

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

  // APEUI库 - Koho 五大类页面 (逐页独立路由)
const apeuiMenus = [
  {
    title: 'Dashboards',
    icon: 'Odometer',
    items: [
      { title: 'Default', path: '/apeui/dashboard/default' },
      { title: 'Ecommerce', path: '/apeui/dashboard/ecommerce' },
    ],
  },
  {
    title: 'Applications',
    icon: 'Grid',
    items: [
      { title: 'Project List', path: '/apeui/app/projects' },
      { title: 'Create new', path: '/apeui/app/project-create' },
      { title: 'File Manager', path: '/apeui/app/file-manager' },
      { title: 'Kanban Board', path: '/apeui/app/kanban' },
      { title: 'Bookmarks', path: '/apeui/app/bookmark' },
      { title: 'Contacts', path: '/apeui/app/contacts' },
      { title: 'Tasks', path: '/apeui/app/tasks' },
      { title: 'Calendar', path: '/apeui/app/calendar' },
      { title: 'Social App', path: '/apeui/app/social' },
      { title: 'To-Do', path: '/apeui/app/todo' },
      { title: 'Search Result', path: '/apeui/app/search' },
      { title: 'Chat App', path: '/apeui/app/chat' },
      { title: 'Video Chat', path: '/apeui/app/chat-video' },
    ],
  },
  {
    title: 'Ecommerce',
    icon: 'ShoppingCart',
    items: [
      { title: 'Product', path: '/apeui/ecommerce/product' },
      { title: 'Product Page', path: '/apeui/ecommerce/product-page' },
      { title: 'Add Product', path: '/apeui/ecommerce/add-product' },
      { title: 'Product List', path: '/apeui/ecommerce/product-list' },
      { title: 'Payment Details', path: '/apeui/ecommerce/payment' },
      { title: 'Order History', path: '/apeui/ecommerce/order-history' },
      { title: 'Invoice', path: '/apeui/ecommerce/invoice' },
      { title: 'Cart', path: '/apeui/ecommerce/cart' },
      { title: 'Wishlist', path: '/apeui/ecommerce/wishlist' },
      { title: 'Checkout', path: '/apeui/ecommerce/checkout' },
      { title: 'Pricing', path: '/apeui/ecommerce/pricing' },
    ],
  },
  {
    title: 'Users',
    icon: 'UserFilled',
    items: [
      { title: 'Users Profile', path: '/apeui/users/profile' },
      { title: 'Users Edit', path: '/apeui/users/edit-profile' },
      { title: 'Users Cards', path: '/apeui/users/cards' },
    ],
  },
  {
    title: 'Components',
    icon: 'Box',
    items: [
      { title: 'State Color', path: '/apeui/components/state-color' },
      { title: 'Typography', path: '/apeui/components/typography' },
      { title: 'Avatars', path: '/apeui/components/avatars' },
      { title: 'Grid', path: '/apeui/components/grid' },
      { title: 'Tag & Pills', path: '/apeui/components/tag-pills' },
      { title: 'Progress', path: '/apeui/components/progress-bar' },
      { title: 'Modal', path: '/apeui/components/modal' },
      { title: 'Alert', path: '/apeui/components/alert' },
      { title: 'Popover', path: '/apeui/components/popover' },
      { title: 'Tooltip', path: '/apeui/components/tooltip' },
      { title: 'Dropdown', path: '/apeui/components/dropdown' },
      { title: 'Accordion', path: '/apeui/components/accordion' },
      { title: 'Tabs Bootstrap', path: '/apeui/components/tabs-bootstrap' },
      { title: 'Tabs Line', path: '/apeui/components/tabs-line' },
      { title: 'Shadow', path: '/apeui/components/box-shadow' },
      { title: 'Lists', path: '/apeui/components/list' },
      { title: 'Scrollable', path: '/apeui/components/scrollable' },
      { title: 'Tree View', path: '/apeui/components/tree' },
      { title: 'Rating', path: '/apeui/components/rating' },
      { title: 'SweetAlert2', path: '/apeui/components/sweet-alert2' },
      { title: 'Pagination', path: '/apeui/components/pagination' },
      { title: 'Breadcrumb', path: '/apeui/components/breadcrumb' },
      { title: 'Range Slider', path: '/apeui/components/range-slider' },
      { title: 'Basic Card', path: '/apeui/components/basic-card' },
      { title: 'Creative Card', path: '/apeui/components/creative-card' },
      { title: 'Tabbed Card', path: '/apeui/components/tabbed-card' },
      { title: 'Draggable Card', path: '/apeui/components/dragable-card' },
      { title: 'Timeline 1', path: '/apeui/components/timeline-1' },
      { title: 'Timeline 2', path: '/apeui/components/timeline-2' },
      { title: 'Buttons', path: '/apeui/components/buttons' },
      { title: 'Button Group', path: '/apeui/components/button-group' },
      { title: 'Apex Chart', path: '/apeui/components/chart-apex' },
      { title: 'Google Chart', path: '/apeui/components/chart-google' },
      { title: 'Sparkline', path: '/apeui/components/chart-sparkline' },
      { title: 'Flot Chart', path: '/apeui/components/chart-flot' },
      { title: 'Knob Chart', path: '/apeui/components/chart-knob' },
      { title: 'Morris Chart', path: '/apeui/components/chart-morris' },
      { title: 'Chartjs', path: '/apeui/components/chartjs' },
      { title: 'Chartist', path: '/apeui/components/chartist' },
      { title: 'Peity Chart', path: '/apeui/components/chart-peity' },
      { title: 'Flag Icon', path: '/apeui/components/flag-icon' },
      { title: 'Font Awesome', path: '/apeui/components/font-awesome' },
      { title: 'Ico Icon', path: '/apeui/components/ico-icon' },
      { title: 'Themify Icon', path: '/apeui/components/themify-icon' },
      { title: 'Feather Icon', path: '/apeui/components/feather-icon' },
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
  color: var(--el-color-primary, #534686);
}
.sidebar-submenu li a.active {
  color: var(--el-color-primary, #534686);
  font-weight: 600;
  background: rgba(83, 70, 134, 0.08);
}

/* Collapsed: hide submenus */
.koho-sidebar.close-icon .submenu-item .sidebar-submenu,
.koho-sidebar.close-icon .submenu-item .sub-arrow {
  display: none;
}

.upgrade-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}
</style>