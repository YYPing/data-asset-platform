import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// API响应数据结构
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 是否正在刷新token
let isRefreshing = false
// 待重试的请求队列
let requestQueue: Array<(token: string) => void> = []

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    const token = userStore.token

    // 注入token
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data

    // 如果code不是200，认为是错误
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')

      // 401: 未授权，token过期或无效
      if (res.code === 401) {
        handleTokenExpired()
      }

      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  async (error: AxiosError<ApiResponse>) => {
    console.error('Response error:', error)

    // 处理401错误（token过期）
    if (error.response?.status === 401) {
      const config = error.config as AxiosRequestConfig & { _retry?: boolean }

      // 如果是刷新token接口失败，直接登出
      if (config.url?.includes('/auth/refresh')) {
        handleTokenExpired()
        return Promise.reject(error)
      }

      // 如果已经重试过，直接登出
      if (config._retry) {
        handleTokenExpired()
        return Promise.reject(error)
      }

      // 如果正在刷新token，将请求加入队列
      if (isRefreshing) {
        return new Promise((resolve) => {
          requestQueue.push((token: string) => {
            if (config.headers) {
              config.headers.Authorization = `Bearer ${token}`
            }
            resolve(service(config))
          })
        })
      }

      // 标记正在刷新token
      config._retry = true
      isRefreshing = true

      try {
        const userStore = useUserStore()
        const newToken = await userStore.refreshToken()

        // 更新队列中所有请求的token并重试
        requestQueue.forEach((callback) => callback(newToken))
        requestQueue = []

        // 重试当前请求
        if (config.headers) {
          config.headers.Authorization = `Bearer ${newToken}`
        }
        return service(config)
      } catch (refreshError) {
        // 刷新token失败，清空队列并登出
        requestQueue = []
        handleTokenExpired()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 其他错误处理
    const message = error.response?.data?.message || error.message || '网络请求失败'
    ElMessage.error(message)

    return Promise.reject(error)
  }
)

// 处理token过期
function handleTokenExpired() {
  const userStore = useUserStore()
  userStore.logout()
  router.push('/login')
  ElMessage.warning('登录已过期，请重新登录')
}

export default service
