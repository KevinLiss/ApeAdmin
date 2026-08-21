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
    redirect: '/dashboard-1',
    children: [
      // ===== 仪表盘 =====
      {
        path: 'dashboard-1',
        name: 'Dashboard1',
        component: () => import('@/views/apeui/dashboard/Default.vue'),
        meta: { title: '仪表盘1', icon: 'Odometer' },
      },
      {
        path: 'dashboard-2',
        name: 'Dashboard2',
        component: () => import('@/views/apeui/dashboard/Ecommerce.vue'),
        meta: { title: '仪表盘2', icon: 'DataAnalysis' },
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

      // ===== APEUI库 - Applications =====
      {
        path: 'apeui/app/projects',
        name: 'ApeUIProjects',
        component: () => import('@/views/apeui/applications/Projects.vue'),
        meta: { title: '项目列表' },
      },
      {
        path: 'apeui/app/project-create',
        name: 'ApeUIProjectCreate',
        component: () => import('@/views/apeui/applications/ProjectCreate.vue'),
        meta: { title: '新建项目' },
      },
      {
        path: 'apeui/app/file-manager',
        name: 'ApeUIFileManager',
        component: () => import('@/views/apeui/applications/FileManager.vue'),
        meta: { title: '文件管理' },
      },
      {
        path: 'apeui/app/kanban',
        name: 'ApeUIKanban',
        component: () => import('@/views/apeui/applications/Kanban.vue'),
        meta: { title: '看板视图' },
      },
      {
        path: 'apeui/app/bookmark',
        name: 'ApeUIBookmark',
        component: () => import('@/views/apeui/applications/Bookmark.vue'),
        meta: { title: '书签管理' },
      },
      {
        path: 'apeui/app/contacts',
        name: 'ApeUIContacts',
        component: () => import('@/views/apeui/applications/Contacts.vue'),
        meta: { title: '通讯录' },
      },
      {
        path: 'apeui/app/tasks',
        name: 'ApeUITasks',
        component: () => import('@/views/apeui/applications/Tasks.vue'),
        meta: { title: '任务列表' },
      },
      {
        path: 'apeui/app/calendar',
        name: 'ApeUICalendar',
        component: () => import('@/views/apeui/applications/CalendarBasic.vue'),
        meta: { title: '日历' },
      },
      {
        path: 'apeui/app/social',
        name: 'ApeUISocial',
        component: () => import('@/views/apeui/applications/SocialApp.vue'),
        meta: { title: '社交应用' },
      },
      {
        path: 'apeui/app/todo',
        name: 'ApeUITodo',
        component: () => import('@/views/apeui/applications/Todo.vue'),
        meta: { title: '待办事项' },
      },
      {
        path: 'apeui/app/search',
        name: 'ApeUISearch',
        component: () => import('@/views/apeui/applications/SearchResult.vue'),
        meta: { title: '搜索结果' },
      },
      {
        path: 'apeui/app/chat',
        name: 'ApeUIChat',
        component: () => import('@/views/apeui/applications/ChatApp.vue'),
        meta: { title: '聊天应用' },
      },
      {
        path: 'apeui/app/chat-video',
        name: 'ApeUIChatVideo',
        component: () => import('@/views/apeui/applications/ChatVideo.vue'),
        meta: { title: '视频聊天' },
      },

      // ===== APEUI库 - Ecommerce =====
      {
        path: 'apeui/ecommerce/product',
        name: 'ApeUIProduct',
        component: () => import('@/views/apeui/ecommerce/Product.vue'),
        meta: { title: '商品管理' },
      },
      {
        path: 'apeui/ecommerce/product-page',
        name: 'ApeUIProductPage',
        component: () => import('@/views/apeui/ecommerce/ProductPage.vue'),
        meta: { title: '商品详情页' },
      },
      {
        path: 'apeui/ecommerce/add-product',
        name: 'ApeUIAddProduct',
        component: () => import('@/views/apeui/ecommerce/AddProduct.vue'),
        meta: { title: '添加商品' },
      },
      {
        path: 'apeui/ecommerce/product-list',
        name: 'ApeUIProductList',
        component: () => import('@/views/apeui/ecommerce/ProductList.vue'),
        meta: { title: '商品列表' },
      },
      {
        path: 'apeui/ecommerce/payment',
        name: 'ApeUIPayment',
        component: () => import('@/views/apeui/ecommerce/PaymentDetails.vue'),
        meta: { title: '支付详情' },
      },
      {
        path: 'apeui/ecommerce/order-history',
        name: 'ApeUIOrderHistory',
        component: () => import('@/views/apeui/ecommerce/OrderHistory.vue'),
        meta: { title: '订单历史' },
      },
      {
        path: 'apeui/ecommerce/invoice',
        name: 'ApeUIInvoice',
        component: () => import('@/views/apeui/ecommerce/InvoiceTemplate.vue'),
        meta: { title: '发票模板' },
      },
      {
        path: 'apeui/ecommerce/cart',
        name: 'ApeUICart',
        component: () => import('@/views/apeui/ecommerce/Cart.vue'),
        meta: { title: '购物车' },
      },
      {
        path: 'apeui/ecommerce/wishlist',
        name: 'ApeUIWishlist',
        component: () => import('@/views/apeui/ecommerce/Wishlist.vue'),
        meta: { title: '心愿单' },
      },
      {
        path: 'apeui/ecommerce/checkout',
        name: 'ApeUICheckout',
        component: () => import('@/views/apeui/ecommerce/Checkout.vue'),
        meta: { title: '结算页面' },
      },
      {
        path: 'apeui/ecommerce/pricing',
        name: 'ApeUIPricing',
        component: () => import('@/views/apeui/ecommerce/Pricing.vue'),
        meta: { title: '定价方案' },
      },

      // ===== APEUI库 - Users =====
      {
        path: 'apeui/users/profile',
        name: 'ApeUIUserProfile',
        component: () => import('@/views/apeui/users/UserProfile.vue'),
        meta: { title: '用户资料' },
      },
      {
        path: 'apeui/users/edit-profile',
        name: 'ApeUIEditProfile',
        component: () => import('@/views/apeui/users/EditProfile.vue'),
        meta: { title: '编辑资料' },
      },
      {
        path: 'apeui/users/cards',
        name: 'ApeUIUserCards',
        component: () => import('@/views/apeui/users/UserCards.vue'),
        meta: { title: '用户卡片' },
      },

      // ===== APEUI库 - Components =====
      {
        path: 'apeui/components/state-color',
        name: 'ApeUIStateColor',
        component: () => import('@/views/apeui/components/pages/StateColor.vue'),
        meta: { title: '状态颜色' },
      },
      {
        path: 'apeui/components/typography',
        name: 'ApeUITypography',
        component: () => import('@/views/apeui/components/pages/Typography.vue'),
        meta: { title: '排版样式' },
      },
      {
        path: 'apeui/components/avatars',
        name: 'ApeUIAvatars',
        component: () => import('@/views/apeui/components/pages/Avatars.vue'),
        meta: { title: '头像' },
      },
      {
        path: 'apeui/components/grid',
        name: 'ApeUIGrid',
        component: () => import('@/views/apeui/components/pages/Grid.vue'),
        meta: { title: '栅格布局' },
      },
      {
        path: 'apeui/components/box-shadow',
        name: 'ApeUIBoxShadow',
        component: () => import('@/views/apeui/components/pages/BoxShadow.vue'),
        meta: { title: '阴影效果' },
      },
      {
        path: 'apeui/components/buttons',
        name: 'ApeUIButtons',
        component: () => import('@/views/apeui/components/pages/Buttons.vue'),
        meta: { title: '按钮' },
      },
      {
        path: 'apeui/components/button-group',
        name: 'ApeUIButtonGroup',
        component: () => import('@/views/apeui/components/pages/ButtonGroup.vue'),
        meta: { title: '按钮组' },
      },
      {
        path: 'apeui/components/tag-pills',
        name: 'ApeUITagPills',
        component: () => import('@/views/apeui/components/pages/TagPills.vue'),
        meta: { title: '标签与胶囊' },
      },
      {
        path: 'apeui/components/progress-bar',
        name: 'ApeUIProgressBar',
        component: () => import('@/views/apeui/components/pages/ProgressBar.vue'),
        meta: { title: '进度条' },
      },
      {
        path: 'apeui/components/modal',
        name: 'ApeUIModal',
        component: () => import('@/views/apeui/components/pages/Modal.vue'),
        meta: { title: '模态框' },
      },
      {
        path: 'apeui/components/alert',
        name: 'ApeUIAlert',
        component: () => import('@/views/apeui/components/pages/Alert.vue'),
        meta: { title: '警告提示' },
      },
      {
        path: 'apeui/components/popover',
        name: 'ApeUIPopover',
        component: () => import('@/views/apeui/components/pages/Popover.vue'),
        meta: { title: '气泡卡片' },
      },
      {
        path: 'apeui/components/tooltip',
        name: 'ApeUITooltip',
        component: () => import('@/views/apeui/components/pages/Tooltip.vue'),
        meta: { title: '文字提示' },
      },
      {
        path: 'apeui/components/dropdown',
        name: 'ApeUIDropdown',
        component: () => import('@/views/apeui/components/pages/Dropdown.vue'),
        meta: { title: '下拉菜单' },
      },
      {
        path: 'apeui/components/accordion',
        name: 'ApeUIAccordion',
        component: () => import('@/views/apeui/components/pages/Accordion.vue'),
        meta: { title: '折叠面板' },
      },
      {
        path: 'apeui/components/tabs-bootstrap',
        name: 'ApeUITabsBootstrap',
        component: () => import('@/views/apeui/components/pages/TabsBootstrap.vue'),
        meta: { title: 'Bootstrap 标签页' },
      },
      {
        path: 'apeui/components/tabs-line',
        name: 'ApeUITabsLine',
        component: () => import('@/views/apeui/components/pages/TabsLine.vue'),
        meta: { title: '线型标签页' },
      },
      {
        path: 'apeui/components/list',
        name: 'ApeUIList',
        component: () => import('@/views/apeui/components/pages/List.vue'),
        meta: { title: '列表' },
      },
      {
        path: 'apeui/components/scrollable',
        name: 'ApeUIScrollable',
        component: () => import('@/views/apeui/components/pages/Scrollable.vue'),
        meta: { title: '滚动区域' },
      },
      {
        path: 'apeui/components/tree',
        name: 'ApeUITree',
        component: () => import('@/views/apeui/components/pages/Tree.vue'),
        meta: { title: '树形视图' },
      },
      {
        path: 'apeui/components/rating',
        name: 'ApeUIRating',
        component: () => import('@/views/apeui/components/pages/Rating.vue'),
        meta: { title: '评分' },
      },
      {
        path: 'apeui/components/sweet-alert2',
        name: 'ApeUISweetAlert2',
        component: () => import('@/views/apeui/components/pages/SweetAlert2.vue'),
        meta: { title: '弹窗提示' },
      },
      {
        path: 'apeui/components/pagination',
        name: 'ApeUIPagination',
        component: () => import('@/views/apeui/components/pages/Pagination.vue'),
        meta: { title: '分页' },
      },
      {
        path: 'apeui/components/breadcrumb',
        name: 'ApeUIBreadcrumb',
        component: () => import('@/views/apeui/components/pages/Breadcrumb.vue'),
        meta: { title: '面包屑' },
      },
      {
        path: 'apeui/components/range-slider',
        name: 'ApeUIRangeSlider',
        component: () => import('@/views/apeui/components/pages/RangeSlider.vue'),
        meta: { title: '范围滑块' },
      },
      {
        path: 'apeui/components/basic-card',
        name: 'ApeUIBasicCard',
        component: () => import('@/views/apeui/components/pages/BasicCard.vue'),
        meta: { title: '基础卡片' },
      },
      {
        path: 'apeui/components/creative-card',
        name: 'ApeUICreativeCard',
        component: () => import('@/views/apeui/components/pages/CreativeCard.vue'),
        meta: { title: '创意卡片' },
      },
      {
        path: 'apeui/components/tabbed-card',
        name: 'ApeUITabbedCard',
        component: () => import('@/views/apeui/components/pages/TabbedCard.vue'),
        meta: { title: '标签页卡片' },
      },
      {
        path: 'apeui/components/dragable-card',
        name: 'ApeUIDragableCard',
        component: () => import('@/views/apeui/components/pages/DragableCard.vue'),
        meta: { title: '可拖拽卡片' },
      },
      {
        path: 'apeui/components/timeline-1',
        name: 'ApeUITimeline1',
        component: () => import('@/views/apeui/components/pages/Timeline1.vue'),
        meta: { title: '时间轴一' },
      },
      {
        path: 'apeui/components/timeline-2',
        name: 'ApeUITimeline2',
        component: () => import('@/views/apeui/components/pages/Timeline2.vue'),
        meta: { title: '时间轴二' },
      },
      {
        path: 'apeui/components/chart-apex',
        name: 'ApeUIChartApex',
        component: () => import('@/views/apeui/components/pages/ChartApex.vue'),
        meta: { title: 'Apex 图表' },
      },
      {
        path: 'apeui/components/chart-google',
        name: 'ApeUIChartGoogle',
        component: () => import('@/views/apeui/components/pages/ChartGoogle.vue'),
        meta: { title: 'Google 图表' },
      },
      {
        path: 'apeui/components/chart-sparkline',
        name: 'ApeUIChartSparkline',
        component: () => import('@/views/apeui/components/pages/ChartSparkline.vue'),
        meta: { title: '迷你走势图' },
      },
      {
        path: 'apeui/components/chart-flot',
        name: 'ApeUIChartFlot',
        component: () => import('@/views/apeui/components/pages/ChartFlot.vue'),
        meta: { title: 'Flot 图表' },
      },
      {
        path: 'apeui/components/chart-knob',
        name: 'ApeUIChartKnob',
        component: () => import('@/views/apeui/components/pages/ChartKnob.vue'),
        meta: { title: '旋钮图表' },
      },
      {
        path: 'apeui/components/chart-morris',
        name: 'ApeUIChartMorris',
        component: () => import('@/views/apeui/components/pages/ChartMorris.vue'),
        meta: { title: 'Morris 图表' },
      },
      {
        path: 'apeui/components/chartjs',
        name: 'ApeUIChartjs',
        component: () => import('@/views/apeui/components/pages/Chartjs.vue'),
        meta: { title: 'Chart.js 图表' },
      },
      {
        path: 'apeui/components/chartist',
        name: 'ApeUIChartist',
        component: () => import('@/views/apeui/components/pages/Chartist.vue'),
        meta: { title: 'Chartist 图表' },
      },
      {
        path: 'apeui/components/chart-peity',
        name: 'ApeUIChartPeity',
        component: () => import('@/views/apeui/components/pages/ChartPeity.vue'),
        meta: { title: 'Peity 图表' },
      },
      {
        path: 'apeui/components/flag-icon',
        name: 'ApeUIFlagIcon',
        component: () => import('@/views/apeui/components/pages/FlagIcon.vue'),
        meta: { title: '国旗图标' },
      },
      {
        path: 'apeui/components/font-awesome',
        name: 'ApeUIFontAwesome',
        component: () => import('@/views/apeui/components/pages/FontAwesome.vue'),
        meta: { title: 'Font Awesome 图标' },
      },
      {
        path: 'apeui/components/ico-icon',
        name: 'ApeUIIcoIcon',
        component: () => import('@/views/apeui/components/pages/IcoIcon.vue'),
        meta: { title: 'Ico 图标' },
      },
      {
        path: 'apeui/components/themify-icon',
        name: 'ApeUIThemifyIcon',
        component: () => import('@/views/apeui/components/pages/ThemifyIcon.vue'),
        meta: { title: 'Themify 图标' },
      },
      {
        path: 'apeui/components/feather-icon',
        name: 'ApeUIFeatherIcon',
        component: () => import('@/views/apeui/components/pages/FeatherIcon.vue'),
        meta: { title: 'Feather 图标' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard-1',
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
    if (token) next('/dashboard-1')
    else next()
  } else {
    if (!token) next('/login')
    else next()
  }
})

export default router
