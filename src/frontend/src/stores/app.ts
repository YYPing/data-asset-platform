import { defineStore } from 'pinia'
import { ref } from 'vue'

// 主题类型
export type ThemeMode = 'light' | 'dark'

// 语言类型
export type Language = 'zh-CN' | 'en-US'

// 应用配置接口
export interface AppConfig {
  theme: ThemeMode
  language: Language
  sidebarCollapsed: boolean
  showBreadcrumb: boolean
  showTags: boolean
  fixedHeader: boolean
  pageSize: number
}

const APP_CONFIG_KEY = 'app_config'

// 默认配置
const defaultConfig: AppConfig = {
  theme: 'light',
  language: 'zh-CN',
  sidebarCollapsed: false,
  showBreadcrumb: true,
  showTags: true,
  fixedHeader: true,
  pageSize: 20,
}

export const useAppStore = defineStore('app', () => {
  // 状态
  const config = ref<AppConfig>({ ...defaultConfig })
  const loading = ref(false)
  const loadingText = ref('')

  /**
   * 从本地存储初始化配置
   */
  function initFromStorage() {
    const storedConfig = localStorage.getItem(APP_CONFIG_KEY)
    if (storedConfig) {
      try {
        const parsed = JSON.parse(storedConfig)
        config.value = { ...defaultConfig, ...parsed }
        applyTheme(config.value.theme)
      } catch (e) {
        console.error('Failed to parse app config from storage:', e)
      }
    }
  }

  /**
   * 保存配置到本地存储
   */
  function saveToStorage() {
    localStorage.setItem(APP_CONFIG_KEY, JSON.stringify(config.value))
  }

  /**
   * 更新配置
   */
  function updateConfig(newConfig: Partial<AppConfig>) {
    config.value = { ...config.value, ...newConfig }
    saveToStorage()

    // 如果主题改变，应用主题
    if (newConfig.theme) {
      applyTheme(newConfig.theme)
    }
  }

  /**
   * 切换主题
   */
  function toggleTheme() {
    const newTheme = config.value.theme === 'light' ? 'dark' : 'light'
    updateConfig({ theme: newTheme })
  }

  /**
   * 应用主题
   */
  function applyTheme(theme: ThemeMode) {
    const html = document.documentElement
    if (theme === 'dark') {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }

  /**
   * 切换侧边栏折叠状态
   */
  function toggleSidebar() {
    updateConfig({ sidebarCollapsed: !config.value.sidebarCollapsed })
  }

  /**
   * 设置语言
   */
  function setLanguage(language: Language) {
    updateConfig({ language })
  }

  /**
   * 显示全局加载
   */
  function showLoading(text = '加载中...') {
    loading.value = true
    loadingText.value = text
  }

  /**
   * 隐藏全局加载
   */
  function hideLoading() {
    loading.value = false
    loadingText.value = ''
  }

  /**
   * 重置配置
   */
  function reset() {
    config.value = { ...defaultConfig }
    localStorage.removeItem(APP_CONFIG_KEY)
    applyTheme(defaultConfig.theme)
  }

  return {
    // 状态
    config,
    loading,
    loadingText,
    // 方法
    initFromStorage,
    updateConfig,
    toggleTheme,
    toggleSidebar,
    setLanguage,
    showLoading,
    hideLoading,
    reset,
  }
})
