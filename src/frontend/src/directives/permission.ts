import { App, Directive } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'

/**
 * 权限指令
 * 用法：
 * v-permission="['admin']" - 需要 admin 角色
 * v-permission="{ roles: ['admin', 'user'], mode: 'or' }" - 需要 admin 或 user 角色
 * v-permission="{ menu: '/assets' }" - 需要访问 /assets 菜单的权限
 */
interface PermissionBinding {
  roles?: string | string[]
  menu?: string
  mode?: 'and' | 'or'
}

const permissionDirective: Directive = {
  mounted(el, binding) {
    const userStore = useUserStore()
    const permissionStore = usePermissionStore()

    let hasPermission = false

    // 简化写法：直接传入角色数组或字符串
    if (Array.isArray(binding.value) || typeof binding.value === 'string') {
      const roles = Array.isArray(binding.value) ? binding.value : [binding.value]
      hasPermission = roles.includes(userStore.role)
    }
    // 对象写法：支持更复杂的权限判断
    else if (typeof binding.value === 'object') {
      const { roles, menu, mode = 'or' } = binding.value as PermissionBinding
      const checks: boolean[] = []

      // 检查角色权限
      if (roles) {
        const roleArray = Array.isArray(roles) ? roles : [roles]
        checks.push(roleArray.includes(userStore.role))
      }

      // 检查菜单权限
      if (menu) {
        checks.push(permissionStore.hasMenuPermission(menu))
      }

      if (checks.length === 0) {
        hasPermission = true
      } else if (mode === 'and') {
        hasPermission = checks.every((check) => check)
      } else {
        hasPermission = checks.some((check) => check)
      }
    }

    // 如果没有权限，移除元素
    if (!hasPermission) {
      el.parentNode?.removeChild(el)
    }
  },
}

/**
 * 角色指令（简化版）
 * 用法：v-role="'admin'" 或 v-role="['admin', 'user']"
 */
const roleDirective: Directive = {
  mounted(el, binding) {
    const userStore = useUserStore()
    const roles = Array.isArray(binding.value) ? binding.value : [binding.value]
    const hasRole = roles.includes(userStore.role)

    if (!hasRole) {
      el.parentNode?.removeChild(el)
    }
  },
}

/**
 * 注册所有权限相关指令
 */
export function setupPermissionDirectives(app: App) {
  app.directive('permission', permissionDirective)
  app.directive('role', roleDirective)
}

export default {
  install(app: App) {
    setupPermissionDirectives(app)
  },
}
