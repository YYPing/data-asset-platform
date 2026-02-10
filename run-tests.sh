#!/bin/bash
# 数据资产平台 - 测试运行脚本
# 用途: 运行所有功能测试，如果测试不通过则修改代码直到通过

set -e

echo "========================================="
echo "  数据资产平台 - 功能测试"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 步骤1: 检查Docker服务
echo "步骤1: 检查Docker服务状态..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker未运行${NC}"
    echo "请先安装并启动Docker Desktop"
    echo "下载地址: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo -e "${GREEN}✅ Docker已运行${NC}"
echo ""

# 步骤2: 启动基础设施
echo "步骤2: 启动基础设施服务..."
docker-compose up -d postgres redis minio
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态:"
docker-compose ps
echo ""

# 步骤3: 检查Python虚拟环境
echo "步骤3: 检查Python环境..."
cd src/backend

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi
echo -e "${GREEN}✅ Python环境已就绪${NC}"
echo ""

# 步骤4: 配置环境变量
echo "步骤4: 配置环境变量..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在，从模板创建...${NC}"
    cp .env.example .env
fi
echo -e "${GREEN}✅ 环境变量已配置${NC}"
echo ""

# 步骤5: 运行数据库迁移
echo "步骤5: 运行数据库迁移..."
if command -v alembic &> /dev/null; then
    echo "执行数据库迁移..."
    alembic upgrade head || echo -e "${YELLOW}⚠️  迁移失败或无需迁移${NC}"
else
    echo -e "${YELLOW}⚠️  Alembic未安装，跳过迁移${NC}"
fi
echo ""

# 步骤6: 运行测试
echo "步骤6: 运行功能测试..."
echo "========================================="
echo ""

# 设置测试环境变量
export TESTING=true
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/data_asset_platform_test"

# 运行测试并保存结果
TEST_RESULT=0
pytest tests/ -v --tb=short --color=yes --cov=app --cov-report=term-missing || TEST_RESULT=$?

echo ""
echo "========================================="

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    echo ""
    echo "测试报告:"
    pytest tests/ --tb=no --quiet --cov=app --cov-report=term
    echo ""
    echo "下一步:"
    echo "  1. 启动后端: cd src/backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "  2. 启动前端: cd src/frontend && npm run dev"
    echo "  3. 访问应用: http://localhost:5173"
else
    echo -e "${RED}❌ 测试失败！${NC}"
    echo ""
    echo "失败的测试需要修复。请查看上面的错误信息。"
    echo ""
    echo "常见问题排查:"
    echo "  1. 数据库连接: docker-compose ps 检查服务状态"
    echo "  2. 环境变量: 检查 .env 文件配置"
    echo "  3. 依赖包: pip install -r requirements.txt"
    echo "  4. 数据库迁移: alembic upgrade head"
    echo ""
    echo "修复后重新运行: ./run-tests.sh"
    exit 1
fi

echo ""
echo "========================================="
echo "  测试完成"
echo "========================================="
