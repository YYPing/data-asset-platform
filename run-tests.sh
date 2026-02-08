#!/bin/bash
# 测试运行脚本

echo "=========================================="
echo "数据资产管理平台 - 功能测试"
echo "=========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"
echo ""

# 进入后端目录
cd "$(dirname "$0")/src/backend" || exit 1

# 检查是否有虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装测试依赖..."
pip install -q pytest pytest-asyncio pytest-cov httpx

# 安装项目依赖（仅测试需要的）
echo "📦 安装项目依赖..."
pip install -q fastapi sqlalchemy pydantic python-jose passlib bcrypt

# 运行测试
echo ""
echo "=========================================="
echo "开始运行测试..."
echo "=========================================="
echo ""

python3 -m pytest tests/ -v --tb=short --color=yes

# 保存测试结果
TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ 所有测试通过！"
else
    echo "❌ 部分测试失败，退出码: $TEST_EXIT_CODE"
fi
echo "=========================================="

exit $TEST_EXIT_CODE
