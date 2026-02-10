import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { ElMessage } from 'element-plus'

// 基础路由（不需要权限）
const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录',
      requiresAuth: false,
    },
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在',
      requiresAuth: false,
    },
  },
]

// 主要路由（需要权限）
const asyncRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true,
    },
    children: [
      // 首页
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '首页',
          icon: 'HomeFilled',
          requiresAuth: true,
        },
      },
      // 资产管理
      {
        path: '/assets',
        name: 'Assets',
        redirect: '/assets/list',
        meta: {
          title: '资产管理',
          icon: 'Box',
          requiresAuth: true,
          roles: ['admin', 'center_auditor', 'data_holder'],
        },
        children: [
          {
            path: 'list',
            name: 'AssetList',
            component: () => import('@/views/assets/index.vue'),
            meta: {
              title: '资产列表',
              requiresAuth: true,
            },
          },
          {
            path: 'detail/:id',
            name: 'AssetDetail',
            component: () => import('@/views/assets/detail.vue'),
            meta: {
              title: '资产详情',
              requiresAuth: true,
              hideInMenu: true,
            },
          },
          {
            path: 'form',
            name: 'AssetForm',
            component: () => import('@/views/assets/form.vue'),
            meta: {
              title: '资产登记',
              requiresAuth: true,
              roles: ['admin', 'data_holder'],
            },
          },
        ],
      },
      // 工作流管理
      {
        path: '/workflow',
        name: 'Workflow',
        redirect: '/workflow/pending',
        meta: {
          title: '工作流',
          icon: 'CircleCheck',
          requiresAuth: true,
          roles: ['admin', 'center_auditor', 'evaluator'],
        },
        children: [
          {
            path: 'pending',
            name: 'WorkflowPending',
            component: () => import('@/views/workflow/pending.vue'),
            meta: {
              title: '待办任务',
              requiresAuth: true,
            },
          },
          {
            path: 'detail/:id',
            name: 'WorkflowDetail',
            component: () => import('@/views/workflow/detail.vue'),
            meta: {
              title: '流程详情',
              requiresAuth: true,
              hideInMenu: true,
            },
          },
        ],
      },
      // 评估管理
      {
        path: '/assessment',
        name: 'Assessment',
        component: () => import('@/views/assessment/index.vue'),
        meta: {
          title: '评估管理',
          icon: 'DataAnalysis',
          requiresAuth: true,
          roles: ['admin', 'evaluator'],
        },
      },
      // 统计分析
      {
        path: '/statistics',
        name: 'Statistics',
        component: () => import('@/views/statistics/index.vue'),
        meta: {
          title: '统计分析',
          icon: 'TrendCharts',
          requiresAuth: true,
          roles: ['admin', 'center_auditor', 'regulator'],
        },
      },
      // 审计日志
      {
        path: '/audit',
        name: 'Audit',
        component: () => import('@/views/audit/index.vue'),
        meta: {
          title: '审计日志',
          icon: 'List',
          requiresAuth: true,
          roles: ['admin', 'auditor', 'regulator'],
        },
      },
      // 通知中心
      {
        path: '/notifications',
        name: 'Notifications',
        component: () => import('@/views/notifications/index.vue'),
        meta: {
          title: '通知中心',
          icon: 'Bell',
          requiresAuth: true,
        },
      },
      // 系统管理
      {
        path: '/system',
        name: 'System',
        redirect: '/system/users',
        meta: {
          title: '系统管理',
          icon: 'Setting',
          requiresAuth: true,
          roles: ['admin', 'system'],
        },
        children: [
          {
            path: 'users',
            name: 'SystemUsers',
            component: () => import('@/views/system/users.vue'),
            meta: {
              title: '用户管理',
              icon: 'User',
              requiresAuth: true,
            },
          },
        ],
      },
      // 个人中心
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/placeholder.vue'),
        meta: {
          title: '个人中心',
          requiresAuth: true,
          hideInMenu: true,
        },
      },
    ],
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [...constantRoutes, ...asyncRoutes],
  scrollBehavior: () => ({ top: 0 }),
})

// 路由守卫
let hasInitialized = false

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 数据资产管理平台`
  } else {
    document.title = '数据资产管理平台'
  }

  // 从本地存储初始化用户信息（仅首次）
  if (!hasInitialized) {
    userStore.initFromStorage()
    hasInitialized = true
  }

  // 判断是否需要认证
  const requiresAuth = to.meta.requiresAuth !== false

  // 如果不需要认证，直接放行
  if (!requiresAuth) {
    // 如果已登录，访问登录页时重定向到首页
    if (to.path === '/login' && userStore.isLoggedIn) {
      next('/dashboard')
      return
    }
    next()
    return
  }

  // 需要认证但未登录，重定向到登录页
  if (!userStore.isLoggedIn) {
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
    return
  }

  // 已登录，生成权限路由（仅首次）
  if (!permissionStore.hasRoutes && userStore.role) {
    try {
      permissionStore.generateRoutes(userStore.role)
    } catch (error) {
      console.error('Failed to generate routes:', error)
      ElMessage.error('权限初始化失败')
      await userStore.logout()
      next('/login')
      return
    }
  }

  // 检查角色权限
  const roles = to.meta.roles as string[] | undefined
  if (roles && roles.length > 0) {
    if (!userStore.hasRole(roles)) {
      ElMessage.error('您没有权限访问该页面')
      // 如果是从其他页面跳转过来的，返回上一页；否则跳转到首页
      if (from.path && from.path !== '/login') {
        next(from.path)
      } else {
        next('/dashboard')
      }
      return
    }
  }

  // 检查路径权限
  if (!permissionStore.canAccessPath(to.path)) {
    ElMessage.error('您没有权限访问该页面')
    if (from.path && from.path !== '/login') {
      next(from.path)
    } else {
      next('/dashboard')
    }
    return
  }

  next()
})

// 路由错误处理
router.onError((error) => {
  console.error('Router error:', error)
  ElMessage.error('页面加载失败，请刷新重试')
})

// 404 处理
router.beforeResolve((to) => {
  // 如果路由不存在，重定向到 404
  if (to.matched.length === 0) {
    return '/404'
  }
})

export default router
