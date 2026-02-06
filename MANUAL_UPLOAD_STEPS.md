# 手动上传步骤 (在终端中执行)

## 步骤1: 生成Personal Access Token

### 在浏览器中:
1. 访问: https://github.com/settings/tokens
2. 点击: "Generate new token"
3. 选择: "Generate new token (classic)"
4. 设置:
   - Note: `data-asset-platform-upload`
   - Expiration: 30 days
   - Select scopes: ✅ 勾选 `repo` (全选)
5. 点击: "Generate token"
6. **立即复制token** (类似 `ghp_XXX_REPLACE_WITH_YOUR_TOKEN_XXXxxxxxxxxxxxxxxxxx`)

## 步骤2: 在终端中执行以下命令

### 打开终端，逐行执行:
```bash
# 1. 进入项目目录
cd /Users/guiping/.openclaw/workspace/data-asset-platform

# 2. 设置变量 (替换YOUR_TOKEN为刚才复制的token)
TOKEN="ghp_XXX_REPLACE_WITH_YOUR_TOKEN_XXXxxxxxxxxxxxxxxxxx"

# 3. 创建GitHub仓库
curl -H "Authorization: token $TOKEN" \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"data-asset-platform","description":"数据资产全流程管理平台","private":false}'

# 4. 等待2秒让仓库创建完成
sleep 2

# 5. 配置Git使用token
git remote set-url origin https://x-access-token:$TOKEN@github.com/915493744/data-asset-platform.git

# 6. 推送代码
git push -u origin main

# 7. 验证上传
echo "上传完成！访问: https://github.com/915493744/data-asset-platform"
```

## 步骤3: 一键执行脚本

### 创建并执行脚本:
```bash
cd /Users/guiping/.openclaw/workspace/data-asset-platform

cat > quick-upload.sh << 'EOF'
#!/bin/bash
echo "🔧 数据资产管理平台上传脚本"
echo "=============================="
echo ""
echo "请在此处粘贴您的GitHub Personal Access Token:"
read -s TOKEN
echo ""
echo "正在创建仓库..."
curl -s -H "Authorization: token $TOKEN" \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"data-asset-platform","description":"数据资产全流程管理平台","private":false}' > /dev/null
echo "✅ 仓库创建请求已发送"
sleep 3
echo "正在配置Git..."
git remote set-url origin https://x-access-token:$TOKEN@github.com/915493744/data-asset-platform.git
echo "正在推送代码..."
if git push -u origin main 2>&1; then
    echo "🎉 上传成功！"
    echo "🌐 访问: https://github.com/915493744/data-asset-platform"
else
    echo "⚠️ 推送失败，尝试强制推送..."
    git push -u origin main --force
    echo "✅ 强制推送完成"
fi
echo ""
echo "⚠️ 安全提醒: 上传完成后请修改GitHub密码！"
EOF

chmod +x quick-upload.sh
./quick-upload.sh
```

## 步骤4: 验证上传成功

### 在浏览器中访问:
https://github.com/915493744/data-asset-platform

### 或使用curl验证:
```bash
curl -s https://api.github.com/repos/915493744/data-asset-platform | grep -E '"name"|"description"|"html_url"'
```

## 预期结果

### 成功上传后应该看到:
- 仓库名称: `data-asset-platform`
- 描述: `数据资产全流程管理平台`
- 75个文件
- 完整的代码结构

## 故障排除

### 如果创建仓库失败:
```bash
# 直接尝试推送 (假设仓库已存在)
git push -u origin main
```

### 如果提示权限问题:
```bash
# 重新生成token，确保有repo权限
# 然后更新远程URL
git remote set-url origin https://x-access-token:NEW_TOKEN@github.com/915493744/data-asset-platform.git
git push -u origin main
```

### 如果网络问题:
- 检查网络连接
- 等待几分钟后重试

## 安全提醒

### 上传后立即:
1. **修改GitHub密码**
2. **启用双重认证**
3. **撤销使用的token** (在 https://github.com/settings/tokens)

### Token安全:
- 不要分享token
- 设置合理过期时间
- 使用后及时撤销

## 联系方式

如有问题:
- GitHub文档: https://docs.github.com
- 本项目问题: 查看README.md

---

**最后更新**: 2026-02-06 14:26  
**状态**: 等待执行上传