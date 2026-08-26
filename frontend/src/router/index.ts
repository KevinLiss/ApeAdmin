import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

// Vue 的动态组件导入器——使用 Vite 的 import.meta.glob 实现懒加载
// 后端菜单 component 字段如 "system/user/index" → 自动匹配 @/views/system/user/index.vue
const modules = import.meta.glob('@/views/**/*.vue')

/**
 * 根据后端菜单数据动态生成路由
 * @param menus  后端 /auth/userinfo 返回的菜单树
 * @returns RouteRecordRaw[] 动态路由数组
 */
export function generateDynamicRoutes(menus: any[]): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = []

  function buildPath(parentPath: string, childPath: string): string {
    if (childPath.startsWith('/')) return childPath
    return `${parentPath.replace(/\/$/, '')}/${childPath}`
  }

  function traverse(menuList: any[], parentPath: string) {
    for (const menu of menuList) {
      // 只处理 C（菜单）类型，M（目录）和 F（按钮）不生成路由
      if (menu.type === 'C' && menu.component) {
        const fullPath = buildPath(parentPath, menu.path || '')
        // 相对 path（去掉前导 /），因为路由挂在 Layout 的 children 下
        const relativePath = fullPath.replace(/^\//, '')

        // 同时尝试两种路径：${component}.vue 和 ${component}/index.vue
        const componentKey1 = `/src/views/${menu.component}.vue`
        const componentKey2 = `/src/views/${menu.component}/index.vue`
        const component = modules[componentKey1] || modules[componentKey2]

        if (component) {
          routes.push({
            path: relativePath,
            name: menu.name,
            component: component as any,
            meta: {
              title: menu.name,
              icon: menu.icon,
              permission: menu.permission || undefined,
            },
          })
        } else {
          console.warn(`[Router] 未找到组件: ${componentKey1}（或 ${componentKey2}），菜单: ${menu.name}`)
        }
      }

      // 递归处理子菜单
      if (menu.children && menu.children.length > 0) {
        const currentPath = menu.type === 'M' && menu.path
          ? menu.path.replace(/^\//, '')
          : parentPath
        traverse(menu.children, currentPath)
      }
    }
  }

  traverse(menus, '')
  return routes
}

// 静态路由（始终可用，不需要权限）
const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404' },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard-monitor',
    children: [
      // ===== 个人中心 & 系统设置 =====
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/system/profile/index.vue'),
        meta: { title: '个人中心', icon: 'User' },
      },
      {
        path: 'system/settings',
        name: 'SystemSettings',
        component: () => import('@/views/system/settings/index.vue'),
        meta: { title: '系统设置', icon: 'Setting' },
      },

      // ===== 仪表盘 =====
      {
        path: 'dashboard-monitor',
        name: 'DashboardMonitor',
        component: () => import('@/views/apeui/dashboard/Monitor.vue'),
        meta: { title: '系统仪表盘', icon: 'Monitor' },
      },
      {
        path: 'dashboard-1',
        name: 'Dashboard1',
        component: () => import('@/views/apeui/dashboard/Default.vue'),
        meta: { title: '仪表盘样式1', icon: 'Odometer' },
      },
      {
        path: 'dashboard-2',
        name: 'Dashboard2',
        component: () => import('@/views/apeui/dashboard/Ecommerce.vue'),
        meta: { title: '仪表盘样式2', icon: 'DataAnalysis' },
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
        meta: { title: 'ApeAdmin 标签页' },
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
  // Catch-all: 兜底路由，匹配所有未命中的路径
  // 使用 component 而非 redirect，确保 beforeEach 守卫能拦截并重新导航到动态路由
  {
    path: '/:pathMatch(.*)*',
    name: 'CatchAll',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404' },
  },
]

// Legacy component-demo pages are no longer part of the product navigation.
// Keep their files temporarily for reference while preventing direct route registration.
const productRoutes = staticRoutes.map((route) => {
  if (route.name !== 'Layout' || !route.children) return route
  return {
    ...route,
    children: route.children.filter((child) => {
      const path = typeof child.path === 'string' ? child.path : ''
      return !path.startsWith('apeui/components/')
    }),
  }
})

const router = createRouter({
  history: createWebHistory(),
  routes: productRoutes,
})

// 标记是否已加载动态路由（防止重复加载）
let dynamicRoutesLoaded = false

/**
 * 全局路由守卫
 * 1. 无 token → 跳转登录
 * 2. 有 token 但未加载动态路由 → fetchUserInfo + generateDynamicRoutes + addRoute
 * 3. 有 token 且已加载 → 校验 meta.permission
 */
router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('apeadmin_token')

  if (to.path === '/login') {
    if (token) next('/dashboard-monitor')
    else next()
    return
  }

  if (!token) {
    next('/login')
    return
  }

  // 有 token，但动态路由尚未加载
  if (!dynamicRoutesLoaded) {
    const userStore = useUserStore()
    try {
      if (!userStore.menus.length) {
        await userStore.fetchUserInfo()
      }
      const dynamicRoutes = generateDynamicRoutes(userStore.menus)
      for (const route of dynamicRoutes) {
        router.addRoute('Layout', route)  // 挂在 Layout 的 children 下
      }

      dynamicRoutesLoaded = true

      // 重新导航到目标路由（addRoute 后需重新解析路径以匹配动态路由）
      // 使用 fullPath 而非展开 to 对象，避免携带已匹配的 name/matched 等属性
      next({ path: to.fullPath, replace: true })
      return
    } catch (e) {
      console.error('[Router] 动态路由加载失败:', e)
      userStore.reset()
      next('/login')
      return
    }
  }

  // 动态路由已加载——校验权限
  const userStore = useUserStore()
  const requiredPerm = to.meta?.permission as string | undefined
  if (requiredPerm && !userStore.hasPermission(requiredPerm)) {
    next('/404')
    return
  }

  next()
})

