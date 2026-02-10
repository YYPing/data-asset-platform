import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { RouteRecordRaw } from 'vue-router'
import router from '@/router'
import { filterMenusByRole, getAccessiblePaths } from '@/utils/permission'

// 角色对应的菜单权限配置
const roleMenuMap: Record<string, string[]> = {
  admin: ['*'], // 所有菜单
  center_auditor: ['/assets', '/workflow', '/statistics', '/audit'],
  evaluator: ['/assessment', '/workflow'],
  data_holder: ['/assets', '/materials', '/certificates'],
  auditor: ['/audit', '/statistics'],
  regulator: ['/statistics', '/audit'],
  system: ['/system', '/audit'],
}

export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const routes = ref<RouteRecordRaw[]>([])
  const accessiblePaths = ref<string[]>([])
  const menuPermissions = ref<string[]>([])

  // 计算属性
  const hasRoutes = computed(() => routes.value.length > 0)

  /**
   * 根据角色生成可访问的路由
   */
  function generateRoutes(role: string): RouteRecordRaw[] {
    const allRoutes = router.getRoutes()
    const layoutRoute = allRoutes.find((r) => r.name === 'Layout')

    if (!layoutRoute || !layoutRoute.children) {
      return []
    }

    // 根据角色过滤路由
    const filteredRoutes = filterMenusByRole(layoutRoute.children, role)
    routes.value = filteredRoutes

    // 生成可访问路径列表
    accessiblePaths.value = getAccessiblePaths(filteredRoutes, role)

    // 生成菜单权限列表
    menuPermissions.value = roleMenuMap[role] || []

    return filteredRoutes
  }

  /**
   * 检查是否有访问指定路径的权限
   */
  function canAccessPath(path: string): boolean {
    // admin 角色拥有所有权限
    if (menuPermissions.value.includes('*')) {
      return true
    }

    // 检查路径是否在可访问列表中
    return accessiblePaths.value.some((p) => {
      // 精确匹配
      if (p === path) return true
      // 前缀匹配（用于子路由）
      if (path.startsWith(p + '/')) return true
      return false
    })
  }

  /**
   * 检查是否有指定菜单的权限
   */
  function hasMenuPermission(menuPath: string): boolean {
    // admin 角色拥有所有权限
    if (menuPermissions.value.includes('*')) {
      return true
    }

    return menuPermissions.value.includes(menuPath)
  }

  /**
   * 获取用户的菜单列表
   */
  function getMenus(): RouteRecordRaw[] {
    return routes.value.filter((route) => {
      // 过滤掉不在菜单中显示的路由
      return route.meta?.title && !route.meta?.hideInMenu
    })
  }

  /**
   * 重置权限状态
   */
  function reset() {
    routes.value = []
    accessiblePaths.value = []
    menuPermissions.value = []
  }

  return {
    // 状态
    routes,
    accessiblePaths,
    menuPermissions,
    // 计算属性
    hasRoutes,
    // 方法
    generateRoutes,
    canAccessPath,
    hasMenuPermission,
    getMenus,
    reset,
  }
})
