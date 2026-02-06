# 数据资产平台 - 本地开发运行脚本
# 使用内嵌H2数据库，无需Docker

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据资产平台 - 本地开发模式          ${NC}"
echo -e "${BLUE}========================================${NC}"

# 检查Java
check_java() {
    echo -e "${YELLOW}[1/4] 检查Java环境...${NC}"
    
    if ! command -v java &> /dev/null; then
        echo -e "${RED}错误: Java未安装${NC}"
        echo "请安装Java 17或更高版本"
        exit 1
    fi
    
    JAVA_VERSION=$(java -version 2>&1 | head -1 | cut -d'"' -f2)
    echo -e "${GREEN}✓ Java已安装: $JAVA_VERSION${NC}"
}

# 检查Maven
check_maven() {
    echo -e "${YELLOW}[2/4] 检查Maven...${NC}"
    
    if ! command -v mvn &> /dev/null; then
        echo -e "${YELLOW}⚠ Maven未安装，正在安装...${NC}"
        brew install maven 2>/dev/null || {
            echo -e "${RED}错误: Maven安装失败${NC}"
            exit 1
        }
    fi
    
    MAVEN_VERSION=$(mvn -v 2>&1 | head -1 | cut -d' ' -f3)
    echo -e "${GREEN}✓ Maven已安装: $MAVEN_VERSION${NC}"
}

# 创建开发配置文件
create_dev_config() {
    echo -e "${YELLOW}[3/4] 创建开发配置...${NC}"
    
    cat > /tmp/application-dev.yml << 'EOF'
spring:
  config:
    activate:
      on-profile: dev

  # 使用H2内嵌数据库
  datasource:
    driver-class-name: org.h2.Driver
    url: jdbc:h2:mem:data_asset;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE;MODE=MySQL
    username: sa
    password: 
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20

  # H2控制台
  h2:
    console:
      enabled: true
      path: /h2-console

  # 使用内存Redis
  redis:
    host: localhost
    port: 6379
    lettuce:
      pool:
        max-active: 8
        max-idle: 8

  # 禁用MinIO（开发模式）
  autoconfigure:
    exclude: io.minio.MinioAutoConfiguration

# 禁用文件上传限制
  servlet:
    multipart:
      max-file-size: 500MB
      max-request-size: 500MB

# 开发模式配置
app:
  file:
    upload-path: ./uploads
    temp-path: ./temp
  report:
    template-path: ./templates
    output-path: ./reports

# 日志配置
logging:
  level:
    com.company.dataasset: DEBUG
    org.springframework.security: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{50} - %msg%n"

# 禁用安全（开发模式）
jwt:
  secret: dev-secret-key-1234567890abcdefghijklmnopqrstuv
  expiration: 86400000
EOF

    echo -e "${GREEN}✓ 开发配置创建完成${NC}"
}

# 编译和运行
run_application() {
    echo -e "${YELLOW}[4/4] 编译并运行应用...${NC}"
    
    cd /Users/guiping/.openclaw/workspace/data-asset-platform/src/backend
    
    echo "编译项目..."
    mvn clean compile -q
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 编译成功${NC}"
    else
        echo -e "${RED}错误: 编译失败${NC}"
        exit 1
    fi
    
    echo "启动应用..."
    echo -e "${YELLOW}应用正在启动，请稍候...${NC}"
    
    # 在后台运行应用
    mvn spring-boot:run -Dspring-boot.run.profiles=dev -q &
    APP_PID=$!
    
    # 等待应用启动
    sleep 30
    
    # 检查应用是否运行
    if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 应用启动成功${NC}"
    else
        echo -e "${RED}错误: 应用启动失败${NC}"
        kill $APP_PID 2>/dev/null
        exit 1
    fi
    
    # 保存PID
    echo $APP_PID > /tmp/data-asset-app.pid
    echo -e "${GREEN}应用PID: $APP_PID${NC}"
}

# 显示信息
show_info() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}🎉 本地开发环境启动完成！${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}服务访问地址:${NC}"
    echo -e "后端API: ${GREEN}http://localhost:8080/api${NC}"
    echo -e "健康检查: ${GREEN}http://localhost:8080/api/health${NC}"
    echo -e "H2控制台: ${GREEN}http://localhost:8080/h2-console${NC}"
    echo -e "Swagger UI: ${GREEN}http://localhost:8080/swagger-ui.html${NC}"
    echo ""
    echo -e "${YELLOW}H2数据库连接信息:${NC}"
    echo -e "JDBC URL: ${GREEN}jdbc:h2:mem:data_asset${NC}"
    echo -e "用户名: ${GREEN}sa${NC}"
    echo -e "密码: ${GREEN}(空)${NC}"
    echo ""
    echo -e "${YELLOW}默认账号:${NC}"
    echo -e "用户名: ${GREEN}admin${NC}"
    echo -e "密码: ${GREEN}admin123${NC}"
    echo ""
    echo -e "${YELLOW}管理命令:${NC}"
    echo -e "停止应用: ${GREEN}kill \$(cat /tmp/data-asset-app.pid)${NC}"
    echo -e "查看日志: ${GREEN}tail -f target/logs/application.log${NC}"
    echo ""
    echo -e "${YELLOW}测试API:${NC}"
    echo -e "运行测试: ${GREEN}curl http://localhost:8080/api/health${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# 清理函数
cleanup() {
    if [ -f /tmp/data-asset-app.pid ]; then
        PID=$(cat /tmp/data-asset-app.pid)
        kill $PID 2>/dev/null && echo -e "${GREEN}应用已停止${NC}" || true
        rm -f /tmp/data-asset-app.pid
    fi
}

# 捕获退出信号
trap cleanup EXIT INT TERM

# 主函数
main() {
    check_java
    check_maven
    create_dev_config
    run_application
    show_info
    
    # 等待用户输入
    echo -e "${YELLOW}按Ctrl+C停止应用...${NC}"
    wait $APP_PID
}

# 执行主函数
main
