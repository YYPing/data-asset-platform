#!/bin/bash
set -e

echo "=== 数据资产管理平台 - 环境启动 ==="

# 启动数据库
docker compose up -d db
echo "等待数据库就绪..."
sleep 3

# 安装后端依赖并启动
cd backend
pip3 install -r requirements.txt -q
python3 -m alembic upgrade head 2>/dev/null || true
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 安装前端依赖并启动
cd frontend
npm install -q 2>/dev/null || true
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== 服务已启动 ==="
echo "后端: http://localhost:8000"
echo "前端: http://localhost:5173"
echo "API文档: http://localhost:8000/docs"
