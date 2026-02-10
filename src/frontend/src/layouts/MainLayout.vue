<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="sidebarWidth" class="main-layout__aside">
      <div class="sidebar-header">
        <transition name="fade">
          <img v-if="!isCollapsed" src="/logo.png" alt="Logo" class="sidebar-logo" />
        </transition>
        <transition name="fade">
          <span v-if="!isCollapsed" class="sidebar-title">数据资产平台</span>
        </transition>
        <transition name="fade">
          <span v-if="isCollapsed" class="sidebar-title-mini">数</span>
        </transition>
      </div>

      <el-scrollbar class="sidebar-scrollbar">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapsed"
          :unique-opened="true"
          :collapse-transition="false"
          router
          class="sidebar-menu"
        >
          <template v-for="item in menuList" :key="item.path">
            <!-- 无子菜单 -->
            <el-menu-item v-if="!item.children || item.children.length === 0" :index="item.path">
              <el-icon v-if="item.meta?.icon">
                <component :is="item.meta.icon" />
              </el-icon>
              <template #title>{{ item.meta?.title }}</template>
            </el-menu-item>

            <!-- 有子菜单 -->
            <el-sub-menu v-else :index="item.path">
              <template #title>
                <el-icon v-if="item.meta?.icon">
                  <component :is="item.meta.icon" />
                </el-icon>
                <span>{{ item.meta?.title }}</span>
              </template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.path"
                :index="child.path"
              >
                <el-icon v-if="child.meta?.icon">
                  <component :is="child.meta.icon" />
                </el-icon>
                <template #title>{{ child.meta?.title }}</template>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-layout__container">
      <!-- 顶部导航 -->
      <el-header class="main-layout__header" :class="{ 'is-fixed': appStore.config.fixedHeader }">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleSidebar">
            <component :is="isCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>

          <el-breadcrumb v-if="appStore.config.showBreadcrumb" separator="/" class="breadcrumb">
            <el-breadcrumb-item
              v-for="(item, index) in breadcrumbs"
              :key="index"
              :to="index === breadcrumbs.length - 1 ? undefined : item.path"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 主题切换 -->
          <el-tooltip content="切换主题" placement="bottom">
            <el-icon class="header-icon" @click="toggleTheme">
              <component :is="appStore.config.theme === 'dark' ? 'Sunny' : 'Moon'" />
            </el-icon>
          </el-tooltip>

          <!-- 全屏 -->
          <el-tooltip content="全屏" placement="bottom">
            <el-icon class="header-icon" @click="toggleFullscreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>

          <!-- 通知 -->
          <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="notification-badge">
            <el-icon class="header-icon" @click="goToNotifications">
              <Bell />
            </el-icon>
          </el-badge>

          <!-- 用户信息 -->
          <el-dropdown @command="handleUserCommand" class="user-dropdown">
            <div class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="user-name">{{ userStore.realName || userStore.username }}</span>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <div class="user-detail">
                    <div class="user-detail-name">{{ userStore.realName }}</div>
                    <div class="user-detail-role">{{ getRoleLabel(userStore.role) }}</div>
                    <div class="user-detail-org">{{ userStore.organization }}</div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item divided command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-layout__content">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <keep-alive :include="cachedViews">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- 全局加载 -->
    <Loading v-if="appStore.loading" :text="appStore.loadingText" fullscreen />
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  UserFilled,
  ArrowDown,
  SwitchButton,
  User,
  Setting,
  Fold,
  Expand,
  Sunny,
  Moon,
  FullScreen,
  Bell,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { usePermissionStore } from '@/stores/permission'
import Loading from '@/components/Loading.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

// 侧边栏折叠状态
const isCollapsed = computed(() => appStore.config.sidebarCollapsed)
const sidebarWidth = computed(() => (isCollapsed.value ? '64px' : '240px'))

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 面包屑
const breadcrumbs = computed(() => {
  const matched = route.matched.filter((item) => item.meta?.title)
  return matched.map((item) => ({
    path: item.path,
    title: item.meta?.title as string,
  }))
})

// 菜单列表
const menuList = computed(() => {
  return permissionStore.getMenus()
})

// 缓存的视图（用于 keep-alive）
const cachedViews = ref<string[]>([])

// 通知数量（示例，实际应从 API 获取）
const notificationCount = ref(0)

// 切换侧边栏
const toggleSidebar = () => {
  appStore.toggleSidebar()
}

// 切换主题
const toggleTheme = () => {
  appStore.toggleTheme()
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 跳转到通知中心
const goToNotifications = () => {
  router.push('/notifications')
}

// 获取角色标签
const getRoleLabel = (role: string): string => {
  const roleMap: Record<string, string> = {
    admin: '系统管理员',
    center_auditor: '登记中心审核员',
    evaluator: '评估机构',
    data_holder: '数据持有方',
    auditor: '审计人员',
    regulator: '监管人员',
    system: '系统运维',
  }
  return roleMap[role] || role
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        })
        await userStore.logout()
        router.push('/login')
      } catch (error) {
        // 用户取消
      }
      break
  }
}

// 初始化权限路由
watch(
  () => userStore.isLoggedIn,
  (isLoggedIn) => {
    if (isLoggedIn && userStore.role) {
      permissionStore.generateRoutes(userStore.role)
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.main-layout {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.main-layout__aside {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  padding: 0 16px;
  background-color: #002140;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-logo {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.sidebar-title {
  flex: 1;
}

.sidebar-title-mini {
  font-size: 24px;
}

.sidebar-scrollbar {
  height: calc(100vh - 60px);
}

.sidebar-menu {
  border-right: none;
  background-color: #001529;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.65);
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.08) !important;
}

:deep(.el-menu-item.is-active) {
  color: #fff;
  background-color: #1890ff !important;
}

:deep(.el-sub-menu .el-menu-item) {
  background-color: #000c17 !important;
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
}

.main-layout__container {
  flex-direction: column;
  overflow: hidden;
}

.main-layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: #fff;
  border-bottom: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 999;
}

.main-layout__header.is-fixed {
  position: sticky;
  top: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: #409eff;
}

.breadcrumb {
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
  color: #606266;
}

.header-icon:hover {
  color: #409eff;
}

.notification-badge {
  cursor: pointer;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.user-name {
  font-size: 14px;
  color: #333;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow-icon {
  font-size: 12px;
  color: #999;
}

.user-detail {
  padding: 8px 0;
  text-align: center;
  font-size: 14px;
  min-width: 150px;
}

.user-detail-name {
  font-weight: 600;
  color: #303133;
}

.user-detail-role {
  margin-top: 4px;
  font-size: 12px;
  color: #409eff;
}

.user-detail-org {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.main-layout__content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* 暗色主题 */
:global(.dark) .main-layout__header {
  background-color: #1f1f1f;
  border-bottom-color: #333;
}

:global(.dark) .main-layout__content {
  background-color: #141414;
}

:global(.dark) .user-info:hover {
  background-color: #333;
}

:global(.dark) .user-name {
  color: #fff;
}
</style>
