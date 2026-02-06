# 数据资产全流程管理平台

## 项目概述

数据资产全流程管理平台是一个企业级的数据资产管理解决方案，提供从客户管理、项目登记、系统评估到价值挖掘的全流程管理功能。

## 项目状态

### 开发进度：72% 完成

#### ✅ 已完成：
- **第一阶段（基础平台）**: 100% 完成
- **第二阶段-系统登记模块**: 100% 完成

#### 🔄 进行中：
- **第二阶段-价值评估模块**: 60% 进行中
- **用户认证集成**: 30% 基础框架存在

## 技术栈

### 后端技术
- **框架**: Spring Boot 3.2.2
- **ORM**: MyBatis Plus 3.5.5
- **数据库**: MySQL 8.0+
- **缓存**: Redis (可选)
- **认证**: JWT (JSON Web Token)
- **文档**: SpringDoc OpenAPI 3.0

### 前端技术 (待开发)
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia

## 功能模块

### 1. 客户管理模块
- 客户信息CRUD操作
- 客户编码自动生成
- 客户状态管理
- 客户统计报表

### 2. 项目管理模块
- 项目信息管理
- 项目进度跟踪
- 项目阶段管理
- 项目统计报表

### 3. 系统登记模块
- 客户系统信息管理
- 系统自动编码生成
- 系统状态管理
- 系统评估预警
- 丰富的统计报表

### 4. 价值评估模块 (开发中)
- 系统价值评估算法
- 风险评估模型
- 挖掘优先级推荐
- 投资回报率分析

### 5. 用户认证模块
- JWT认证授权
- 基于角色的权限控制
- 用户管理功能

## API文档

项目使用SpringDoc OpenAPI 3.0生成API文档，启动后访问：
- Swagger UI: http://localhost:8080/swagger-ui.html
- OpenAPI JSON: http://localhost:8080/v3/api-docs

### API端点统计
- 客户管理API: 12个端点
- 项目管理API: 15个端点
- 系统登记API: 25个端点
- 系统API: 2个端点
- **总计**: 54个API端点

## 快速开始

### 环境要求
- Java 17+
- Maven 3.6+
- MySQL 8.0+
- Redis (可选)

### 数据库初始化
1. 创建数据库:
   ```sql
   CREATE DATABASE data_asset CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. 执行初始化脚本:
   ```bash
   mysql -u root -p data_asset < src/backend/src/main/resources/db/init.sql
   ```

### 启动应用
1. 修改数据库配置:
   ```yaml
   # src/backend/src/main/resources/application.yml
   spring:
     datasource:
       url: jdbc:mysql://localhost:3306/data_asset
       username: your_username
       password: your_password
   ```

2. 启动应用:
   ```bash
   # 使用启动脚本
   ./start-and-test.sh
   
   # 或手动启动
   cd src/backend
   mvn spring-boot:run
   ```

3. 访问应用:
   - 应用地址: http://localhost:8080
   - API地址: http://localhost:8080/api
   - 健康检查: http://localhost:8080/api/health
   - Swagger文档: http://localhost:8080/swagger-ui.html

## 项目结构

```
data-asset-platform/
├── src/backend/                          # Spring Boot后端
│   ├── src/main/java/com/company/dataasset/
│   │   ├── controller/                   # 控制器层
│   │   ├── service/                      # 服务层
│   │   ├── mapper/                       # 数据访问层
│   │   ├── entity/                       # 实体类
│   │   ├── dto/                          # 数据传输对象
│   │   └── vo/                           # 视图对象
│   └── src/main/resources/
│       ├── mapper/                       # MyBatis XML配置
│       ├── db/init.sql                   # 数据库脚本
│       └── application.yml               # 应用配置
├── docs/                                 # 设计文档
│   ├── prototype/                        # UI原型设计
│   ├── 项目设计总结.md                    # 项目总体设计
│   └── 设计图查看指南.md                  # 设计图查看指南
├── scripts/                              # 脚本文件
│   ├── start-and-test.sh                 # 启动测试脚本
│   └── deploy.sh                         # 部署脚本
└── README.md                             # 项目说明文档
```

## 开发指南

### 代码规范
- 遵循Java开发规范
- 使用Lombok减少样板代码
- 统一的异常处理机制
- 完整的日志记录

### 数据库设计
- 使用MySQL 8.0+
- 表名使用下划线分隔
- 字段名使用下划线分隔
- 包含创建时间、更新时间、逻辑删除字段

### API设计
- RESTful API设计规范
- 统一的响应格式
- 完整的参数验证
- Swagger API文档

## 部署指南

### 开发环境
```bash
# 1. 克隆项目
git clone <repository-url>
cd data-asset-platform

# 2. 配置环境
# 修改application.yml中的数据库配置

# 3. 启动应用
./start-and-test.sh
```

### 生产环境
```bash
# 1. 构建应用
cd src/backend
mvn clean package -DskipTests

# 2. 运行应用
java -jar target/data-asset-platform-1.0.0-SNAPSHOT.jar

# 3. 使用Docker (待完善)
docker-compose up -d
```

## 测试报告

详细测试报告见: [第一阶段测试报告.md](第一阶段测试报告.md)

### 测试结果
- ✅ 项目结构完整性测试通过
- ✅ 代码逻辑测试通过
- ✅ 功能实现测试通过
- ✅ 技术特性测试通过

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目负责人: AI Assistant
- 邮箱: assistant@company.com
- 项目状态: 开发中

## 更新日志

### 2026-02-06
- ✅ 第一阶段（基础平台）开发完成
- ✅ 系统登记模块开发完成
- 🔄 价值评估模块开发中
- 📅 用户认证集成完善中

---

**最后更新**: 2026-02-06 14:04 GMT+8  
**版本**: v1.0.0-SNAPSHOT  
**状态**: 开发中