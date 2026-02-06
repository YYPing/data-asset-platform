# 🔒 GitHub安全配置指南

## ⚠️ 紧急安全措施

### 立即行动：
1. **撤销已泄露的token**：
   ```bash
   # 访问 https://github.com/settings/tokens
   # 找到 token: ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   # 点击 "Revoke"
   ```

2. **生成新的安全token**：
   ```bash
   # 访问 https://github.com/settings/tokens
   # 点击 "Generate new token"
   # 设置:
   #   - Note: data-asset-platform-upload-20260206
   #   - Expiration: 7 days
   #   - Select scopes: ✅ repo (全选)
   # 点击 "Generate token"
   # 立即复制新token
   ```

3. **安全存储token**：
   ```bash
   # 不要在任何地方分享token
   # 使用环境变量存储
   export GITHUB_TOKEN="你的新token"
   
   # 或使用配置文件（确保文件权限安全）
   echo "GITHUB_TOKEN=你的新token" >> ~/.env
   chmod 600 ~/.env
   ```

## 安全上传步骤

### 方法A：使用环境变量
```bash
# 1. 设置环境变量
export GITHUB_TOKEN="你的新token"

# 2. 进入项目目录
cd /Users/guiping/.openclaw/workspace/data-asset-platform

# 3. 配置Git使用token
git remote set-url origin https://x-access-token:$GITHUB_TOKEN@github.com/915493744/data-asset-platform.git

# 4. 推送代码
git push -u origin main
```

### 方法B：使用GitHub CLI（最安全）
```bash
# 1. 安装GitHub CLI
brew install gh

# 2. 安全登录（浏览器OAuth）
gh auth login

# 3. 创建并推送
gh repo create data-asset-platform \
  --description="数据资产全流程管理平台" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

### 方法C：使用脚本（自动清理）
```bash
#!/bin/bash
# save-github-upload.sh

# 读取token（不显示在终端）
read -sp "请输入GitHub Personal Access Token: " TOKEN
echo ""

# 临时配置
git remote set-url origin https://x-access-token:$TOKEN@github.com/915493744/data-asset-platform.git

# 上传
git push -u origin main

# 立即清理
unset TOKEN
git remote set-url origin https://github.com/915493744/data-asset-platform.git
echo "✅ 上传完成，token已清理"
```

## 安全最佳实践

### 1. Token管理
- ✅ 设置合理过期时间（7-30天）
- ✅ 仅授予必要权限
- ✅ 使用后及时撤销
- ✅ 不要分享token

### 2. 环境安全
- ✅ 使用环境变量存储敏感信息
- ✅ 设置文件权限（chmod 600）
- ✅ 不在日志中记录token
- ✅ 定期轮换token

### 3. 账户安全
- ✅ 启用双重认证（2FA）
- ✅ 定期检查安全日志
- ✅ 使用强密码
- ✅ 限制第三方应用权限

## 紧急处理

### 如果token已泄露：
1. **立即撤销token**
2. **检查仓库活动**
3. **修改GitHub密码**
4. **启用双重认证**

### 联系支持：
- GitHub安全报告：https://github.com/contact/report-abuse
- Token管理：https://github.com/settings/tokens
- 账户安全：https://github.com/settings/security

---

**重要**：请立即撤销已泄露的token并生成新的安全token！