// 提供手动重置动态路由的方法（登出时调用）
export function resetRouter() {
  dynamicRoutesLoaded = false
  // 移除所有动态路由（保留静态路由）
  const staticNames = ['Login', 'NotFound', 'CatchAll', 'Layout', 'Profile', 'SystemSettings', 'DashboardMonitor', 'Dashboard1', 'Dashboard2',
    'ApeUIProjects', 'ApeUIProjectCreate', 'ApeUIFileManager', 'ApeUIKanban',
    'ApeUIBookmark', 'ApeUIContacts', 'ApeUITasks', 'ApeUICalendar',
    'ApeUISocial', 'ApeUITodo', 'ApeUISearch', 'ApeUIChat', 'ApeUIChatVideo',
    'ApeUIProduct', 'ApeUIProductPage', 'ApeUIAddProduct', 'ApeUIProductList',
    'ApeUIPayment', 'ApeUIOrderHistory', 'ApeUIInvoice', 'ApeUICart',
    'ApeUIWishlist', 'ApeUICheckout', 'ApeUIPricing',
    'ApeUIUserProfile', 'ApeUIEditProfile', 'ApeUIUserCards',
    'ApeUIStateColor', 'ApeUITypography', 'ApeUIAvatars', 'ApeUIGrid',
    'ApeUIBoxShadow', 'ApeUIButtons', 'ApeUIButtonGroup', 'ApeUITagPills',
    'ApeUIProgressBar', 'ApeUIModal', 'ApeUIAlert', 'ApeUIPopover',
    'ApeUITooltip', 'ApeUIDropdown', 'ApeUIAccordion', 'ApeUITabsBootstrap',
    'ApeUITabsLine', 'ApeUIList', 'ApeUIScrollable', 'ApeUITree',
    'ApeUIRating', 'ApeUISweetAlert2', 'ApeUIPagination', 'ApeUIBreadcrumb',
    'ApeUIRangeSlider', 'ApeUIBasicCard', 'ApeUICreativeCard', 'ApeUITabbedCard',
    'ApeUIDragableCard', 'ApeUITimeline1', 'ApeUITimeline2',
    'ApeUIChartApex', 'ApeUIChartGoogle', 'ApeUIChartSparkline', 'ApeUIChartFlot',
    'ApeUIChartKnob', 'ApeUIChartMorris', 'ApeUIChartjs', 'ApeUIChartist',
    'ApeUIChartPeity', 'ApeUIFlagIcon', 'ApeUIFontAwesome', 'ApeUIIcoIcon',
    'ApeUIThemifyIcon', 'ApeUIFeatherIcon',
  ]
  router.getRoutes().forEach((route) => {
    if (route.name && !staticNames.includes(route.name as string)) {
      router.removeRoute(route.name)
    }
  })
}

export default router
