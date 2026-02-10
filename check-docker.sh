#!/bin/bash
# Docker安装验证脚本

echo "检查Docker安装状态..."
echo ""

if command -v docker &> /dev/null; then
    echo "✅ Docker已安装"
    docker --version
    echo ""
    
    if docker info &> /dev/null 2>&1; then
        echo "✅ Docker服务正在运行"
        echo ""
        echo "准备启动项目服务..."
        cd data-asset-platform
        docker-compose up -d
        echo ""
        echo "服务状态:"
        docker-compose ps
    else
        echo "⚠️  Docker已安装但未运行"
        echo "请启动Docker Desktop应用"
    fi
else
    echo "❌ Docker未安装"
    echo "请完成Docker Desktop的安装"
fi
