#!/bin/bash

# 数据资产管理平台 - 启动脚本

set -e

echo "=========================================="
echo "数据资产管理平台 - 启动脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: Docker Compose 未安装"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

echo ""
echo "⏳ 等待服务启动完成..."
sleep 15

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
docker-compose ps

# 初始化数据库
echo ""
echo "🗄️  初始化数据库..."
docker-compose exec -T backend python /app/../scripts/init_db.py

echo ""
echo "=========================================="
echo "✅ 启动完成！"
echo "=========================================="
echo ""
echo "📝 访问地址："
echo "   前端:        http://localhost:3000"
echo "   后端 API:    http://localhost:8000"
echo "   API 文档:    http://localhost:8000/api/docs"
echo "   MinIO 控制台: http://localhost:9001"
echo ""
echo "🔑 默认登录账号："
echo "   管理员:      admin / Admin@123456"
echo "   资产管理员:  manager / Manager@123456"
echo "   评估专家:    evaluator / Evaluator@123456"
echo "   普通用户:    viewer / Viewer@123456"
echo ""
echo "📖 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"
echo ""
