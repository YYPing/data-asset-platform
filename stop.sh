#!/bin/bash

# 数据资产管理平台 - 停止脚本

set -e

echo "=========================================="
echo "数据资产管理平台 - 停止脚本"
echo "=========================================="
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 停止服务
echo "🛑 停止服务..."
docker-compose down

echo ""
echo "✅ 服务已停止"
echo ""
echo "💡 提示："
echo "   - 重新启动: ./start.sh"
echo "   - 删除数据: docker-compose down -v"
echo ""
