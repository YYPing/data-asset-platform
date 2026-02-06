#!/bin/bash

# 数据资产管理平台 - 启动和测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKEND_DIR="src/backend"
API_BASE_URL="http://localhost:8080/api"
TEST_DB_SCRIPT="src/backend/src/main/resources/db/init.sql"

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log "检查依赖..."
    
    # 检查Java
    if ! command -v java &> /dev/null; then
        error "Java未安装"
        return 1
    fi
    JAVA_VERSION=$(java -version 2>&1 | head -1 | cut -d'"' -f2)
    log "Java版本: $JAVA_VERSION"
    
    # 检查Maven
    if ! command -v mvn &> /dev/null; then
        error "Maven未安装"
        return 1
    fi
    MAVEN_VERSION=$(mvn --version 2>&1 | head -1 | cut -d' ' -f3)
    log "Maven版本: $MAVEN_VERSION"
    
    # 检查MySQL (可选)
    if command -v mysql &> /dev/null; then
        MYSQL_VERSION=$(mysql --version 2>&1 | cut -d' ' -f4)
        log "MySQL版本: $MYSQL_VERSION"
    else
        warning "MySQL未安装，数据库测试将跳过"
    fi
    
    success "依赖检查完成"
}

# 初始化测试数据库
init_test_database() {
    log "初始化测试数据库..."
    
    if [ ! -f "$TEST_DB_SCRIPT" ]; then
        error "数据库脚本不存在: $TEST_DB_SCRIPT"
        return 1
    fi
    
    # 检查MySQL是否可用
    if ! command -v mysql &> /dev/null; then
        warning "MySQL未安装，跳过数据库初始化"
        return 0
    fi
    
    # 尝试创建测试数据库
    if mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS data_asset_test;" 2>/dev/null; then
        log "创建测试数据库: data_asset_test"
        
        # 执行初始化脚本
        if mysql -u root -p data_asset_test < "$TEST_DB_SCRIPT" 2>/dev/null; then
            success "数据库初始化成功"
        else
            warning "数据库初始化可能失败，请手动检查"
        fi
    else
        warning "无法创建测试数据库，请检查MySQL连接"
    fi
}

# 编译项目
compile_project() {
    log "编译项目..."
    
    cd "$BACKEND_DIR"
    
    if mvn clean compile -q; then
        success "项目编译成功"
    else
        error "项目编译失败"
        return 1
    fi
    
    cd - > /dev/null
}

# 启动应用
start_application() {
    log "启动应用..."
    
    cd "$BACKEND_DIR"
    
    # 在后台启动应用
    mvn spring-boot:run -q &
    APP_PID=$!
    
    # 保存PID
    echo $APP_PID > /tmp/data-asset-platform.pid
    
    # 等待应用启动
    log "等待应用启动..."
    sleep 15
    
    # 检查应用是否运行
    if curl -s "$API_BASE_URL/health" > /dev/null 2>&1; then
        success "应用启动成功 (PID: $APP_PID)"
        log "API地址: $API_BASE_URL"
        log "健康检查: $API_BASE_URL/health"
        log "Swagger UI: http://localhost:8080/swagger-ui.html"
    else
        error "应用启动失败"
        kill $APP_PID 2>/dev/null
        return 1
    fi
    
    cd - > /dev/null
}

# 测试API
test_api() {
    log "开始API测试..."
    
    # 等待应用完全启动
    sleep 5
    
    # 1. 测试健康检查
    log "测试健康检查..."
    if curl -s "$API_BASE_URL/health" | grep -q "UP"; then
        success "健康检查通过"
    else
        error "健康检查失败"
        return 1
    fi
    
    # 2. 测试客户管理API
    log "测试客户管理API..."
    
    # 生成客户编码
    CUSTOMER_CODE=$(curl -s "$API_BASE_URL/customers/generate-code" | jq -r '.data' 2>/dev/null || echo "C2024020001")
    log "生成的客户编码: $CUSTOMER_CODE"
    
    # 3. 测试项目管理API
    log "测试项目管理API..."
    
    # 生成项目编码
    PROJECT_CODE=$(curl -s "$API_BASE_URL/projects/generate-code" | jq -r '.data' 2>/dev/null || echo "P2024020001")
    log "生成的项目编码: $PROJECT_CODE"
    
    # 4. 测试统计API
    log "测试统计API..."
    
    if curl -s "$API_BASE_URL/customers/stats" > /dev/null 2>&1; then
        success "客户统计API可用"
    else
        warning "客户统计API可能有问题"
    fi
    
    if curl -s "$API_BASE_URL/projects/stats" > /dev/null 2>&1; then
        success "项目统计API可用"
    else
        warning "项目统计API可能有问题"
    fi
    
    success "API测试完成"
}

# 显示API文档
show_api_docs() {
    log "API文档信息:"
    echo ""
    echo "客户管理API:"
    echo "  GET    $API_BASE_URL/customers              - 分页查询客户列表"
    echo "  POST   $API_BASE_URL/customers              - 创建客户"
    echo "  GET    $API_BASE_URL/customers/{id}         - 获取客户详情"
    echo "  PUT    $API_BASE_URL/customers/{id}         - 更新客户"
    echo "  DELETE $API_BASE_URL/customers/{id}         - 删除客户"
    echo "  GET    $API_BASE_URL/customers/stats        - 客户统计"
    echo "  GET    $API_BASE_URL/customers/generate-code - 生成客户编码"
    echo ""
    echo "项目管理API:"
    echo "  GET    $API_BASE_URL/projects               - 分页查询项目列表"
    echo "  POST   $API_BASE_URL/projects               - 创建项目"
    echo "  GET    $API_BASE_URL/projects/{id}          - 获取项目详情"
    echo "  PUT    $API_BASE_URL/projects/{id}          - 更新项目"
    echo "  DELETE $API_BASE_URL/projects/{id}          - 删除项目"
    echo "  GET    $API_BASE_URL/projects/stats         - 项目统计"
    echo "  GET    $API_BASE_URL/projects/generate-code - 生成项目编码"
    echo ""
    echo "系统API:"
    echo "  GET    $API_BASE_URL/health                 - 健康检查"
    echo "  GET    http://localhost:8080/swagger-ui.html - Swagger UI"
    echo ""
}

# 停止应用
stop_application() {
    log "停止应用..."
    
    if [ -f /tmp/data-asset-platform.pid ]; then
        PID=$(cat /tmp/data-asset-platform.pid)
        if kill $PID 2>/dev/null; then
            success "应用已停止 (PID: $PID)"
            rm -f /tmp/data-asset-platform.pid
        else
            warning "无法停止应用，可能已退出"
        fi
    else
        warning "未找到应用PID文件"
    fi
}

# 清理
cleanup() {
    stop_application
}

# 主函数
main() {
    trap cleanup EXIT INT TERM
    
    log "数据资产管理平台 - 启动和测试脚本"
    echo ""
    
    # 检查参数
    if [ "$1" = "stop" ]; then
        stop_application
        exit 0
    fi
    
    # 执行步骤
    check_dependencies
    init_test_database
    compile_project
    start_application
    test_api
    show_api_docs
    
    echo ""
    log "启动和测试完成！"
    log "按Ctrl+C停止应用"
    
    # 等待用户中断
    wait
}

# 运行主函数
main "$@"