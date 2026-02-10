#!/bin/bash
# 数据资产平台 - 完整启动脚本
# 检查Docker → 启动服务 → 运行测试

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  数据资产平台 - 自动化启动${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# 步骤1: 检查Docker
echo -e "${YELLOW}[1/6] 检查Docker安装...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装或未添加到PATH${NC}"
    echo ""
    echo "请确保："
    echo "  1. Docker Desktop已安装到Applications"
    echo "  2. Docker Desktop已启动（菜单栏有鲸鱼图标）"
    echo "  3. 重新打开终端（让PATH生效）"
    exit 1
fi
echo -e "${GREEN}✅ Docker已安装: $(docker --version)${NC}"
echo ""

# 步骤2: 检查Docker服务
echo -e "${YELLOW}[2/6] 检查Docker服务状态...${NC}"
if ! docker info &> /dev/null 2>&1; then
    echo -e "${RED}❌ Docker服务未运行${NC}"
    echo ""
    echo "请启动Docker Desktop应用，等待菜单栏图标变为正常状态"
    echo "然后重新运行此脚本"
    exit 1
fi
echo -e "${GREEN}✅ Docker服务正在运行${NC}"
echo ""

# 步骤3: 启动基础设施
echo -e "${YELLOW}[3/6] 启动基础设施服务...${NC}"
docker-compose up -d postgres redis minio
echo ""
echo "等待服务启动..."
sleep 15
echo ""

# 步骤4: 检查服务状态
echo -e "${YELLOW}[4/6] 检查服务状态...${NC}"
docker-compose ps
echo ""

# 步骤5: 配置后端环境
echo -e "${YELLOW}[5/6] 配置后端环境...${NC}"
cd src/backend

if [ ! -f ".env" ]; then
    echo "创建.env文件..."
    cp .env.example .env
fi

if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Python虚拟环境不存在${NC}"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✅ Python环境已激活${NC}"
echo ""

# 步骤6: 运行测试
echo -e "${YELLOW}[6/6] 运行功能测试...${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

export TESTING=true
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/data_asset_platform_test"

pytest tests/ -v --tb=short --color=yes || {
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}  测试失败 - 需要修复${NC}"
    echo -e "${RED}=========================================${NC}"
    echo ""
    echo "查看上面的错误信息，我会帮您修复问题"
    exit 1
}

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  ✅ 所有测试通过！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# 显示测试覆盖率
echo "测试覆盖率报告:"
pytest tests/ --tb=no --quiet --cov=app --cov-report=term
echo ""

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  环境已就绪，可以开始开发${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo "启动开发服务器:"
echo ""
echo "  后端 (终端1):"
echo "    cd src/backend"
echo "    source venv/bin/activate"
echo "    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  前端 (终端2):"
echo "    cd src/frontend"
echo "    npm run dev"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:5173"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "  MinIO控制台: http://localhost:9001"
echo ""
