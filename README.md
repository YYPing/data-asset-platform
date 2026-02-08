# 数据资产管理平台 - 快速启动指南

## 项目概述

数据资产管理平台是一个完整的数据资产全生命周期管理系统，提供资产登记、审批流程、评估管理、统计分析等功能。

## 技术栈

### 后端
- FastAPI - 现代化的 Python Web 框架
- SQLAlchemy - ORM 框架
- PostgreSQL - 关系型数据库
- Redis - 缓存和会话管理
- MinIO - 对象存储
- APScheduler - 定时任务调度

### 前端
- Vue 3 - 渐进式 JavaScript 框架
- TypeScript - 类型安全
- Element Plus - UI 组件库
- Pinia - 状态管理
- Vue Router - 路由管理
- Axios - HTTP 客户端

## 快速启动

### 方式一：使用 Docker Compose（推荐）

1. **确保已安装 Docker 和 Docker Compose**

2. **启动所有服务**
```bash
cd /Users/guiping/.openclaw/workspace/data-asset-platform
docker-compose up -d
```

3. **初始化数据库**
```bash
# 等待数据库启动完成（约10秒）
sleep 10

# 运行初始化脚本
docker-compose exec backend python /app/../scripts/init_db.py
```

4. **访问应用**
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/api/docs
- MinIO 控制台: http://localhost:9001

5. **默认登录账号**
- 管理员: `admin` / `Admin@123456`
- 资产管理员: `manager` / `Manager@123456`
- 评估专家: `evaluator` / `Evaluator@123456`
- 普通用户: `viewer` / `Viewer@123456`

### 方式二：本地开发环境

#### 后端启动

1. **安装 Python 依赖**
```bash
cd src/backend
pip install -r requirements.txt
```

2. **配置环境变量**
创建 `.env` 文件：
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/data_asset_platform
REDIS_URL=redis://:redis123@localhost:6379/0
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
```

3. **启动数据库服务**
```bash
# 使用 Docker 启动数据库服务
docker-compose up -d postgres redis minio
```

4. **初始化数据库**
```bash
cd /Users/guiping/.openclaw/workspace/data-asset-platform
python scripts/init_db.py
```

5. **启动后端服务**
```bash
cd src/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

1. **安装 Node.js 依赖**
```bash
cd src/frontend
npm install
```

2. **配置环境变量**
创建 `.env` 文件：
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

3. **启动前端开发服务器**
```bash
npm run dev
```

## 项目结构

```
data-asset-platform/
├── src/
│   ├── backend/              # 后端代码
│   │   ├── app/
│   │   │   ├── api/         # API 路由
│   │   │   ├── core/        # 核心配置
│   │   │   ├── models/      # 数据模型
│   │   │   ├── schemas/     # Pydantic 模型
│   │   │   ├── services/    # 业务逻辑
│   │   │   └── main.py      # 应用入口
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/            # 前端代码
│       ├── src/
│       │   ├── api/        # API 接口
│       │   ├── components/ # 组件
│       │   ├── router/     # 路由配置
│       │   ├── stores/     # 状态管理
│       │   ├── views/      # 页面视图
│       │   └── main.ts     # 应用入口
│       ├── package.json
│       └── Dockerfile.dev
├── scripts/
│   └── init_db.py          # 数据库初始化脚本
├── docker-compose.yml       # Docker Compose 配置
└── README.md               # 项目说明
```

## 主要功能模块

### 1. 用户认证与权限管理
- JWT 令牌认证
- 基于角色的访问控制（RBAC）
- 密码强度验证
- 登录失败锁定机制

### 2. 数据资产管理
- 资产登记与编辑
- 资产分类管理
- 资产生命周期管理
- 资产搜索与筛选

### 3. 材料文件管理
- 文件上传与下载
- 文件预览
- 版本控制
- 文件审核

### 4. 登记证书管理
- 证书导入与导出
- 证书查询
- 证书打印

### 5. 工作流引擎
- 流程定义管理
- 流程实例管理
- 待办任务处理
- 流程监控

### 6. 数据资产评估
- 评估模板管理
- 评估记录管理
- 评估报告生成

### 7. 审计日志
- 操作日志记录
- 日志查询与分析
- 日志导出

### 8. 通知中心
- 系统通知
- 任务提醒
- 消息推送

### 9. 统计分析
- 资产统计
- 趋势分析
- 数据可视化

### 10. 系统管理
- 用户管理
- 机构管理
- 数据字典
- 系统配置
- 定时任务

## API 文档

启动后端服务后，访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 常见问题

### 1. 数据库连接失败
确保 PostgreSQL 服务已启动，并检查连接配置是否正确。

### 2. Redis 连接失败
确保 Redis 服务已启动，并检查密码配置。

### 3. MinIO 连接失败
确保 MinIO 服务已启动，并检查访问密钥配置。

### 4. 前端无法连接后端
检查 CORS 配置，确保前端地址在允许列表中。

## 开发建议

1. **代码规范**
   - 后端遵循 PEP 8 规范
   - 前端使用 ESLint 和 Prettier

2. **提交规范**
   - 使用语义化提交信息
   - 格式：`<type>(<scope>): <subject>`

3. **测试**
   - 编写单元测试
   - 运行集成测试

## 生产部署

1. **修改默认密码和密钥**
2. **配置 HTTPS**
3. **设置防火墙规则**
4. **配置日志收集**
5. **设置监控告警**
6. **定期备份数据库**

## 技术支持

如有问题，请联系技术支持团队。

## 许可证

Copyright © 2024 数据资产管理平台
