# 数据资产管理平台 - 前端基础框架

## 技术栈

- **Vue 3** + **TypeScript** + **Composition API**
- **Element Plus** - UI 组件库
- **Pinia** - 状态管理
- **Vue Router 4** - 路由管理
- **Axios** - HTTP 请求
- **Vite** - 构建工具

## 项目结构

```
src/frontend/src/
├── api/                    # API 接口
│   ├── request.ts         # Axios 封装（请求/响应拦截、错误处理、token 刷新）
│   ├── auth.ts            # 认证相关 API
│   └── ...
├── assets/                # 静态资源
├── components/            # 全局组件
│   ├── Loading.vue        # 加载组件
│   ├── ErrorTip.vue       # 错误提示组件
│   ├── EmptyState.vue     # 空状态组件
│   ├── Pagination.vue     # 分页组件
│   └── Permission.vue     # 权限组件
├── directives/            # 自定义指令
│   └── permission.ts      # 权限指令（v-permission, v-role）
├── layouts/               # 布局组件
│   ├── MainLayout.vue     # 主布局（侧边栏+顶部导航）
│   └── LoginLayout.vue    # 登录布局
├── router/                # 路由配置
│   └── index.ts           # 路由守卫、权限检查、动态路由
├── stores/                # Pinia 状态管理
│   ├── user.ts            # 用户状态（登录、登出、token 管理）
│   ├── permission.ts      # 权限状态（角色权限、菜单权限）
│   └── app.ts             # 应用状态（主题、语言、配置）
├── styles/                # 全局样式
│   └── global.css         # 全局样式变量、工具类
├── utils/                 # 工具函数
│   ├── permission.ts      # 权限工具函数
│   ├── request.ts         # 请求工具（已在 api/request.ts）
│   └── validate.ts        # 表单验证工具
├── views/                 # 页面组件
│   ├── login/             # 登录页面
│   ├── dashboard/         # 首页
│   ├── assets/            # 资产管理
│   ├── workflow/          # 工作流
│   ├── error/             # 错误页面（404）
│   └── ...
├── App.vue                # 根组件
└── main.ts                # 入口文件
```

## 核心功能

### 1. 用户认证与授权

#### 登录流程
```typescript
// 1. 用户登录
const userStore = useUserStore()
await userStore.login({ username, password })

// 2. 自动保存 token 到 localStorage
// 3. 自动在请求头中携带 token
// 4. token 过期自动刷新
// 5. 刷新失败自动跳转登录页
```

#### 角色权限
系统支持 7 种角色：
- **admin** - 所有菜单
- **center_auditor** - 资产审核、工作流审批、统计分析
- **evaluator** - 评估管理、我的评估
- **data_holder** - 资产登记、我的资产、材料上传
- **auditor** - 审计日志、合规检查
- **regulator** - 监管查询、统计分析
- **system** - 系统监控、任务管理

### 2. 路由权限控制

#### 路由守卫
```typescript
// 自动检查：
// 1. 是否需要登录
// 2. 是否有访问权限
// 3. 角色是否匹配
// 4. 自动重定向到登录页或 404
```

#### 路由配置示例
```typescript
{
  path: '/assets',
  name: 'Assets',
  component: () => import('@/views/assets/index.vue'),
  meta: {
    title: '资产管理',
    icon: 'Box',
    requiresAuth: true,
    roles: ['admin', 'center_auditor', 'data_holder'], // 角色限制
  },
}
```

### 3. 权限指令

#### v-permission 指令
```vue
<!-- 简化写法：角色数组 -->
<el-button v-permission="['admin']">删除</el-button>

<!-- 对象写法：支持多种权限判断 -->
<el-button v-permission="{ roles: ['admin', 'auditor'], mode: 'or' }">
  审核
</el-button>

<!-- 菜单权限 -->
<div v-permission="{ menu: '/assets' }">资产管理内容</div>
```

#### v-role 指令
```vue
<!-- 简化的角色判断 -->
<el-button v-role="'admin'">管理员功能</el-button>
<div v-role="['admin', 'auditor']">管理员或审核员可见</div>
```

### 4. 权限组件

```vue
<template>
  <Permission :roles="['admin', 'auditor']">
    <el-button>审核</el-button>
  </Permission>

  <Permission :menu="'/assets'">
    <div>资产管理内容</div>
  </Permission>
</template>
```

### 5. 状态管理

#### 用户状态（useUserStore）
```typescript
const userStore = useUserStore()

// 登录
await userStore.login({ username, password })

// 登出
await userStore.logout()

// 获取用户信息
userStore.userInfo
userStore.role
userStore.username

// 检查角色
userStore.hasRole(['admin', 'auditor'])
```

#### 权限状态（usePermissionStore）
```typescript
const permissionStore = usePermissionStore()

// 生成权限路由
permissionStore.generateRoutes(role)

// 检查路径权限
permissionStore.canAccessPath('/assets')

// 检查菜单权限
permissionStore.hasMenuPermission('/assets')

// 获取菜单列表
const menus = permissionStore.getMenus()
```

