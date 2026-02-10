#!/bin/bash

# 数据资产平台 - 本地开发环境启动脚本
# 不使用Docker，使用本地安装的服务

set -e

echo "🚀 启动数据资产平台本地开发环境..."

# 检查必要服务
echo "🔍 检查必要服务..."

# 检查PostgreSQL
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo "❌ PostgreSQL未运行，请先启动PostgreSQL"
    echo "    brew services start postgresql@15"
    exit 1
fi
echo "✅ PostgreSQL已运行"

# 检查Redis
if ! redis-cli ping >/dev/null 2>&1; then
    echo "❌ Redis未运行，请先启动Redis"
    echo "    brew services start redis"
    exit 1
fi
echo "✅ Redis已运行"

# 检查数据库是否存在
echo "📊 检查数据库..."
if ! psql -h localhost -U postgres -lqt | cut -d \| -f 1 | grep -qw data_asset_platform; then
    echo "📦 创建数据库..."
    createdb -h localhost -U postgres data_asset_platform
    echo "✅ 数据库创建完成"
    
    echo "📋 初始化数据库结构..."
    psql -h localhost -U postgres -d data_asset_platform -f scripts/init_database.sql
    echo "✅ 数据库初始化完成"
else
    echo "✅ 数据库已存在"
fi

# 设置环境变量
export DATABASE_URL="postgresql+asyncpg://postgres:postgres123@localhost:5432/data_asset_platform"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key-change-in-production-min-32-chars"
export DEBUG="true"

# 启动后端
echo "🚀 启动后端服务..."
cd src/backend
source venv/bin/activate

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "❌ 找不到requirements.txt"
    exit 1
fi

echo "📦 安装Python依赖..."
pip install -r requirements.txt >/dev/null 2>&1 || echo "依赖可能已安装"

echo "🔧 运行数据库迁移..."
alembic upgrade head >/dev/null 2>&1 || echo "迁移可能已应用"

echo "🌐 启动FastAPI服务..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ 后端启动完成 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端服务..."
cd ../frontend

echo "📦 安装Node.js依赖..."
npm install >/dev/null 2>&1 || echo "依赖可能已安装"

echo "🎨 启动Vite开发服务器..."
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端启动完成 (PID: $FRONTEND_PID)"

# 显示访问信息
echo ""
echo "========================================="
echo "🎉 数据资产平台启动完成！"
echo "========================================="
echo ""
echo "🌐 访问地址:"
echo "   前端: http://localhost:5173"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "🔑 默认登录账号:"
echo "   管理员: admin / admin123"
echo "   登记中心审核员: center_auditor / admin123"
echo "   评估专家: evaluator / admin123"
echo "   数据持有方: data_holder / admin123"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "========================================="

# 等待用户中断
trap "echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait