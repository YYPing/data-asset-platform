# 🐙 GitHub技能安装与配置指南

## 📦 GitHub技能概述

OpenClaw内置了GitHub技能，使用`gh` CLI工具与GitHub交互。技能支持：
- ✅ 仓库管理（创建、克隆、推送）
- ✅ Issue和PR管理
- ✅ CI/CD状态检查
- ✅ API高级查询
- ✅ JSON输出处理

## 🔧 安装GitHub CLI

### 方法1：Homebrew（推荐）
```bash
# 如果brew安装慢，可以跳过更新
HOMEBREW_NO_AUTO_UPDATE=1 brew install gh
```

### 方法2：MacPorts
```bash
sudo port install gh
```

### 方法3：直接下载
```bash
# 下载最新版本
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signedby=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### 方法4：使用已安装的版本
```bash
# 检查是否已安装
which gh || echo "未安装"
```

## 🔐 GitHub CLI认证

### 登录GitHub CLI
```bash
# 交互式登录（推荐）
gh auth login

# 使用token登录
gh auth login --with-token < ~/.github-token

# 检查登录状态
gh auth status
```

### 认证方式选择
1. **HTTPS**：使用GitHub token
2. **SSH**：使用SSH密钥
3. **GitHub.com**：默认使用GitHub.com

## 🚀 使用GitHub技能

### 基本命令
```bash
# 查看帮助
gh --help

# 仓库操作
gh repo create data-asset-platform --public --description "数据资产平台"

# 克隆仓库
gh repo clone 915493744/data-asset-platform

# 查看仓库信息
gh repo view 915493744/data-asset-platform
```

### Issue管理
```bash
# 创建issue
gh issue create --title "功能请求" --body "详细描述"

# 列出issue
gh issue list --state open

# 查看issue
gh issue view 123
```

### Pull Request管理
```bash
# 创建PR
gh pr create --title "新功能" --body "描述变更"

# 查看PR状态
gh pr status

# 合并PR
gh pr merge 123 --squash
```

### CI/CD状态
```bash
# 查看工作流运行
gh run list

# 查看具体运行
gh run view 123456789

# 查看失败日志
gh run view 123456789 --log-failed
```

## 📁 数据资产平台上传流程

### 步骤1：安全准备
```bash
# 撤销泄露的token
# 访问：https://github.com/settings/tokens

# 生成新token
# 设置：7天过期，仅repo权限
```

### 步骤2：配置项目
```bash
cd /Users/guiping/.openclaw/workspace/data-asset-platform

# 初始化Git（如果未初始化）
git init
git add .
git commit -m "初始提交"
```

### 步骤3：使用GitHub CLI上传
```bash
# 方法A：创建新仓库并推送
gh repo create data-asset-platform \
  --description="数据资产全流程管理平台" \
  --public \
  --source=. \
  --remote=origin \
  --push

# 方法B：推送到现有仓库
git remote add origin https://github.com/915493744/data-asset-platform.git
git push -u origin main
```

### 步骤4：验证上传
```bash
# 检查远程仓库
git remote -v

# 查看提交历史
git log --oneline

# 访问网页验证
open https://github.com/915493744/data-asset-platform
```

## 🔧 OpenClaw集成

### 在OpenClaw中使用GitHub技能
```bash
# 通过exec调用
exec: gh repo view 915493744/data-asset-platform

# 检查CI状态
exec: gh run list --repo 915493744/data-asset-platform

# 创建issue
exec: gh issue create --repo 915493744/data-asset-platform --title "Bug报告" --body "详细描述"
```

### 自动化脚本
```bash
#!/bin/bash
# github-automation.sh

# 检查GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "安装GitHub CLI..."
    brew install gh
fi

# 登录检查
if ! gh auth status &> /dev/null; then
    echo "请登录GitHub CLI..."
    gh auth login
fi

# 上传项目
gh repo create data-asset-platform \
  --description="企业级数据资产管理平台" \
  --public \
  --source=. \
  --remote=origin \
  --push

echo "✅ 上传完成！"
```

## 🛡️ 安全最佳实践

### Token管理
```bash
# 环境变量存储
export GITHUB_TOKEN="ghp_XXX_REPLACE_WITH_YOUR_TOKEN_XXX"

# 临时使用
GITHUB_TOKEN="ghp_XXX_REPLACE_WITH_YOUR_TOKEN_XXX" gh auth login --with-token

# 清理
unset GITHUB_TOKEN
```

### 权限控制
1. **最小权限原则**：仅授予必要权限
2. **短期token**：设置7-30天过期
3. **定期轮换**：每月更新token
4. **审计日志**：监控token使用

### 仓库安全
1. **分支保护**：保护main分支
2. **代码审查**：要求PR审查
3. **状态检查**：要求CI通过
4. **安全扫描**：启用代码扫描

## 🚨 故障排除

### 常见问题
1. **认证失败**
   ```bash
   gh auth logout
   gh auth login
   ```

2. **权限不足**
   ```bash
   # 检查token权限
   gh auth status
   # 重新生成token
   ```

3. **网络问题**
   ```bash
   # 测试连接
   curl -I https://api.github.com
   # 设置代理
   export HTTPS_PROXY=http://proxy:port
   ```

4. **仓库已存在**
   ```bash
   # 删除远程仓库
   git remote remove origin
   # 或推送到不同分支
   git push -u origin dev
   ```

### 调试命令
```bash
# 详细输出
gh --verbose repo view

# JSON输出
gh repo view --json name,description,url

# API调试
gh api /user --jq '.login'
```

## 📚 学习资源

### 官方文档
- **GitHub CLI文档**：https://cli.github.com/manual/
- **GitHub API文档**：https://docs.github.com/en/rest
- **OpenClaw GitHub技能**：查看SKILL.md

### 实用命令
```bash
# 查看所有命令
gh help --all

# 查看命令帮助
gh help repo
gh help pr
gh help issue

# 查看版本
gh version
```

### 社区资源
- **GitHub CLI仓库**：https://github.com/cli/cli
- **问题反馈**：https://github.com/cli/cli/issues
- **Discord社区**：https://discord.gg/github

## 🎯 立即行动清单

### 安装阶段
1. [ ] 安装GitHub CLI：`brew install gh`
2. [ ] 登录认证：`gh auth login`
3. [ ] 验证安装：`gh --version`

### 安全阶段
1. [ ] 撤销泄露token
2. [ ] 生成新token
3. [ ] 修改GitHub密码
4. [ ] 启用双重认证

### 上传阶段
1. [ ] 进入项目目录
2. [ ] 运行上传脚本
3. [ ] 验证上传结果
4. [ ] 清理临时token

### 后续阶段
1. [ ] 设置仓库保护规则
2. [ ] 配置CI/CD流水线
3. [ ] 添加项目文档
4. [ ] 邀请协作者

---

**提示**：如果brew安装慢，可以先使用token方法上传，稍后再安装GitHub CLI。