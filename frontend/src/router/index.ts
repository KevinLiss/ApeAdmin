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