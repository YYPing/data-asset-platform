# Mac重装前备份清单

## 📦 需要备份的内容

### 1. 项目文件
```bash
# 当前工作目录
/Users/guiping/.openclaw/workspace/

# 重要项目
- data-asset-platform/  # 数据资产管理平台
- 所有设计文档和代码
```

### 2. 配置文件
```bash
# OpenClaw配置
~/.openclaw/

# Git配置
~/.gitconfig
~/.ssh/  # SSH密钥

# 开发工具配置
~/.zshrc
~/.bashrc
~/.vimrc
```

### 3. 重要数据
- 浏览器书签和密码
- 应用程序数据
- 文档和下载文件夹

## 🔄 备份命令

### 快速备份项目
```bash
# 创建备份目录
mkdir -p ~/Desktop/backup_$(date +%Y%m%d)

# 备份OpenClaw工作区
cp -r ~/.openclaw/workspace ~/Desktop/backup_$(date +%Y%m%d)/

# 备份配置文件
cp ~/.gitconfig ~/Desktop/backup_$(date +%Y%m%d)/ 2>/dev/null
cp -r ~/.ssh ~/Desktop/backup_$(date +%Y%m%d)/ 2>/dev/null
cp ~/.zshrc ~/Desktop/backup_$(date +%Y%m%d)/ 2>/dev/null

# 压缩备份
cd ~/Desktop
tar -czf backup_$(date +%Y%m%d).tar.gz backup_$(date +%Y%m%d)/

echo "备份完成: ~/Desktop/backup_$(date +%Y%m%d).tar.gz"
```

### 备份到云盘
```bash
# 如果有iCloud
cp ~/Desktop/backup_*.tar.gz ~/Library/Mobile\ Documents/com~apple~CloudDocs/

# 或上传到其他云盘
```

## 📋 重装后恢复步骤

### 1. 安装基础工具（约30分钟）
```bash
# 安装Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装开发工具
brew install git node python@3.11

# 安装Docker Desktop
# 下载: https://www.docker.com/products/docker-desktop
```

### 2. 恢复OpenClaw（约10分钟）
```bash
# 安装OpenClaw
npm install -g @qingchencloud/openclaw-zh

# 恢复工作区
mkdir -p ~/.openclaw
tar -xzf backup_*.tar.gz
cp -r backup_*/workspace ~/.openclaw/

# 启动OpenClaw
openclaw gateway start
```

### 3. 恢复项目环境（约15分钟）
```bash
cd ~/.openclaw/workspace/data-asset-platform

# 后端环境
cd src/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端环境
cd ../frontend
npm install

# Docker服务
cd ../..
docker compose up -d
```

### 4. 配置VPN和代理
- 安装Clash Verge
- 配置Docker代理（参考DOCKER_PROXY_GUIDE.md）

## 🎯 重装后的优势

### 解决的问题
- ✅ Docker网络问题
- ✅ Homebrew版本问题（当前系统版本不支持）
- ✅ 系统环境干净

### 预计时间
- 系统重装: 1-2小时
- 工具安装: 30分钟
- 环境恢复: 30分钟
- **总计: 2-3小时**

## 💡 重装前建议

### 检查是否真的需要重装
当前问题可能可以通过以下方式解决：
1. **升级macOS** - 如果版本太旧
2. **修复Docker** - 重新安装Docker Desktop
3. **清理Homebrew** - 卸载重装

### 如果确定要重装
1. ✅ 备份所有重要数据
2. ✅ 记录所有账号密码
3. ✅ 导出浏览器书签
4. ✅ 记录已安装的应用列表
5. ✅ 备份项目代码到Git仓库

## 📝 当前项目状态记录

### 数据资产管理平台
- **状态**: 环境配置70%完成
- **已完成**:
  - ✅ Python虚拟环境 + 67个依赖包
  - ✅ Node.js环境 + Vue 3依赖
  - ✅ 测试文件和脚本
  - ✅ 完整文档
- **待完成**:
  - ⏳ Docker镜像拉取
  - ⏳ 服务启动
  - ⏳ 功能测试

### 重要文件
- `data-asset-platform/` - 完整项目
- `MEMORY.md` - 长期记忆
- `memory/2026-02-09.md` - 今日工作日志

## 🚀 重装后快速启动

重装完成后，只需运行：
```bash
cd ~/.openclaw/workspace/data-asset-platform
./start-all.sh
```

一切都会自动配置好！

## ⚠️ 重要提醒

1. **确保备份完整** - 检查备份文件是否可以正常解压
2. **记录账号信息** - OpenClaw、Git、云服务等
3. **保存激活码** - 付费软件的许可证
4. **测试恢复** - 在重装前测试备份恢复流程

---

**需要我帮您执行备份命令吗？**
