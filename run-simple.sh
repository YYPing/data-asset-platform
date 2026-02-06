#!/bin/bash

# 数据资产平台 - 纯Node.js版本启动脚本
# 无需任何依赖，立即运行

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据资产平台 - 纯Node.js版本         ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查Node.js
check_node() {
    echo -e "${YELLOW}[1/3] 检查Node.js环境...${NC}"
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: Node.js未安装${NC}"
        echo "请从 https://nodejs.org/ 下载安装Node.js"
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js已安装: $NODE_VERSION${NC}"
}

# 启动服务
start_service() {
    echo -e "${YELLOW}[2/3] 启动API服务...${NC}"
    
    echo "正在启动服务..."
    node simple-server.js &
    SERVER_PID=$!
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 3
    
    # 检查服务是否运行
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API服务启动成功${NC}"
        echo -e "${GREEN}服务PID: $SERVER_PID${NC}"
        
        # 保存PID
        echo $SERVER_PID > /tmp/data-asset-simple.pid
    else
        echo -e "${RED}错误: 服务启动失败${NC}"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
}

# 显示信息
show_info() {
    echo -e "${YELLOW}[3/3] 显示服务信息...${NC}"
    
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
    echo -e "  GET  /api/customers/generate-code - 生成客户编码"
    echo -e "  GET  /api/projects/generate-code  - 生成项目编码"
    echo ""
    echo -e "${YELLOW}默认账号:${NC}"
    echo -e "用户名: ${GREEN}admin${NC}"
    echo -e "密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${YELLOW}测试命令:${NC}"
    echo -e "运行测试: ${GREEN}node simple-test.js${NC}"
    echo -e "或手动测试: ${GREEN}curl http://localhost:3000/api/health${NC}"
    echo ""
    echo -e "${YELLOW}管理命令:${NC}"
    echo -e "停止服务: ${GREEN}kill \$(cat /tmp/data-asset-simple.pid)${NC}"
    echo -e "重新启动: ${GREEN}./run-simple.sh${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 清理函数
cleanup() {
    if [ -f /tmp/data-asset-simple.pid ]; then
        PID=$(cat /tmp/data-asset-simple.pid)
        kill $PID 2>/dev/null && echo -e "\n${GREEN}服务已停止${NC}" || true
        rm -f /tmp/data-asset-simple.pid
    fi
}

# 捕获退出信号
trap cleanup EXIT INT TERM

# 主函数
main() {
    check_node
    start_service
    show_info
    
    # 等待用户输入
    echo -e "${YELLOW}按Ctrl+C停止服务...${NC}"
    wait $SERVER_PID
}

# 执行主函数
main
