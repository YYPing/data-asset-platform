#!/bin/bash

# 数据资产平台测试运行脚本

set -e

echo "🚀 开始运行数据资产平台功能测试..."
echo "========================================="

# 进入后端目录
cd src/backend

# 检查Python虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装测试依赖
echo "📦 安装测试依赖..."
pip install -q pytest pytest-asyncio pytest-cov httpx sqlalchemy aiosqlite

# 安装项目依赖
echo "📦 安装项目依赖..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
fi

# 运行测试
echo "🧪 运行测试..."
echo "========================================="

# 运行认证测试
echo "🔐 运行认证模块测试..."
pytest tests/test_auth.py -v --cov=app.core --cov-report=term-missing

echo "========================================="

# 运行资产管理测试
echo "📦 运行资产管理测试..."
if [ -f "tests/test_assets.py" ]; then
    pytest tests/test_assets.py -v --cov=app.api.v1.assets --cov-report=term-missing
else
    echo "⚠️  资产管理测试文件不存在，跳过"
fi

echo "========================================="

# 运行工作流测试
echo "🔄 运行工作流测试..."
if [ -f "tests/test_workflow.py" ]; then
    pytest tests/test_workflow.py -v --cov=app.models.workflow --cov-report=term-missing
else
    echo "⚠️  工作流测试文件不存在，跳过"
fi

echo "========================================="

# 运行所有测试并生成报告
echo "📊 运行所有测试并生成覆盖率报告..."
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

echo "========================================="
echo "📋 测试结果摘要:"
echo "-----------------------------------------"

# 显示测试结果
if [ -f ".coverage" ]; then
    echo "✅ 覆盖率报告已生成: file://$(pwd)/htmlcov/index.html"
fi

echo ""
echo "🎯 下一步:"
echo "  1. 查看详细测试报告: open htmlcov/index.html"
echo "  2. 修复失败的测试用例"
echo "  3. 运行特定模块测试: pytest tests/test_auth.py -v"
echo "  4. 运行单个测试: pytest tests/test_auth.py::TestAuth::test_login_success -v"
echo ""
echo "✅ 测试运行完成!"
echo "========================================="