# API接口规范

## 通用规范
- 前缀: `/api/v1/`
- 认证: `Authorization: Bearer <token>`（除登录/注册外）
- 响应格式:
```json
{"code": 200, "message": "success", "data": {...}}
```
- 分页: `?page=1&page_size=20`，响应含 `{"items": [...], "total": N, "page": 1, "page_size": 20}`
- 错误码: 40001-40099认证, 40100-40199权限, 40200-40299资产, 40300-40399材料, 40400-40499工作流, 50000系统错误

## 接口清单

### 认证 /api/v1/auth/
- POST /login — 登录（username+password → access_token+refresh_token）
- POST /refresh — 刷新token
- POST /logout — 登出（token加黑名单）
- GET /me — 当前用户信息
- PUT /me/password — 修改密码

### 用户管理 /api/v1/users/
- GET / — 用户列表（分页+搜索）
- POST / — 创建用户
- GET /{id} — 用户详情
- PUT /{id} — 更新用户
- DELETE /{id} — 删除用户（软删除）
- PUT /{id}/role — 修改角色
- PUT /{id}/status — 启用/禁用

### 数据资产 /api/v1/assets/
- GET / — 资产列表（分页+搜索+筛选status/org）
- POST / — 创建资产（草稿）
- GET /{id} — 资产详情（含材料列表+工作流状态）
- PUT /{id} — 更新资产
- DELETE /{id} — 删除（仅草稿状态）
- POST /{id}/submit — 提交审批
- GET /search?q= — 全文搜索（zhparser）

### 材料 /api/v1/materials/
- POST /upload — 上传材料（multipart，自动算SHA256）
- GET /{asset_id} — 资产材料列表
- GET /{id}/download — 下载
- GET /{id}/verify — 验证哈希
- GET /checklist/{stage} — 阶段材料清单

### 登记证书 /api/v1/certificates/
- POST /import — 导入证书（文件+证书信息）
- GET /{asset_id} — 资产证书列表
- GET /{id}/verify — 验证证书哈希
- PUT /{id} — 更新证书（续期等）
- GET /expiring — 即将过期证书列表

### 工作流 /api/v1/workflow/
- POST /start/{asset_id} — 启动审批流程
- GET /{asset_id}/status — 流程状态
- POST /approve/{node_id} — 审批通过
- POST /reject/{node_id} — 驳回（含原因+回退环节）
- POST /correct/{asset_id} — 提交补正
- GET /pending — 我的待办
- GET /history/{asset_id} — 审批历史

### 评估 /api/v1/assessment/
- POST /compliance/{asset_id} — 提交合规评估
- POST /valuation/{asset_id} — 提交价值评估
- GET /{asset_id} — 评估结果
- PUT /{id} — 更新评估

### 统计 /api/v1/statistics/
- GET /overview — 总览数据
- GET /holder/dashboard — 持有方大屏数据
- GET /center/dashboard — 登记中心大屏数据
- GET /trend — 趋势数据（按时间）

### 审计 /api/v1/audit/
- GET /logs — 审计日志列表（分页+筛选）
- GET /logs/{id} — 日志详情

### 通知 /api/v1/notifications/
- GET / — 通知列表
- PUT /{id}/read — 标记已读
- PUT /read-all — 全部已读
- GET /unread-count — 未读数量

### 系统 /api/v1/system/
- GET /config — 系统配置
- PUT /config — 更新配置
- GET /dict/{type} — 数据字典
- GET /health — 健康检查
