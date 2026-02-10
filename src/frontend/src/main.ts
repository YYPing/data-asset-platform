import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import permissionDirectives from './directives/permission'
import './styles/global.css'

// 导入 stores 以便初始化
import { useUserStore } from './stores/user'
import { useAppStore } from './stores/app'

const app = createApp(App)
const pinia = createPinia()

// 注册 Pinia
app.use(pinia)

// 初始化应用配置
const appStore = useAppStore()
appStore.initFromStorage()

// 初始化用户信息
const userStore = useUserStore()
userStore.initFromStorage()

// 注册路由
app.use(router)

// 注册 Element Plus
app.use(ElementPlus, {
  locale: zhCn,
  size: 'default',
})

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册权限指令
app.use(permissionDirectives)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err)
  console.error('Error info:', info)
  console.error('Component instance:', instance)
}

// 全局警告处理
app.config.warnHandler = (msg, instance, trace) => {
  console.warn('Global warning:', msg)
  console.warn('Warning trace:', trace)
}

app.mount('#app')
