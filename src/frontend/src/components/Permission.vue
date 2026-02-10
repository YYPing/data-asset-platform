<template>
  <div v-if="hasPermission" class="permission-wrapper">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'

interface Props {
  // 需要的角色（满足其一即可）
  roles?: string | string[]
  // 需要的权限（满足其一即可）
  permissions?: string | string[]
  // 需要的菜单权限
  menu?: string
  // 逻辑模式：and（同时满足）或 or（满足其一）
  mode?: 'and' | 'or'
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'or',
})

const userStore = useUserStore()
const permissionStore = usePermissionStore()

// 检查角色权限
const hasRolePermission = computed(() => {
  if (!props.roles) return true

  const roles = Array.isArray(props.roles) ? props.roles : [props.roles]
  return roles.includes(userStore.role)
})

// 检查菜单权限
const hasMenuPermission = computed(() => {
  if (!props.menu) return true
  return permissionStore.hasMenuPermission(props.menu)
})

// 检查自定义权限（预留，可扩展）
const hasCustomPermission = computed(() => {
  if (!props.permissions) return true
  // 这里可以根据实际需求实现权限检查逻辑
  return true
})

// 综合权限判断
const hasPermission = computed(() => {
  const checks = []

  if (props.roles) checks.push(hasRolePermission.value)
  if (props.menu) checks.push(hasMenuPermission.value)
  if (props.permissions) checks.push(hasCustomPermission.value)

  if (checks.length === 0) return true

  if (props.mode === 'and') {
    return checks.every((check) => check)
  } else {
    return checks.some((check) => check)
  }
})
</script>

<style scoped>
.permission-wrapper {
  display: contents;
}
</style>
