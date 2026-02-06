# 使用Maven构建阶段
FROM maven:3.9.6-eclipse-temurin-17 AS build

WORKDIR /app

# 复制pom.xml和源代码
COPY pom.xml .
COPY src ./src

# 构建应用
RUN mvn clean package -DskipTests

# 运行阶段
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# 复制构建的jar文件
COPY --from=build /app/target/*.jar app.jar

# 创建必要的目录
RUN mkdir -p /opt/data-asset/uploads /opt/data-asset/reports /opt/data-asset/temp /opt/data-asset/templates

# 设置时区
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 暴露端口
EXPOSE 8080

# 运行应用
ENTRYPOINT ["java", "-jar", "app.jar"]
