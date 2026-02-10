# Docker Desktop 安装指南

## 为什么需要Docker？

数据资产平台使用Docker来运行以下基础设施服务：
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和会话存储
- **MinIO**: 对象存储（文件上传）

使用Docker的优势：
- ✅ 一键启动所有服务
- ✅ 环境隔离，不污染本地系统
- ✅ 配置统一，团队协作方便
- ✅ 可以轻松重置和清理

## 安装步骤

### macOS 安装

**1. 下载Docker Desktop**
- 访问: https://www.docker.com/products/docker-desktop
- 点击"Download for Mac"
- 根据芯片类型选择:
  - Apple Silicon (M1/M2/M3): 选择"Mac with Apple chip"
  - Intel芯片: 选择"Mac with Intel chip"

**2. 安装**
```bash
# 打开下载的 .dmg 文件
# 将Docker图标拖到Applications文件夹
# 从Applications启动Docker Desktop
```

**3. 首次启动配置**
- 同意服务条款
- 可选: 登录Docker Hub账号（不登录也可以使用）
- 等待Docker引擎启动（菜单栏会显示Docker图标）

**4. 验证安装**
```bash
# 打开终端，运行以下命令
docker --version
# 应该显示: Docker version 24.x.x, build xxxxx

docker-compose --version
# 应该显示: Docker Compose version v2.x.x

# 测试运行
docker run hello-world
# 应该显示: Hello from Docker!
```

### 系统要求

**macOS**:
- macOS 11 Big Sur或更高版本
- 至少4GB RAM（推荐8GB+）
- 至少10GB可用磁盘空间

**Apple Silicon (M1/M2/M3)**:
- 原生支持，性能优秀
- 某些镜像可能需要Rosetta 2

**Intel Mac**:
- 需要支持虚拟化（大多数2010年后的Mac都支持）

## 配置建议

### 资源分配

打开Docker Desktop → Settings → Resources:

**推荐配置**:
- **CPUs**: 4核（最少2核）
- **Memory**: 4GB（最少2GB）
- **Swap**: 1GB
- **Disk**: 20GB（最少10GB）

### 国内镜像加速（可选）

如果Docker镜像下载很慢，可以配置镜像加速：

1. 打开Docker Desktop → Settings → Docker Engine
2. 添加以下配置:

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

3. 点击"Apply & Restart"

## 启动项目服务

安装完Docker后，在项目目录运行：

```bash
cd data-asset-platform

# 启动所有基础设施服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 常用Docker命令

### 容器管理
```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 停止容器
docker stop <container_id>

# 删除容器
docker rm <container_id>

# 查看容器日志
docker logs <container_id>
docker logs -f <container_id>  # 实时查看
```

### 镜像管理
```bash
# 查看本地镜像
docker images

# 删除镜像
docker rmi <image_id>

# 拉取镜像
docker pull postgres:15-alpine
```

### 清理
```bash
# 清理未使用的容器
docker container prune

# 清理未使用的镜像
docker image prune

# 清理所有未使用的资源（谨慎使用）
docker system prune -a
```

## 故障排查

### 1. Docker Desktop无法启动

**症状**: 点击Docker图标后一直转圈，无法启动

**解决方案**:
```bash
# 完全重置Docker
rm -rf ~/Library/Group\ Containers/group.com.docker
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/.docker

# 重新启动Docker Desktop
```

### 2. 端口冲突

**症状**: 启动服务时提示端口已被占用

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :9000  # MinIO

# 杀死进程
kill -9 <PID>

# 或者修改docker-compose.yml中的端口映射
```

### 3. 磁盘空间不足

**症状**: 无法拉取镜像或启动容器

**解决方案**:
```bash
# 查看Docker磁盘使用
docker system df

# 清理未使用的资源
docker system prune -a --volumes

# 在Docker Desktop中增加磁盘空间限制
# Settings → Resources → Disk image size
```

### 4. 网络问题

**症状**: 无法拉取镜像，连接超时

**解决方案**:
- 配置镜像加速（见上文）
- 检查网络连接
- 尝试使用VPN或代理

### 5. 权限问题

**症状**: 提示"permission denied"

**解决方案**:
```bash
# 确保Docker Desktop已启动
# 检查用户是否在docker组（Linux）
sudo usermod -aG docker $USER

# 重新登录或重启终端
```

## 替代方案：不使用Docker

如果实在无法安装Docker，可以本地安装服务：

### 使用Homebrew安装

```bash
# 安装PostgreSQL
brew install postgresql@15
brew services start postgresql@15
createdb data_asset_platform

# 安装Redis
brew install redis
brew services start redis

# MinIO需要手动下载
wget https://dl.min.io/server/minio/release/darwin-amd64/minio
chmod +x minio
./minio server /data --console-address ":9001"
```

### 修改配置

编辑 `src/backend/.env`:
```bash
DATABASE_URL=postgresql://localhost:5432/data_asset_platform
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
```

## 学习资源

- **官方文档**: https://docs.docker.com/
- **Docker Hub**: https://hub.docker.com/
- **Docker Compose文档**: https://docs.docker.com/compose/
- **中文教程**: https://yeasy.gitbook.io/docker_practice/

## 下一步

安装完Docker后：

1. ✅ 验证Docker安装: `docker --version`
2. ✅ 启动项目服务: `cd data-asset-platform && docker-compose up -d`
3. ✅ 运行测试: `./run-tests.sh`
4. ✅ 开始开发

如有问题，请查看故障排查部分或联系技术支持。
