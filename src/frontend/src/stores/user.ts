import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, logout as apiLogout, refreshToken as apiRefreshToken, getMe, type LoginParams, type UserInfo } from '@/api/auth'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_INFO_KEY = 'user_info'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string>('')
  const refreshTokenValue = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const role = computed(() => userInfo.value?.role || '')
  const username = computed(() => userInfo.value?.username || '')
  const realName = computed(() => userInfo.value?.real_name || '')
  const organization = computed(() => userInfo.value?.organization || '')

  // 从本地存储初始化
  function initFromStorage() {
    const storedToken = localStorage.getItem(TOKEN_KEY)
    const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    const storedUserInfo = localStorage.getItem(USER_INFO_KEY)

    if (storedToken) {
      token.value = storedToken
    }
    if (storedRefreshToken) {
      refreshTokenValue.value = storedRefreshToken
    }
    if (storedUserInfo) {
      try {
        userInfo.value = JSON.parse(storedUserInfo)
      } catch (e) {
        console.error('Failed to parse user info from storage:', e)
      }
    }
  }

  // 保存到本地存储
  function saveToStorage() {
    if (token.value) {
      localStorage.setItem(TOKEN_KEY, token.value)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }

    if (refreshTokenValue.value) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshTokenValue.value)
    } else {
      localStorage.removeItem(REFRESH_TOKEN_KEY)
    }

    if (userInfo.value) {
      localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo.value))
    } else {
      localStorage.removeItem(USER_INFO_KEY)
    }
  }

  // 清除本地存储
  function clearStorage() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_INFO_KEY)
  }

  // 登录
  async function login(params: LoginParams) {
    try {
      const response = await apiLogin(params)
      const { access_token, refresh_token, user } = response.data

      token.value = access_token
      refreshTokenValue.value = refresh_token
      userInfo.value = user

      saveToStorage()

      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }

  // 登出
  async function logout() {
    try {
      await apiLogout()
    } catch (error) {
      console.error('Logout API failed:', error)
    } finally {
      // 无论API调用是否成功，都清除本地状态
      token.value = ''
      refreshTokenValue.value = ''
      userInfo.value = null
      clearStorage()
    }
  }

  // 刷新token
  async function refreshToken(): Promise<string> {
    if (!refreshTokenValue.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await apiRefreshToken(refreshTokenValue.value)
      const newToken = response.data.access_token

      token.value = newToken
      saveToStorage()

      return newToken
    } catch (error) {
      console.error('Refresh token failed:', error)
      // 刷新失败，清除所有状态
      token.value = ''
      refreshTokenValue.value = ''
      userInfo.value = null
      clearStorage()
      throw error
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const response = await getMe()
      userInfo.value = response.data
      saveToStorage()
      return userInfo.value
    } catch (error) {
      console.error('Fetch user info failed:', error)
      throw error
    }
  }

  // 检查是否有指定角色
  function hasRole(roles: string | string[]): boolean {
    if (!role.value) return false
    const roleArray = Array.isArray(roles) ? roles : [roles]
    return roleArray.includes(role.value)
  }

  return {
    // 状态
    token,
    refreshTokenValue,
    userInfo,
    // 计算属性
    isLoggedIn,
    role,
    username,
    realName,
    organization,
    // 方法
    initFromStorage,
    login,
    logout,
    refreshToken,
    fetchUserInfo,
    hasRole,
  }
})
