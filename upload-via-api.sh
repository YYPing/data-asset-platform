#!/bin/bash

# 🚀 使用GitHub API直接上传
# 当Git协议有问题时的备选方案

set -e

echo "🌐 GitHub API上传方案"
echo "========================"

# 读取token
read -sp "请输入GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 未提供token"
    exit 1
fi

# 验证token
echo "🔍 验证token..."
USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
if echo "$USER_INFO" | grep -q '"login"'; then
    USERNAME=$(echo "$USER_INFO" | grep '"login"' | head -1 | cut -d'"' -f4)
    echo "✅ Token有效，用户: $USERNAME"
else
    echo "❌ Token无效或权限不足"
    exit 1
fi

# 检查仓库是否存在
echo "🔍 检查仓库状态..."
REPO_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/915493744/data-asset-platform)

if echo "$REPO_INFO" | grep -q '"not found"'; then
    echo "📦 仓库不存在，创建新仓库..."
    
    # 创建仓库
    CREATE_RESPONSE=$(curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "data-asset-platform",
            "description": "数据资产全流程管理平台 - 企业级解决方案",
            "private": false,
            "has_issues": true,
            "has_projects": true,
            "has_wiki": true
        }' \
        https://api.github.com/user/repos)
    
    if echo "$CREATE_RESPONSE" | grep -q '"id"'; then
        echo "✅ 仓库创建成功"
    else
        echo "❌ 仓库创建失败"
        echo "$CREATE_RESPONSE"
        exit 1
    fi
else
    echo "✅ 仓库已存在"
fi

# 创建临时工作目录
TEMP_DIR=$(mktemp -d)
echo "📁 临时目录: $TEMP_DIR"

# 复制项目文件（排除.git等）
echo "📦 打包项目文件..."
rsync -av --exclude='.git' --exclude='.git-credentials' --exclude='node_modules' \
    --exclude='target' --exclude='*.log' --exclude='*.tmp' \
    . "$TEMP_DIR/data-asset-platform/"

cd "$TEMP_DIR"

# 创建ZIP文件
echo "🗜️ 创建ZIP压缩包..."
zip -r data-asset-platform.zip data-asset-platform/ > /dev/null
ZIP_SIZE=$(du -h data-asset-platform.zip | cut -f1)
echo "✅ ZIP文件大小: $ZIP_SIZE"

# 注意：GitHub API不支持直接上传ZIP创建仓库内容
# 需要先初始化仓库，然后通过Git操作
echo ""
echo "⚠️ 注意：GitHub API限制"
echo "----------------------"
echo "GitHub API不支持直接上传ZIP文件创建仓库内容。"
echo "需要先通过Git命令行推送。"
echo ""
echo "建议解决方案："
echo "1. 使用SSH方式（upload-via-ssh.sh）"
echo "2. 检查网络设置"
echo "3. 使用GitHub CLI"
echo ""

# 清理
cd - > /dev/null
rm -rf "$TEMP_DIR"

# 显示Git命令
echo "📋 手动Git命令："
echo "---------------"
echo "cd /Users/guiping/.openclaw/workspace/data-asset-platform"
echo "git remote add origin https://x-access-token:$GITHUB_TOKEN@github.com/915493744/data-asset-platform.git"
echo "git push -u origin main"
echo ""
echo "或使用SSH："
echo "git remote add origin git@github.com:915493744/data-asset-platform.git"
echo "git push -u origin main"
echo ""

# 清理token
unset GITHUB_TOKEN

echo "🔒 Token已清理"
echo ""
echo "🎯 建议使用SSH方式上传！"