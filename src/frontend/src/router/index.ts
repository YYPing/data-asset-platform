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
  // 数据大屏（独立布局，无需认证）
  {
    path: '/screen',
    name: 'DataScreen',
    component: () => import('@/views/screen/index.vue'),
    meta: {
      title: '数据资产大屏',
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
      // 资产管理
      {
        path: '/assets',
        name: 'Assets',
        redirect: '/assets/list',
        meta: {
          title: '资产管理',
          icon: 'Box',
          requiresAuth: true,
          roles: ['admin', 'asset_manager', 'viewer'],
        },
        children: [
          {
            path: '/assets/list',
            name: 'AssetList',
            component: () => import('@/views/assets/list.vue'),
            meta: {
              title: '资产列表',
              requiresAuth: true,
            },
          },
          {
            path: '/assets/create',
            name: 'AssetCreate',
            component: () => import('@/views/assets/create.vue'),
            meta: {
              title: '新建资产',
              requiresAuth: true,
              roles: ['admin', 'asset_manager'],
            },
          },
          {
            path: '/assets/:id',
            name: 'AssetDetail',
            component: () => import('@/views/assets/detail.vue'),
            meta: {
              title: '资产详情',
              requiresAuth: true,
            },
          },
          {
            path: '/assets/:id/edit',
            name: 'AssetEdit',
            component: () => import('@/views/assets/edit.vue'),
            meta: {
              title: '编辑资产',
              requiresAuth: true,
              roles: ['admin', 'asset_manager'],
            },
          },
        ],
      },
      // 材料管理
      {
        path: '/materials',
        name: 'Materials',
        component: () => import('@/views/materials/index.vue'),
        meta: {
          title: '材料管理',
          icon: 'Document',
          requiresAuth: true,
          roles: ['admin', 'asset_manager'],
        },
      },
      // 证书管理
      {
        path: '/certificates',
        name: 'Certificates',
        component: () => import('@/views/certificates/index.vue'),
        meta: {
          title: '证书管理',
          icon: 'Stamp',
          requiresAuth: true,
          roles: ['admin', 'asset_manager'],
        },
      },
      // 工作流管理
      {
        path: '/workflow',
        name: 'Workflow',
        redirect: '/workflow/instances',
        meta: {
          title: '工作流',
          icon: 'CircleCheck',
          requiresAuth: true,
          roles: ['admin', 'asset_manager', 'evaluator'],
        },
        children: [
          {
            path: '/workflow/instances',
            name: 'WorkflowInstances',
            component: () => import('@/views/workflow/instances.vue'),
            meta: {
              title: '流程实例',
              requiresAuth: true,
            },
          },
          {
            path: '/workflow/definitions',
            name: 'WorkflowDefinitions',
            component: () => import('@/views/workflow/definitions.vue'),
            meta: {
              title: '流程定义',
              requiresAuth: true,
              roles: ['admin'],
            },
          },
          {
            path: '/workflow/tasks',
            name: 'WorkflowTasks',
            component: () => import('@/views/workflow/tasks.vue'),
            meta: {
              title: '待办任务',
              requiresAuth: true,
            },
          },
        ],
      },
      // 评估管理
      {
        path: '/assessment',
        name: 'Assessment',
        redirect: '/assessment/records',
        meta: {
          title: '评估管理',
          icon: 'DataAnalysis',
          requiresAuth: true,
          roles: ['admin', 'evaluator'],
        },
        children: [
          {
            path: '/assessment/records',
            name: 'AssessmentRecords',
            component: () => import('@/views/assessment/records.vue'),
            meta: {
              title: '评估记录',
              requiresAuth: true,
            },
          },
          {
            path: '/assessment/templates',
            name: 'AssessmentTemplates',
            component: () => import('@/views/assessment/templates.vue'),
            meta: {
              title: '评估模板',
              requiresAuth: true,
              roles: ['admin'],
            },
          },
        ],
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
          roles: ['admin'],
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
          roles: ['admin'],
        },
        children: [
          {
            path: '/system/users',
            name: 'SystemUsers',
            component: () => import('@/views/system/users.vue'),
            meta: {
              title: '用户管理',
              icon: 'User',
              requiresAuth: true,
              roles: ['admin'],
            },
          },
          {
            path: '/system/organizations',
            name: 'SystemOrganizations',
            component: () => import('@/views/system/organizations.vue'),
            meta: {
              title: '机构管理',
              icon: 'OfficeBuilding',
              requiresAuth: true,
              roles: ['admin'],
            },
          },
          {
            path: '/system/dict',
            name: 'SystemDict',
            component: () => import('@/views/system/dict.vue'),
            meta: {
              title: '数据字典',
              icon: 'Collection',
              requiresAuth: true,
              roles: ['admin'],
            },
          },
          {
            path: '/system/config',
            name: 'SystemConfig',
            component: () => import('@/views/system/config.vue'),
            meta: {
              title: '系统配置',
              icon: 'Tools',
              requiresAuth: true,
              roles: ['admin'],
            },
          },
          {
            path: '/system/jobs',
            name: 'SystemJobs',
            component: () => import('@/views/system/jobs.vue'),
            meta: {
              title: '定时任务',
              icon: 'Timer',
              requiresAuth: true,
              roles: ['admin'],
            },
          },
        ],
      },
      // 个人中心
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: {
          title: '个人中心',
          requiresAuth: true,
        },
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
