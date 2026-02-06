#!/bin/bash

# 数据资产平台 - 简化部署脚本
# 使用Docker构建和运行

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据资产平台 - 简化部署              ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查Docker
check_docker() {
    echo -e "${YELLOW}[1/4] 检查Docker...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Docker已安装${NC}"
}

# 清理旧容器
cleanup() {
    echo -e "${YELLOW}[2/4] 清理旧容器...${NC}"
    
    docker-compose down --remove-orphans 2>/dev/null || true
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 启动基础设施
start_infrastructure() {
    echo -e "${YELLOW}[3/4] 启动基础设施...${NC}"
    
    echo "启动MySQL、Redis、MinIO..."
    docker-compose up -d mysql redis minio
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 30
    
    # 初始化数据库
    echo "初始化数据库..."
    docker-compose exec -T mysql mysql -uroot -proot123456 data_asset < src/backend/src/main/resources/db/init.sql 2>/dev/null || true
    
    # 初始化MinIO
    echo "初始化MinIO..."
    sleep 10
    docker-compose exec minio mc mb --ignore-existing data-asset/data-asset 2>/dev/null || true
    
    echo -e "${GREEN}✓ 基础设施启动完成${NC}"
}

# 构建并启动后端
start_backend() {
    echo -e "${YELLOW}[4/4] 构建并启动后端...${NC}"
    
    echo "构建Docker镜像..."
    docker-compose build backend
    
    echo "启动后端应用..."
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

# 显示信息
show_info() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 部署完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}服务访问地址:${NC}"
    echo -e "后端API: ${GREEN}http://localhost:8080/api${NC}"
    echo -e "健康检查: ${GREEN}http://localhost:8080/api/actuator/health${NC}"
    echo -e "MinIO控制台: ${GREEN}http://localhost:9001${NC}"
    echo ""
    echo -e "${YELLOW}默认账号:${NC}"
    echo -e "用户名: ${GREEN}admin${NC}"
    echo -e "密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${YELLOW}管理命令:${NC}"
    echo -e "查看日志: ${GREEN}docker-compose logs -f${NC}"
    echo -e "停止服务: ${GREEN}docker-compose down${NC}"
    echo -e "重启服务: ${GREEN}docker-compose restart${NC}"
    echo ""
    echo -e "${YELLOW}测试API:${NC}"
    echo -e "运行测试: ${GREEN}./test-api.sh${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 主函数
main() {
    check_docker
    cleanup
    start_infrastructure
    start_backend
    show_info
}

# 执行主函数
main
