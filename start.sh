#!/bin/bash

# 数据资产平台 - 本地部署启动脚本
# 版本: 1.0.0
# 创建日期: 2026-02-05

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/src/backend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据资产全流程管理平台 - 本地部署     ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查Docker和Docker Compose
check_dependencies() {
    echo -e "${YELLOW}[1/5] 检查依赖...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装${NC}"
        echo "请访问 https://docs.docker.com/get-docker/ 安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}错误: Docker Compose未安装${NC}"
        echo "请访问 https://docs.docker.com/compose/install/ 安装Docker Compose"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker和Docker Compose已安装${NC}"
}

# 构建后端应用
build_backend() {
    echo -e "${YELLOW}[2/5] 构建后端应用...${NC}"
    
    cd "$BACKEND_DIR"
    
    if [ ! -f "pom.xml" ]; then
        echo -e "${RED}错误: pom.xml文件不存在${NC}"
        exit 1
    fi
    
    echo "正在编译项目..."
    mvn clean package -DskipTests
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 后端应用构建成功${NC}"
    else
        echo -e "${RED}错误: 后端应用构建失败${NC}"
        exit 1
    fi
}

# 启动Docker服务
start_services() {
    echo -e "${YELLOW}[3/5] 启动Docker服务...${NC}"
    
    cd "$PROJECT_ROOT"
    
    echo "正在启动MySQL、Redis、MinIO..."
    docker-compose up -d mysql redis minio
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    echo "检查服务状态..."
    
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✓ 基础服务启动成功${NC}"
    else
        echo -e "${RED}错误: 基础服务启动失败${NC}"
        docker-compose logs --tail=20
        exit 1
    fi
}

# 初始化MinIO存储桶
init_minio() {
    echo -e "${YELLOW}[4/5] 初始化MinIO存储桶...${NC}"
    
    # 等待MinIO完全启动
    sleep 10
    
    # 创建存储桶
    docker-compose exec minio mc mb --ignore-existing data-asset/data-asset
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ MinIO存储桶初始化成功${NC}"
    else
        echo -e "${YELLOW}⚠ MinIO存储桶初始化失败，可能已存在${NC}"
    fi
}

# 启动后端应用
start_backend() {
    echo -e "${YELLOW}[5/5] 启动后端应用...${NC}"
    
    cd "$PROJECT_ROOT"
    
    echo "正在启动后端应用..."
    docker-compose up -d backend
    
    # 等待应用启动
    echo "等待应用启动..."
    sleep 30
    
    # 检查应用状态
    if docker-compose ps | grep backend | grep -q "Up"; then
        echo -e "${GREEN}✓ 后端应用启动成功${NC}"
    else
        echo -e "${RED}错误: 后端应用启动失败${NC}"
        docker-compose logs --tail=20 backend
        exit 1
    fi
}

# 显示服务信息
show_info() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}服务访问地址:${NC}"
    echo -e "后端API: ${GREEN}http://localhost:8080/api${NC}"
    echo -e "MinIO控制台: ${GREEN}http://localhost:9001${NC}"
    echo ""
    echo -e "${YELLOW}默认账号:${NC}"
    echo -e "用户名: ${GREEN}admin${NC}"
    echo -e "密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${YELLOW}查看日志:${NC}"
    echo -e "所有服务: ${GREEN}docker-compose logs -f${NC}"
    echo -e "后端应用: ${GREEN}docker-compose logs -f backend${NC}"
    echo ""
    echo -e "${YELLOW}停止服务:${NC}"
    echo -e "${GREEN}docker-compose down${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 主函数
main() {
    check_dependencies
    build_backend
    start_services
    init_minio
    start_backend
    show_info
}

# 执行主函数
main
