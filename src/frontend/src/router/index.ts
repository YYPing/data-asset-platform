import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
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
    path: '/',
    name: 'Layout',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    meta: {
      requiresAuth: true,
    },
    children: [
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
      {
        path: '/assets',
        name: 'Assets',
        component: () => import('@/views/placeholder.vue'),
        meta: {
          title: '资产管理',
          icon: 'Box',
          requiresAuth: true,
          roles: ['holder_admin', 'holder_user', 'center_admin', 'center_user'],
        },
      },
      {
        path: '/materials',
        name: 'Materials',
        component: () => import('@/views/placeholder.vue'),
        meta: {
          title: '材料管理',
          icon: 'Document',
          requiresAuth: true,
          roles: ['holder_admin', 'holder_user'],
        },
      },
      {
        path: '/workflow',
        name: 'Workflow',
        component: () => import('@/views/placeholder.vue'),
        meta: {
          title: '审批管理',
          icon: 'CircleCheck',
          requiresAuth: true,
          roles: ['center_admin', 'center_user'],
        },
      },
      {
        path: '/assessment',
        name: 'Assessment',
        component: () => import('@/views/placeholder.vue'),
        meta: {
          title: '评估管理',
          icon: 'DataAnalysis',
          requiresAuth: true,
          roles: ['evaluator', 'center_admin'],
        },
      },
      {
        path: '/statistics',
        name: 'Statistics',
        component: () => import('@/views/placeholder.vue'),
        meta: {
          title: '统计分析',
          icon: 'TrendCharts',
          requiresAuth: true,
          roles: ['center_admin', 'center_user', 'auditor'],
        },
      },
      {
        path: '/audit',
        name: 'Audit',
        component: () => import('@/views/placeholder.vue'),
        meta: {
          title: '审计日志',
          icon: 'List',
          requiresAuth: true,
          roles: ['auditor', 'sys_admin'],
        },
      },
      {
        path: '/system',
        name: 'System',
        redirect: '/system/users',
        meta: {
          title: '系统管理',
          icon: 'Setting',
          requiresAuth: true,
          roles: ['sys_admin'],
        },
        children: [
          {
            path: '/system/users',
            name: 'SystemUsers',
            component: () => import('@/views/placeholder.vue'),
            meta: {
              title: '用户管理',
              icon: 'User',
              requiresAuth: true,
              roles: ['sys_admin'],
            },
          },
          {
            path: '/system/roles',
            name: 'SystemRoles',
            component: () => import('@/views/placeholder.vue'),
            meta: {
              title: '角色管理',
              icon: 'UserFilled',
              requiresAuth: true,
              roles: ['sys_admin'],
            },
          },
          {
            path: '/system/dict',
            name: 'SystemDict',
            component: () => import('@/views/placeholder.vue'),
            meta: {
              title: '数据字典',
              icon: 'Collection',
              requiresAuth: true,
              roles: ['sys_admin'],
            },
          },
          {
            path: '/system/config',
            name: 'SystemConfig',
            component: () => import('@/views/placeholder.vue'),
            meta: {
              title: '系统配置',
              icon: 'Tools',
              requiresAuth: true,
              roles: ['sys_admin'],
            },
          },
        ],
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 数据资产管理平台`
  }

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

  // 检查角色权限
  const roles = to.meta.roles as string[] | undefined
  if (roles && roles.length > 0) {
    if (!userStore.hasRole(roles)) {
      ElMessage.error('您没有权限访问该页面')
      next(from.path || '/dashboard')
      return
    }
  }

  next()
})

export default router
