#!/bin/bash

# 数据资产平台 - API测试脚本
# 版本: 1.0.0
# 创建日期: 2026-02-05

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API基础URL
BASE_URL="http://localhost:8080/api"

# 全局变量
TOKEN=""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据资产平台 - API测试脚本           ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查服务是否运行
check_service() {
    echo -e "${YELLOW}[1/6] 检查服务状态...${NC}"
    
    if ! curl -s "$BASE_URL/auth/login" > /dev/null 2>&1; then
        echo -e "${RED}错误: 后端服务未运行${NC}"
        echo "请先运行 ./start.sh 启动服务"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 后端服务运行正常${NC}"
}

# 用户登录
login() {
    echo -e "${YELLOW}[2/6] 用户登录...${NC}"
    
    local response=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
            "username": "admin",
            "password": "admin123"
        }')
    
    if echo "$response" | grep -q '"code":200'; then
        TOKEN=$(echo "$response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✓ 登录成功${NC}"
        echo -e "Token: ${TOKEN:0:20}..."
    else
        echo -e "${RED}错误: 登录失败${NC}"
        echo "响应: $response"
        exit 1
    fi
}

# 测试客户管理API
test_customer_api() {
    echo -e "${YELLOW}[3/6] 测试客户管理API...${NC}"
    
    # 生成客户编码
    echo "1. 生成客户编码..."
    local code_response=$(curl -s -X GET "$BASE_URL/customers/generate-code" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$code_response" | grep -q '"code":200'; then
        local customer_code=$(echo "$code_response" | grep -o '"data":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✓ 生成客户编码成功: $customer_code${NC}"
    else
        echo -e "${RED}错误: 生成客户编码失败${NC}"
        return 1
    fi
    
    # 创建客户
    echo "2. 创建客户..."
    local create_response=$(curl -s -X POST "$BASE_URL/customers" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"companyName\": \"测试科技有限公司\",
            \"industry\": \"信息技术\",
            \"companyScale\": \"medium\",
            \"contactName\": \"张三\",
            \"contactPhone\": \"13800138000\",
            \"contactEmail\": \"zhangsan@test.com\",
            \"registeredAddress\": \"北京市海淀区测试路1号\",
            \"officeAddress\": \"北京市朝阳区测试路2号\"
        }")
    
    if echo "$create_response" | grep -q '"code":200'; then
        local customer_id=$(echo "$create_response" | grep -o '"id":[0-9]*' | cut -d':' -f2)
        echo -e "${GREEN}✓ 创建客户成功: ID=$customer_id${NC}"
    else
        echo -e "${RED}错误: 创建客户失败${NC}"
        echo "响应: $create_response"
        return 1
    fi
    
    # 查询客户列表
    echo "3. 查询客户列表..."
    local list_response=$(curl -s -X GET "$BASE_URL/customers?pageNum=1&pageSize=10" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$list_response" | grep -q '"code":200'; then
        echo -e "${GREEN}✓ 查询客户列表成功${NC}"
    else
        echo -e "${RED}错误: 查询客户列表失败${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ 客户管理API测试完成${NC}"
}

# 测试项目管理API
test_project_api() {
    echo -e "${YELLOW}[4/6] 测试项目管理API...${NC}"
    
    # 先查询一个客户ID
    echo "1. 查询客户ID..."
    local list_response=$(curl -s -X GET "$BASE_URL/customers?pageNum=1&pageSize=1" \
        -H "Authorization: Bearer $TOKEN")
    
    local customer_id=$(echo "$list_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    
    if [ -z "$customer_id" ]; then
        echo -e "${YELLOW}⚠ 没有找到客户，跳过项目管理测试${NC}"
        return 0
    fi
    
    echo -e "使用客户ID: $customer_id"
    
    # 生成项目编码
    echo "2. 生成项目编码..."
    local code_response=$(curl -s -X GET "$BASE_URL/projects/generate-code" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$code_response" | grep -q '"code":200'; then
        local project_code=$(echo "$code_response" | grep -o '"data":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✓ 生成项目编码成功: $project_code${NC}"
    else
        echo -e "${RED}错误: 生成项目编码失败${NC}"
        return 1
    fi
    
    # 创建项目
    echo "3. 创建项目..."
    local create_response=$(curl -s -X POST "$BASE_URL/projects" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"customerId\": $customer_id,
            \"projectName\": \"数据资产价值评估项目\",
            \"projectType\": \"consulting\",
            \"description\": \"为客户提供数据资产价值评估服务\",
            \"contractAmount\": 500000,
            \"startDate\": \"2026-02-01\",
            \"endDate\": \"2026-06-30\"
        }")
    
    if echo "$create_response" | grep -q '"code":200'; then
        local project_id=$(echo "$create_response" | grep -o '"id":[0-9]*' | cut -d':' -f2)
        echo -e "${GREEN}✓ 创建项目成功: ID=$project_id${NC}"
    else
        echo -e "${RED}错误: 创建项目失败${NC}"
        echo "响应: $create_response"
        return 1
    fi
    
    echo -e "${GREEN}✓ 项目管理API测试完成${NC}"
}

# 测试认证API
test_auth_api() {
    echo -e "${YELLOW}[5/6] 测试认证API...${NC}"
    
    # 获取当前用户信息
    echo "1. 获取当前用户信息..."
    local me_response=$(curl -s -X GET "$BASE_URL/auth/me" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$me_response" | grep -q '"code":200'; then
        local username=$(echo "$me_response" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✓ 获取用户信息成功: $username${NC}"
    else
        echo -e "${RED}错误: 获取用户信息失败${NC}"
        return 1
    fi
    
    # 刷新token
    echo "2. 刷新token..."
    local refresh_response=$(curl -s -X POST "$BASE_URL/auth/refresh" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$refresh_response" | grep -q '"code":200'; then
        local new_token=$(echo "$refresh_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
        TOKEN="$new_token"
        echo -e "${GREEN}✓ 刷新token成功${NC}"
        echo -e "新Token: ${TOKEN:0:20}..."
    else
        echo -e "${RED}错误: 刷新token失败${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ 认证API测试完成${NC}"
}

# 显示测试总结
show_summary() {
    echo -e "${YELLOW}[6/6] 测试总结...${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 所有API测试完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}测试结果:${NC}"
    echo -e "✓ 服务状态检查"
    echo -e "✓ 用户登录认证"
    echo -e "✓ 客户管理API"
    echo -e "✓ 项目管理API"
    echo -e "✓ 认证API"
    echo ""
    echo -e "${YELLOW}当前Token:${NC}"
    echo -e "${TOKEN:0:50}..."
    echo ""
    echo -e "${YELLOW}API文档:${NC}"
    echo -e "Swagger UI: ${GREEN}http://localhost:8080/swagger-ui.html${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 主函数
main() {
    check_service
    login
    test_customer_api
    test_project_api
    test_auth_api
    show_summary
}

# 执行主函数
main
