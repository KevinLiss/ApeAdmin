import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// Static routes (always available)
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      // ===== 系统管理 =====
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' },
      },
      {
        path: 'system/user',
        name: 'SystemUser',
        component: () => import('@/views/system/user/index.vue'),
        meta: { title: '用户管理', icon: 'User', permission: 'system:user:list' },
      },
      {
        path: 'system/role',
        name: 'SystemRole',
        component: () => import('@/views/system/role/index.vue'),
        meta: { title: '角色管理', icon: 'UserFilled', permission: 'system:role:list' },
      },
      {
        path: 'system/menu',
        name: 'SystemMenu',
        component: () => import('@/views/system/menu/index.vue'),
        meta: { title: '菜单管理', icon: 'Menu', permission: 'system:menu:list' },
      },
      {
        path: 'system/dept',
        name: 'SystemDept',
        component: () => import('@/views/system/dept/index.vue'),
        meta: { title: '部门管理', icon: 'OfficeBuilding', permission: 'system:dept:list' },
      },
      // ===== MCP =====
      {
        path: 'mcp/tools',
        name: 'McpTools',
        component: () => import('@/views/mcp/tools.vue'),
        meta: { title: 'MCP 工具', icon: 'Tools' },
      },
      {
        path: 'mcp/resources',
        name: 'McpResources',
        component: () => import('@/views/mcp/resources.vue'),
        meta: { title: 'MCP 资源', icon: 'FolderOpened' },
      },

      // ===== APEUI库 - Dashboards =====
      {
        path: 'apeui/dashboard/default',
        name: 'ApeUIDashboardDefault',
        component: () => import('@/views/apeui/dashboard/Default.vue'),
        meta: { title: 'Default Dashboard' },
      },
      {
        path: 'apeui/dashboard/ecommerce',
        name: 'ApeUIDashboardEcommerce',
        component: () => import('@/views/apeui/dashboard/Ecommerce.vue'),
        meta: { title: 'Ecommerce Dashboard' },
      },

      // ===== APEUI库 - Applications =====
      {
        path: 'apeui/app/projects',
        name: 'ApeUIProjects',
        component: () => import('@/views/apeui/applications/Projects.vue'),
        meta: { title: 'Project List' },
      },
      {
        path: 'apeui/app/project-create',
        name: 'ApeUIProjectCreate',
        component: () => import('@/views/apeui/applications/ProjectCreate.vue'),
        meta: { title: 'Create New Project' },
      },
      {
        path: 'apeui/app/file-manager',
        name: 'ApeUIFileManager',
        component: () => import('@/views/apeui/applications/FileManager.vue'),
        meta: { title: 'File Manager' },
      },
      {
        path: 'apeui/app/kanban',
        name: 'ApeUIKanban',
        component: () => import('@/views/apeui/applications/Kanban.vue'),
        meta: { title: 'Kanban Board' },
      },
      {
        path: 'apeui/app/bookmark',
        name: 'ApeUIBookmark',
        component: () => import('@/views/apeui/applications/Bookmark.vue'),
        meta: { title: 'Bookmarks' },
      },
      {
        path: 'apeui/app/contacts',
        name: 'ApeUIContacts',
        component: () => import('@/views/apeui/applications/Contacts.vue'),
        meta: { title: 'Contacts' },
      },
      {
        path: 'apeui/app/tasks',
        name: 'ApeUITasks',
        component: () => import('@/views/apeui/applications/Tasks.vue'),
        meta: { title: 'Tasks' },
      },
      {
        path: 'apeui/app/calendar',
        name: 'ApeUICalendar',
        component: () => import('@/views/apeui/applications/CalendarBasic.vue'),
        meta: { title: 'Calendar' },
      },
      {
        path: 'apeui/app/social',
        name: 'ApeUISocial',
        component: () => import('@/views/apeui/applications/SocialApp.vue'),
        meta: { title: 'Social App' },
      },
      {
        path: 'apeui/app/todo',
        name: 'ApeUITodo',
        component: () => import('@/views/apeui/applications/Todo.vue'),
        meta: { title: 'To-Do' },
      },
      {
        path: 'apeui/app/search',
        name: 'ApeUISearch',
        component: () => import('@/views/apeui/applications/SearchResult.vue'),
        meta: { title: 'Search Result' },
      },
      {
        path: 'apeui/app/chat',
        name: 'ApeUIChat',
        component: () => import('@/views/apeui/applications/ChatApp.vue'),
        meta: { title: 'Chat App' },
      },
      {
        path: 'apeui/app/chat-video',
        name: 'ApeUIChatVideo',
        component: () => import('@/views/apeui/applications/ChatVideo.vue'),
        meta: { title: 'Video Chat' },
      },

      // ===== APEUI库 - Ecommerce =====
      {
        path: 'apeui/ecommerce/product',
        name: 'ApeUIProduct',
        component: () => import('@/views/apeui/ecommerce/Product.vue'),
        meta: { title: 'Product' },
      },
      {
        path: 'apeui/ecommerce/product-page',
        name: 'ApeUIProductPage',
        component: () => import('@/views/apeui/ecommerce/ProductPage.vue'),
        meta: { title: 'Product Page' },
      },
      {
        path: 'apeui/ecommerce/add-product',
        name: 'ApeUIAddProduct',
        component: () => import('@/views/apeui/ecommerce/AddProduct.vue'),
        meta: { title: 'Add Product' },
      },
      {
        path: 'apeui/ecommerce/product-list',
        name: 'ApeUIProductList',
        component: () => import('@/views/apeui/ecommerce/ProductList.vue'),
        meta: { title: 'Product List' },
      },
      {
        path: 'apeui/ecommerce/payment',
        name: 'ApeUIPayment',
        component: () => import('@/views/apeui/ecommerce/PaymentDetails.vue'),
        meta: { title: 'Payment Details' },
      },
      {
        path: 'apeui/ecommerce/order-history',
        name: 'ApeUIOrderHistory',
        component: () => import('@/views/apeui/ecommerce/OrderHistory.vue'),
        meta: { title: 'Order History' },
      },
      {
        path: 'apeui/ecommerce/invoice',
        name: 'ApeUIInvoice',
        component: () => import('@/views/apeui/ecommerce/InvoiceTemplate.vue'),
        meta: { title: 'Invoice' },
      },
      {
        path: 'apeui/ecommerce/cart',
        name: 'ApeUICart',
        component: () => import('@/views/apeui/ecommerce/Cart.vue'),
        meta: { title: 'Cart' },
      },
      {
        path: 'apeui/ecommerce/wishlist',
        name: 'ApeUIWishlist',
        component: () => import('@/views/apeui/ecommerce/Wishlist.vue'),
        meta: { title: 'Wishlist' },
      },
      {
        path: 'apeui/ecommerce/checkout',
        name: 'ApeUICheckout',
        component: () => import('@/views/apeui/ecommerce/Checkout.vue'),
        meta: { title: 'Checkout' },
      },
      {
        path: 'apeui/ecommerce/pricing',
        name: 'ApeUIPricing',
        component: () => import('@/views/apeui/ecommerce/Pricing.vue'),
        meta: { title: 'Pricing' },
      },

      // ===== APEUI库 - Users =====
      {
        path: 'apeui/users/profile',
        name: 'ApeUIUserProfile',
        component: () => import('@/views/apeui/users/UserProfile.vue'),
        meta: { title: 'Users Profile' },
      },
      {
        path: 'apeui/users/edit-profile',
        name: 'ApeUIEditProfile',
        component: () => import('@/views/apeui/users/EditProfile.vue'),
        meta: { title: 'Users Edit' },
      },
      {
        path: 'apeui/users/cards',
        name: 'ApeUIUserCards',
        component: () => import('@/views/apeui/users/UserCards.vue'),
        meta: { title: 'Users Cards' },
      },

      // ===== APEUI库 - Components =====
      {
        path: 'apeui/components/state-color',
        name: 'ApeUIStateColor',
        component: () => import('@/views/apeui/components/pages/StateColor.vue'),
        meta: { title: 'State Color' },
      },
      {
        path: 'apeui/components/typography',
        name: 'ApeUITypography',
        component: () => import('@/views/apeui/components/pages/Typography.vue'),
        meta: { title: 'Typography' },
      },
      {
        path: 'apeui/components/avatars',
        name: 'ApeUIAvatars',
        component: () => import('@/views/apeui/components/pages/Avatars.vue'),
        meta: { title: 'Avatars' },
      },
      {
        path: 'apeui/components/grid',
        name: 'ApeUIGrid',
        component: () => import('@/views/apeui/components/pages/Grid.vue'),
        meta: { title: 'Grid' },
      },
      {
        path: 'apeui/components/box-shadow',
        name: 'ApeUIBoxShadow',
        component: () => import('@/views/apeui/components/pages/BoxShadow.vue'),
        meta: { title: 'Shadow' },
      },
      {
        path: 'apeui/components/buttons',
        name: 'ApeUIButtons',
        component: () => import('@/views/apeui/components/pages/Buttons.vue'),
        meta: { title: 'Buttons' },
      },
      {
        path: 'apeui/components/button-group',
        name: 'ApeUIButtonGroup',
        component: () => import('@/views/apeui/components/pages/ButtonGroup.vue'),
        meta: { title: 'Button Group' },
      },
      {
        path: 'apeui/components/tag-pills',
        name: 'ApeUITagPills',
        component: () => import('@/views/apeui/components/pages/TagPills.vue'),
        meta: { title: 'Tag & Pills' },
      },
      {
        path: 'apeui/components/progress-bar',
        name: 'ApeUIProgressBar',
        component: () => import('@/views/apeui/components/pages/ProgressBar.vue'),
        meta: { title: 'Progress' },
      },
      {
        path: 'apeui/components/modal',
        name: 'ApeUIModal',
        component: () => import('@/views/apeui/components/pages/Modal.vue'),
        meta: { title: 'Modal' },
      },
      {
        path: 'apeui/components/alert',
        name: 'ApeUIAlert',
        component: () => import('@/views/apeui/components/pages/Alert.vue'),
        meta: { title: 'Alert' },
      },
      {
        path: 'apeui/components/popover',
        name: 'ApeUIPopover',
        component: () => import('@/views/apeui/components/pages/Popover.vue'),
        meta: { title: 'Popover' },
      },
      {
        path: 'apeui/components/tooltip',
        name: 'ApeUITooltip',
        component: () => import('@/views/apeui/components/pages/Tooltip.vue'),
        meta: { title: 'Tooltip' },
      },
      {
        path: 'apeui/components/dropdown',
        name: 'ApeUIDropdown',
        component: () => import('@/views/apeui/components/pages/Dropdown.vue'),
        meta: { title: 'Dropdown' },
      },
      {
        path: 'apeui/components/accordion',
        name: 'ApeUIAccordion',
        component: () => import('@/views/apeui/components/pages/Accordion.vue'),
        meta: { title: 'Accordion' },
      },
      {
        path: 'apeui/components/tabs-bootstrap',
        name: 'ApeUITabsBootstrap',
        component: () => import('@/views/apeui/components/pages/TabsBootstrap.vue'),
        meta: { title: 'Tabs Bootstrap' },
      },
      {
        path: 'apeui/components/tabs-line',
        name: 'ApeUITabsLine',
        component: () => import('@/views/apeui/components/pages/TabsLine.vue'),
        meta: { title: 'Tabs Line' },
      },
      {
        path: 'apeui/components/list',
        name: 'ApeUIList',
        component: () => import('@/views/apeui/components/pages/List.vue'),
        meta: { title: 'Lists' },
      },
      {
        path: 'apeui/components/scrollable',
        name: 'ApeUIScrollable',
        component: () => import('@/views/apeui/components/pages/Scrollable.vue'),
        meta: { title: 'Scrollable' },
      },
      {
        path: 'apeui/components/tree',
        name: 'ApeUITree',
        component: () => import('@/views/apeui/components/pages/Tree.vue'),
        meta: { title: 'Tree View' },
      },
      {
        path: 'apeui/components/rating',
        name: 'ApeUIRating',
        component: () => import('@/views/apeui/components/pages/Rating.vue'),
        meta: { title: 'Rating' },
      },
      {
        path: 'apeui/components/sweet-alert2',
        name: 'ApeUISweetAlert2',
        component: () => import('@/views/apeui/components/pages/SweetAlert2.vue'),
        meta: { title: 'SweetAlert2' },
      },
      {
        path: 'apeui/components/pagination',
        name: 'ApeUIPagination',
        component: () => import('@/views/apeui/components/pages/Pagination.vue'),
        meta: { title: 'Pagination' },
      },
      {
        path: 'apeui/components/breadcrumb',
        name: 'ApeUIBreadcrumb',
        component: () => import('@/views/apeui/components/pages/Breadcrumb.vue'),
        meta: { title: 'Breadcrumb' },
      },
      {
        path: 'apeui/components/range-slider',
        name: 'ApeUIRangeSlider',
        component: () => import('@/views/apeui/components/pages/RangeSlider.vue'),
        meta: { title: 'Range Slider' },
      },
      {
        path: 'apeui/components/basic-card',
        name: 'ApeUIBasicCard',
        component: () => import('@/views/apeui/components/pages/BasicCard.vue'),
        meta: { title: 'Basic Card' },
      },
      {
        path: 'apeui/components/creative-card',
        name: 'ApeUICreativeCard',
        component: () => import('@/views/apeui/components/pages/CreativeCard.vue'),
        meta: { title: 'Creative Card' },
      },
      {
        path: 'apeui/components/tabbed-card',
        name: 'ApeUITabbedCard',
        component: () => import('@/views/apeui/components/pages/TabbedCard.vue'),
        meta: { title: 'Tabbed Card' },
      },
      {
        path: 'apeui/components/dragable-card',
        name: 'ApeUIDragableCard',
        component: () => import('@/views/apeui/components/pages/DragableCard.vue'),
        meta: { title: 'Draggable Card' },
      },
      {
        path: 'apeui/components/timeline-1',
        name: 'ApeUITimeline1',
        component: () => import('@/views/apeui/components/pages/Timeline1.vue'),
        meta: { title: 'Timeline 1' },
      },
      {
        path: 'apeui/components/timeline-2',
        name: 'ApeUITimeline2',
        component: () => import('@/views/apeui/components/pages/Timeline2.vue'),
        meta: { title: 'Timeline 2' },
      },
      {
        path: 'apeui/components/chart-apex',
        name: 'ApeUIChartApex',
        component: () => import('@/views/apeui/components/pages/ChartApex.vue'),
        meta: { title: 'Apex Chart' },
      },
      {
        path: 'apeui/components/chart-google',
        name: 'ApeUIChartGoogle',
        component: () => import('@/views/apeui/components/pages/ChartGoogle.vue'),
        meta: { title: 'Google Chart' },
      },
      {
        path: 'apeui/components/chart-sparkline',
        name: 'ApeUIChartSparkline',
        component: () => import('@/views/apeui/components/pages/ChartSparkline.vue'),
        meta: { title: 'Sparkline' },
      },
      {
        path: 'apeui/components/chart-flot',
        name: 'ApeUIChartFlot',
        component: () => import('@/views/apeui/components/pages/ChartFlot.vue'),
        meta: { title: 'Flot Chart' },
      },
      {
        path: 'apeui/components/chart-knob',
        name: 'ApeUIChartKnob',
        component: () => import('@/views/apeui/components/pages/ChartKnob.vue'),
        meta: { title: 'Knob Chart' },
      },
      {
        path: 'apeui/components/chart-morris',
        name: 'ApeUIChartMorris',
        component: () => import('@/views/apeui/components/pages/ChartMorris.vue'),
        meta: { title: 'Morris Chart' },
      },
      {
        path: 'apeui/components/chartjs',
        name: 'ApeUIChartjs',
        component: () => import('@/views/apeui/components/pages/Chartjs.vue'),
        meta: { title: 'Chartjs' },
      },
      {
        path: 'apeui/components/chartist',
        name: 'ApeUIChartist',
        component: () => import('@/views/apeui/components/pages/Chartist.vue'),
        meta: { title: 'Chartist' },
      },
      {
        path: 'apeui/components/chart-peity',
        name: 'ApeUIChartPeity',
        component: () => import('@/views/apeui/components/pages/ChartPeity.vue'),
        meta: { title: 'Peity Chart' },
      },
      {
        path: 'apeui/components/flag-icon',
        name: 'ApeUIFlagIcon',
        component: () => import('@/views/apeui/components/pages/FlagIcon.vue'),
        meta: { title: 'Flag Icon' },
      },
      {
        path: 'apeui/components/font-awesome',
        name: 'ApeUIFontAwesome',
        component: () => import('@/views/apeui/components/pages/FontAwesome.vue'),
        meta: { title: 'Font Awesome' },
      },
      {
        path: 'apeui/components/ico-icon',
        name: 'ApeUIIcoIcon',
        component: () => import('@/views/apeui/components/pages/IcoIcon.vue'),
        meta: { title: 'Ico Icon' },
      },
      {
        path: 'apeui/components/themify-icon',
        name: 'ApeUIThemifyIcon',
        component: () => import('@/views/apeui/components/pages/ThemifyIcon.vue'),
        meta: { title: 'Themify Icon' },
      },
      {
        path: 'apeui/components/feather-icon',
        name: 'ApeUIFeatherIcon',
        component: () => import('@/views/apeui/components/pages/FeatherIcon.vue'),
        meta: { title: 'Feather Icon' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Global navigation guard: check auth
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('apeadmin_token')
  if (to.path === '/login') {
    if (token) next('/dashboard')
    else next()
  } else {
    if (!token) next('/login')
    else next()
  }
})

export default router