#### 应用状态（useAppStore）
```typescript
const appStore = useAppStore()

// 切换主题
appStore.toggleTheme()

// 切换侧边栏
appStore.toggleSidebar()

// 显示/隐藏加载
appStore.showLoading('加载中...')
appStore.hideLoading()

// 更新配置
appStore.updateConfig({ theme: 'dark', language: 'zh-CN' })
```

### 6. API 请求

#### 自动功能
- ✅ 自动携带 JWT token
- ✅ token 过期自动刷新
- ✅ 401 自动跳转登录
- ✅ 请求重试机制
- ✅ 统一错误处理
- ✅ 请求/响应拦截

#### 使用示例
```typescript
import request from '@/api/request'

// GET 请求
const response = await request({
  url: '/assets',
  method: 'get',
  params: { page: 1, size: 20 },
})

// POST 请求
const response = await request({
  url: '/assets',
  method: 'post',
  data: { name: '资产名称' },
})
```

### 7. 表单验证

#### 内置验证规则
```typescript
import { requiredRule, emailRule, phoneRule, usernameRule } from '@/utils/validate'

const rules = {
  username: [requiredRule(), usernameRule()],
  email: [requiredRule(), emailRule()],
  phone: [phoneRule()],
  password: [requiredRule(), lengthRule(6, 20)],
}
```

#### 自定义验证函数
```typescript
import { validateEmail, validatePhone, validateURL } from '@/utils/validate'

if (!validateEmail(email)) {
  ElMessage.error('邮箱格式不正确')
}
```

### 8. 全局组件

#### Loading 组件
```vue
<Loading :visible="loading" text="加载中..." :fullscreen="true" />
```

#### ErrorTip 组件
```vue
<ErrorTip
  type="error"
  title="加载失败"
  message="无法加载数据，请稍后重试"
  :closable="true"
  @close="handleClose"
/>
```

#### EmptyState 组件
```vue
<EmptyState type="no-data" text="暂无数据">
  <el-button type="primary">添加数据</el-button>
</EmptyState>
```

#### Pagination 组件
```vue
<Pagination
  :total="total"
  :page="page"
  :page-size="pageSize"
  @change="handlePageChange"
/>
```

### 9. 布局系统

#### 主布局（MainLayout）
- 侧边栏（可折叠）
- 顶部导航（面包屑、用户信息）
- 主题切换
- 全屏功能
- 通知中心
- 响应式设计

#### 登录布局（LoginLayout）
- 渐变背景
- 动画效果
- 响应式设计

### 10. 主题系统

#### 亮色/暗色主题
```typescript
// 切换主题
appStore.toggleTheme()

// 设置主题
appStore.updateConfig({ theme: 'dark' })
```

#### CSS 变量
```css
/* 使用主题变量 */
.my-component {
  color: var(--color-text-primary);
  background-color: var(--color-bg-base);
  border: 1px solid var(--color-border-base);
}
```

## 开发指南

### 添加新页面

1. 在 `views/` 下创建页面组件
2. 在 `router/index.ts` 中添加路由配置
3. 设置权限（roles）
4. 在菜单中显示（meta.title, meta.icon）

### 添加新 API

1. 在 `api/` 下创建 API 文件
2. 定义接口类型
3. 使用 `request` 函数发起请求

### 添加新权限

1. 在 `stores/permission.ts` 中更新 `roleMenuMap`
2. 在路由配置中设置 `meta.roles`
3. 使用 `v-permission` 或 `Permission` 组件控制显示

## 最佳实践

1. **使用 Composition API**：所有组件使用 `<script setup>` 语法
2. **TypeScript 类型**：为所有 API、Props、State 定义类型
3. **权限控制**：页面级用路由守卫，按钮级用指令或组件
4. **错误处理**：使用 try-catch 和 ElMessage 提示
5. **加载状态**：异步操作显示 loading 状态
6. **响应式设计**：使用 Element Plus 栅格系统
7. **代码复用**：提取公共逻辑到 composables

## 环境变量

```env
# 开发环境
VITE_API_BASE_URL=http://localhost:8000/api/v1

# 生产环境
VITE_API_BASE_URL=https://api.example.com/api/v1
```

## 快速开始

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 开发环境快速登录

开发环境下，登录页面会显示快速登录提示，可以一键登录测试账号：

- **管理员**：admin / admin123
- **审核员**：auditor / auditor123
- **数据持有方**：holder / holder123
- **评估机构**：evaluator / evaluator123

## 注意事项

1. **Token 管理**：token 自动保存到 localStorage，刷新页面不会丢失登录状态
2. **权限刷新**：角色变更后需要重新登录才能生效
3. **路由守卫**：所有需要认证的页面都会自动检查登录状态
4. **API 错误**：401 错误会自动跳转登录页，其他错误会显示提示
5. **主题持久化**：主题设置会保存到 localStorage

## 待完善功能

- [ ] 国际化（i18n）完整配置
- [ ] 验证码功能
- [ ] 第三方登录集成
- [ ] 更多基础组件（表格、表单等）
- [ ] 单元测试
- [ ] E2E 测试

## 技术支持

如有问题，请联系开发团队或查看项目文档。
