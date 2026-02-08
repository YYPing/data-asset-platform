import { RouteRecordRaw } from 'vue-router'

/**
 * 检查用户是否有指定角色
 */
export function hasRole(userRole: string, requiredRoles?: string | string[]): boolean {
  if (!requiredRoles) return true
  if (!userRole) return false

  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]
  return roles.includes(userRole)
}

/**
 * 检查用户是否有指定权限
 */
export function hasPermission(userPermissions: string[], requiredPermission: string): boolean {
  if (!requiredPermission) return true
  if (!userPermissions || userPermissions.length === 0) return false

  return userPermissions.includes(requiredPermission)
}

/**
 * 根据角色过滤菜单
 */
export function filterMenusByRole(menus: RouteRecordRaw[], userRole: string): RouteRecordRaw[] {
  return menus.filter((menu) => {
    // 检查当前菜单是否有角色限制
    const roles = menu.meta?.roles as string[] | undefined
    if (roles && !hasRole(userRole, roles)) {
      return false
    }

    // 如果有子菜单，递归过滤
    if (menu.children && menu.children.length > 0) {
      menu.children = filterMenusByRole(menu.children, userRole)
      // 如果过滤后没有子菜单了，也不显示父菜单
      return menu.children.length > 0
    }

    return true
  })
}

/**
 * 根据角色获取可访问的路由路径列表
 */
export function getAccessiblePaths(routes: RouteRecordRaw[], userRole: string): string[] {
  const paths: string[] = []

  function traverse(routes: RouteRecordRaw[]) {
    routes.forEach((route) => {
      const roles = route.meta?.roles as string[] | undefined
      if (!roles || hasRole(userRole, roles)) {
        if (route.path) {
          paths.push(route.path)
        }
        if (route.children) {
          traverse(route.children)
        }
      }
    })
  }

  traverse(routes)
  return paths
}

/**
 * 检查路由是否可访问
 */
export function canAccessRoute(route: RouteRecordRaw, userRole: string): boolean {
  const roles = route.meta?.roles as string[] | undefined
  return !roles || hasRole(userRole, roles)
}
