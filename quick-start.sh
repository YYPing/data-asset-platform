#!/bin/bash

# 数据资产平台 - 快速启动脚本（使用SQLite内存数据库）
# 专为快速演示和查看设计

set -e

echo "🚀 数据资产平台 - 快速演示启动"
echo "================================"
echo "启动时间: $(date)"
echo "数据库: SQLite内存数据库"
echo "MinIO: 禁用（使用mock）"
echo "================================"

# 设置环境变量
export MINIO_ENABLED=false
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export REDIS_URL="memory://"
export DEBUG=true

echo ""
echo "🔧 环境配置完成"
echo "   数据库: SQLite内存模式"
echo "   文件存储: 本地mock模式"
echo "   缓存: 内存模式"

echo ""
echo "📦 启动后端服务..."

# 启动后端服务（在后台）
cd src/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "✅ 后端服务启动中 (PID: $BACKEND_PID)"
echo "   API地址: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"

# 等待后端启动
sleep 5

echo ""
echo "🎨 检查前端配置..."

cd ../frontend

if [ ! -f "package.json" ]; then
    echo "❌ 前端package.json不存在"
    echo "📦 正在安装前端依赖..."
    npm install
fi

echo ""
echo "🌐 启动前端服务..."

# 启动前端服务（在后台）
npm run dev &
FRONTEND_PID=$!

echo "✅ 前端服务启动中 (PID: $FRONTEND_PID)"
echo "   前端地址: http://localhost:3000"
echo "   管理员账号: admin / Admin@123456"

echo ""
echo "================================"
echo "🎉 启动完成！"
echo ""
echo "📋 访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "🔑 测试账号:"
echo "   管理员: admin / Admin@123456"
echo "   普通用户: user1 / User@123456"
echo ""
echo "🛠️ 功能模块:"
echo "   • 用户认证与权限管理"
echo "   • 数据资产登记管理"
echo "   • 材料上传与版本控制"
echo "   • 证书OCR识别管理"
echo "   • 工作流审批系统"
echo "   • 统计分析报表"
echo ""
echo "📞 技术支持:"
echo "   查看 PROJECT_VERIFICATION.md 获取详细验证信息"
echo "================================"

# 保存进程ID
echo $BACKEND_PID > /tmp/data-asset-backend.pid
echo $FRONTEND_PID > /tmp/data-asset-frontend.pid

echo ""
echo "💡 提示:"
echo "   停止服务: ./quick-stop.sh"
echo "   查看日志: tail -f src/backend/uvicorn.log"

# 等待用户操作
wait