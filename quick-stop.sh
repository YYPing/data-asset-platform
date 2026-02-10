#!/bin/bash

# 数据资产平台 - 快速停止脚本

echo "🛑 停止数据资产平台服务..."

# 停止后端服务
if [ -f /tmp/data-asset-backend.pid ]; then
    BACKEND_PID=$(cat /tmp/data-asset-backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "🔫 强制停止后端服务..."
            kill -9 $BACKEND_PID
        fi
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务未运行"
    fi
    rm -f /tmp/data-asset-backend.pid
else
    echo "⚠️  后端服务PID文件不存在"
fi

# 停止前端服务
if [ -f /tmp/data-asset-frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/data-asset-frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🛑 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "🔫 强制停止前端服务..."
            kill -9 $FRONTEND_PID
        fi
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务未运行"
    fi
    rm -f /tmp/data-asset-frontend.pid
else
    echo "⚠️  前端服务PID文件不存在"
fi

# 查找并停止可能遗留的进程
echo ""
echo "🔍 清理可能遗留的进程..."
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "✅ 清理uvicorn进程"
pkill -f "npm run dev" 2>/dev/null && echo "✅ 清理npm进程"

echo ""
echo "🎉 所有服务已停止"
echo "📊 服务状态:"
echo "   后端: http://localhost:8000 ❌ 已停止"
echo "   前端: http://localhost:3000 ❌ 已停止"