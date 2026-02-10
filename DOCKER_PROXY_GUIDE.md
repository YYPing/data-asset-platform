# Docker代理配置指南

## 问题
Docker无法通过VPN拉取镜像，需要配置代理。

## 解决方案：在Docker Desktop中配置代理

### 步骤1: 打开Docker Desktop设置
1. 点击菜单栏的Docker图标（鲸鱼）
2. 选择 "Settings" 或 "Preferences"

### 步骤2: 配置代理
1. 在左侧菜单选择 "Resources" → "Proxies"
2. 启用 "Manual proxy configuration"
3. 填入以下信息：

```
Web Server (HTTP): http://127.0.0.1:7890
Secure Web Server (HTTPS): http://127.0.0.1:7890
```

4. 在 "Bypass for these hosts & domains" 中添加：
```
localhost,127.0.0.1
```

### 步骤3: 应用并重启
1. 点击 "Apply & Restart"
2. 等待Docker重启（约30秒）

### 步骤4: 验证
重启完成后，在终端运行：

```bash
docker pull postgres:15-alpine
```

如果看到下载进度条，说明配置成功！

## 常见Clash代理端口

- **Clash Verge**: 通常是 7890
- **ClashX**: 通常是 7890
- **ClashX Pro**: 通常是 7890 或 7891

## 如果不确定端口

1. 打开Clash Verge应用
2. 查看 "设置" 或 "Settings"
3. 找到 "端口设置" 或 "Port Settings"
4. 查看 HTTP/HTTPS 代理端口

## 完成配置后

运行以下命令启动所有服务：

```bash
cd data-asset-platform
docker compose up -d
docker compose ps
./run-tests.sh
```

## 如果还是失败

尝试以下替代方案：

### 方案1: 使用阿里云容器镜像服务
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.9
```

### 方案2: 手动下载镜像
访问 https://hub.docker.com 搜索镜像，使用其他方式下载

### 方案3: 使用本地PostgreSQL和Redis
```bash
# 如果Docker实在无法使用，可以本地安装
# 但需要macOS 13+
brew install postgresql@15 redis
```
