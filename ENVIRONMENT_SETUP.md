# 数据资产平台 - 环境安装报告

**安装时间**: 2026-02-09 07:32  
**状态**: ✅ 部分完成（缺少Docker）

## 📋 安装清单

### ✅ 已完成

1. **Python 后端环境**
   - Python版本: 3.11.4
   - 虚拟环境: `src/backend/venv/`
   - 依赖包: 已安装所有requirements.txt中的包
   - 主要框架:
     - FastAPI 0.115.0
     - SQLAlchemy 2.0.35
     - Uvicorn 0.32.0
     - Pydantic 2.12.5
     - 测试工具: pytest, pytest-asyncio, pytest-cov
     - 代码质量: black, flake8, mypy

2. **Node.js 前端环境**
   - Node版本: v22.22.0
   - 包管理器: npm
   - 依赖包: 已安装所有package.json中的包
   - 主要框架:
     - Vue 3.5.0
     - Vue Router 4.4.0
     - Pinia 2.2.0
     - Element Plus 2.8.0
     - Vite 5.4.0
     - TypeScript 5.6.0

### ❌ 待安装

3. **Docker 基础设施**
   - 状态: 未安装
   - 需要: Docker Desktop for Mac
   - 用途: 运行PostgreSQL、Redis、MinIO等服务

## 🚀 快速启动指南

### 方案A: 使用Docker（推荐）

**1. 安装Docker Desktop**
```bash
# 下载并安装Docker Desktop for Mac
# https://www.docker.com/products/docker-desktop

# 安装后验证
docker --version
docker-compose --version
```

**2. 启动基础设施**
```bash
cd data-asset-platform
docker-compose up -d postgres redis minio

# 查看服务状态
docker-compose ps
```

**3. 启动后端**
```bash
cd src/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**4. 启动前端**
```bash
cd src/frontend
npm run dev
```

### 方案B: 本地安装（不使用Docker）

如果不想安装Docker，可以本地安装PostgreSQL、Redis、MinIO：

**1. 使用Homebrew安装**
```bash
# 安装PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 安装Redis
brew install redis
brew services start redis

# MinIO需要Docker或手动下载二进制文件
```

**2. 配置数据库**
```bash
# 创建数据库
createdb data_asset_platform

# 配置环境变量
cd src/backend
cp .env.example .env
# 编辑.env文件，修改数据库连接信息
```

**3. 启动服务**（同方案A的步骤3-4）

## 📝 环境变量配置

### 后端 (.env)
```bash
# 数据库配置
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/data_asset_platform

# Redis配置
REDIS_URL=redis://:redis123@localhost:6379/0

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123

# JWT密钥
SECRET_KEY=your-secret-key-here
```

### 前端 (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 运行测试

### 后端测试
```bash
cd src/backend
source venv/bin/activate
pytest tests/ -v
```

### 前端测试
```bash
cd src/frontend
npm run test
```

## 📊 服务端口

| 服务 | 端口 | 访问地址 |
|------|------|----------|
| 前端 | 5173 | http://localhost:5173 |
| 后端API | 8000 | http://localhost:8000 |
| API文档 | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| MinIO | 9000 | http://localhost:9000 |
| MinIO Console | 9001 | http://localhost:9001 |

## 🔧 常用命令

### Docker管理
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]
```

### 数据库迁移
```bash
cd src/backend
source venv/bin/activate

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 代码质量检查
```bash
cd src/backend
source venv/bin/activate

# 格式化代码
black app/

# 检查代码风格
flake8 app/

# 类型检查
mypy app/
```

## ⚠️ 常见问题

### 1. Docker未安装
**问题**: 执行docker命令提示"command not found"  
**解决**: 安装Docker Desktop for Mac

### 2. 端口被占用
**问题**: 启动服务时提示端口已被占用  
**解决**: 
```bash
# 查找占用端口的进程
lsof -i :8000
# 杀死进程
kill -9 <PID>
```

### 3. Python虚拟环境问题
**问题**: 找不到已安装的包  
**解决**: 确保已激活虚拟环境
```bash
source venv/bin/activate
```

### 4. 数据库连接失败
**问题**: 后端无法连接数据库  
**解决**: 
- 检查Docker服务是否运行: `docker-compose ps`
- 检查.env配置是否正确
- 检查数据库是否已创建

## 📚 下一步

1. ✅ **环境已就绪** - Python和Node.js依赖已安装
2. ⏳ **安装Docker** - 下载并安装Docker Desktop
3. ⏳ **启动服务** - 运行docker-compose启动基础设施
4. ⏳ **运行测试** - 执行功能测试确保一切正常
5. ⏳ **开始开发** - 根据需求文档进行功能开发

## 🎯 当前状态总结

- ✅ Python 3.11.4 已安装
- ✅ Node.js v22.22.0 已安装
- ✅ 后端依赖已安装（FastAPI + SQLAlchemy + 测试工具）
- ✅ 前端依赖已安装（Vue 3 + Vite + TypeScript）
- ❌ Docker未安装（需要手动安装）
- ⏳ 数据库服务未启动（等待Docker）
- ⏳ 应用服务未启动（等待Docker）

**建议**: 先安装Docker Desktop，然后按照"方案A"启动所有服务。
