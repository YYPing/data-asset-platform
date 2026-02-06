# 使用Personal Access Token上传

## 问题
GitHub已不再支持密码认证，需要使用Personal Access Token (PAT)。

## 步骤1: 生成Personal Access Token

### 通过网页生成：
1. 访问: https://github.com/settings/tokens
2. 点击: "Generate new token"
3. 选择: "Generate new token (classic)"
4. 设置:
   - Note: `data-asset-platform-upload`
   - Expiration: 7 days (或更长)
   - Select scopes: 勾选 `repo` (全选)
5. 点击: "Generate token"
6. **立即复制token** (只显示一次)

### Token权限要求:
- ✅ repo (完全控制仓库)
- ✅ workflow (可选)
- ✅ delete_repo (可选)

## 步骤2: 使用Token上传

### 方法A: 使用curl创建仓库
```bash
# 替换YOUR_TOKEN为生成的token
TOKEN="YOUR_TOKEN"

# 创建仓库
curl -H "Authorization: token $TOKEN" \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"data-asset-platform","description":"数据资产全流程管理平台","private":false}'
```

### 方法B: 使用Git推送
```bash
# 进入项目目录
cd /Users/guiping/.openclaw/workspace/data-asset-platform

# 设置远程仓库使用token
git remote set-url origin https://x-access-token:YOUR_TOKEN@github.com/915493744/data-asset-platform.git

# 或使用用户名
git remote set-url origin https://915493744:YOUR_TOKEN@github.com/915493744/data-asset-platform.git

# 推送代码
git push -u origin main
```

## 步骤3: 快速脚本

### 创建上传脚本:
```bash
cat > upload-with-token.sh << 'EOF'
#!/bin/bash

echo "请输入GitHub Personal Access Token:"
read -s TOKEN

echo "正在创建仓库..."
curl -H "Authorization: token $TOKEN" \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"data-asset-platform","description":"数据资产全流程管理平台","private":false}'

echo "正在推送代码..."
cd /Users/guiping/.openclaw/workspace/data-asset-platform
git remote set-url origin https://x-access-token:$TOKEN@github.com/915493744/data-asset-platform.git
git push -u origin main

echo "完成!"
EOF

chmod +x upload-with-token.sh
./upload-with-token.sh
```

## 步骤4: 验证上传

### 检查仓库:
```bash
# 使用token访问API
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/repos/915493744/data-asset-platform

# 或直接访问
# https://github.com/915493744/data-asset-platform
```

## 安全注意事项

### Token安全:
1. **不要分享token**
2. **设置合理过期时间**
3. **仅授予必要权限**
4. **使用后及时撤销**

### 撤销token:
1. 访问: https://github.com/settings/tokens
2. 找到对应token
3. 点击 "Revoke"

## 备选方案

### 方案1: 使用GitHub CLI
```bash
# 安装GitHub CLI
brew install gh

# 登录 (使用浏览器OAuth)
gh auth login

# 创建并推送
gh repo create data-asset-platform --public --push
```

### 方案2: 使用SSH密钥
```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "915493744@qq.com"

# 添加公钥到GitHub
# 然后使用SSH URL
git remote set-url origin git@github.com:915493744/data-asset-platform.git
git push -u origin main
```

## 故障排除

### 问题1: 权限不足
- 检查token是否有`repo`权限
- 重新生成token并勾选所有repo权限

### 问题2: 仓库已存在
```bash
# 直接推送
git push -u origin main
```

### 问题3: 网络问题
- 检查网络连接
- 尝试使用代理

## 紧急联系

如果遇到问题:
- GitHub文档: https://docs.github.com/en/authentication
- 社区支持: https://github.com/community
- 紧急情况: 联系GitHub支持

---

**建议**: 使用GitHub CLI是最安全方便的方法。