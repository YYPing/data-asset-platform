#!/bin/bash

# 数据资产平台 - Node.js版本启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据资产平台 - Node.js版本           ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查Node.js
check_node() {
    echo -e "${YELLOW}[1/4] 检查Node.js环境...${NC}"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: Node.js未安装${NC}"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js已安装: $NODE_VERSION${NC}"
}

# 检查npm
check_npm() {
    echo -e "${YELLOW}[2/4] 检查npm...${NC}"
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}错误: npm未安装${NC}"
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ npm已安装: $NPM_VERSION${NC}"
}

# 安装依赖
install_deps() {
    echo -e "${YELLOW}[3/4] 安装依赖包...${NC}"
    
    if [ ! -f "package.json" ]; then
        echo -e "${RED}错误: package.json文件不存在${NC}"
        exit 1
    fi
    
    echo "正在安装依赖..."
    npm install
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 依赖安装完成${NC}"
    else
        echo -e "${RED}错误: 依赖安装失败${NC}"
        exit 1
    fi
}

# 启动服务
start_service() {
    echo -e "${YELLOW}[4/4] 启动API服务...${NC}"
    
    echo "正在启动服务..."
    npm start &
    SERVER_PID=$!
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 5
    
    # 检查服务是否运行
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API服务启动成功${NC}"
        echo -e "${GREEN}服务PID: $SERVER_PID${NC}"
        
        # 保存PID
        echo $SERVER_PID > /tmp/data-asset-node.pid
    else
        echo -e "${RED}错误: 服务启动失败${NC}"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
}

# 显示信息
show_info() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 数据资产平台启动完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}服务访问地址:${NC}"
    echo -e "API服务: ${GREEN}http://localhost:3000${NC}"
    echo -e "健康检查: ${GREEN}http://localhost:3000/api/health${NC}"
    echo ""
    echo -e "${YELLOW}可用API端点:${NC}"
    echo -e "  GET  /api/health              - 健康检查"
    echo -e "  POST /api/auth/login         - 用户登录"
    echo -e "  GET  /api/auth/me            - 当前用户"
    echo -e "  GET  /api/customers          - 客户列表"
    echo -e "  POST /api/customers          - 创建客户"
    echo -e "  GET  /api/projects           - 项目列表"
    echo -e "  POST /api/projects           - 创建项目"
    echo -e "  POST /api/systems            - 系统登记"
    echo -e "  POST /api/assessments        - 价值评估"
    echo ""
    echo -e "${YELLOW}默认账号:${NC}"
    echo -e "用户名: ${GREEN}admin${NC}"
    echo -e "密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${YELLOW}测试API:${NC}"
    echo -e "运行测试: ${GREEN}node test-api.js${NC}"
    echo -e "或: ${GREEN}npm test${NC}"
    echo ""
    echo -e "${YELLOW}管理命令:${NC}"
    echo -e "停止服务: ${GREEN}kill \$(cat /tmp/data-asset-node.pid)${NC}"
    echo -e "查看日志: ${GREEN}tail -f npm-debug.log${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 清理函数
cleanup() {
    if [ -f /tmp/data-asset-node.pid ]; then
        PID=$(cat /tmp/data-asset-node.pid)
        kill $PID 2>/dev/null && echo -e "${GREEN}服务已停止${NC}" || true
        rm -f /tmp/data-asset-node.pid
    fi
}

# 捕获退出信号
trap cleanup EXIT INT TERM

# 主函数
main() {
    check_node
    check_npm
    install_deps
    start_service
    show_info
    
    # 等待用户输入
    echo -e "${YELLOW}按Ctrl+C停止服务...${NC}"
    wait $SERVER_PID
}

# 执行主函数
main
