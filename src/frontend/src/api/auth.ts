import request, { ApiResponse } from './request'

// 用户信息接口
export interface UserInfo {
  id: number
  username: string
  real_name: string
  role: string
  organization: string
}

// 登录请求参数
export interface LoginParams {
  username: string
  password: string
}

// 登录响应数据
export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: UserInfo
}

// 登录
export function login(data: LoginParams): Promise<ApiResponse<LoginResponse>> {
  return request({
    url: '/auth/login',
    method: 'post',
    data,
  })
}

// 登出
export function logout(): Promise<ApiResponse<null>> {
  return request({
    url: '/auth/logout',
    method: 'post',
  })
}

// 刷新token
export function refreshToken(refreshToken: string): Promise<ApiResponse<{ access_token: string }>> {
  return request({
    url: '/auth/refresh',
    method: 'post',
    data: { refresh_token: refreshToken },
  })
}

// 获取当前用户信息
export function getMe(): Promise<ApiResponse<UserInfo>> {
  return request({
    url: '/auth/me',
    method: 'get',
  })
}
