#!/bin/bash

# 🔒 安全GitHub上传脚本
# 使用GitHub CLI或token安全上传

set -e  # 出错时退出

echo "🚀 开始安全上传数据资产平台到GitHub..."

# 检查是否在项目目录
if [ ! -f "pom.xml" ] && [ ! -f "package.json" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Git配置
if [ ! -d ".git" ]; then
    echo "❌ 错误：未找到.git目录，请先初始化Git"
    exit 1
fi

# 检查远程仓库配置
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
if [ -z "$REMOTE_URL" ]; then
    echo "❌ 错误：未配置远程仓库"
    echo "请先运行: git remote add origin https://github.com/915493744/data-asset-platform.git"
    exit 1
fi

echo "📦 检查本地更改..."
git status --short

# 询问确认
read -p "是否继续上传？(y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "❌ 上传取消"
    exit 0
fi

echo "🔍 检查GitHub CLI..."
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI已安装"
    
    # 检查是否已登录
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI已登录"
        echo "📤 使用GitHub CLI上传..."
        
        # 添加所有文件
        git add .
        
        # 提交
        git commit -m "feat: 数据资产平台完整版本 $(date '+%Y-%m-%d %H:%M:%S')"
        
        # 推送
        git push -u origin main
        
        echo "✅ 上传完成！"
        
        # 显示仓库信息
        echo "🔗 仓库地址: https://github.com/915493744/data-asset-platform"
        
    else
        echo "⚠️ GitHub CLI未登录"
        echo "请运行: gh auth login"
        echo "或使用下面的token方法"
        USE_TOKEN=true
    fi
else
    echo "⚠️ GitHub CLI未安装"
    USE_TOKEN=true
fi

# 使用token方法
if [ "$USE_TOKEN" = true ]; then
    echo "🔐 使用Personal Access Token上传..."
    
    # 安全读取token
    read -sp "请输入GitHub Personal Access Token: " GITHUB_TOKEN
    echo ""
    
    if [ -z "$GITHUB_TOKEN" ]; then
        echo "❌ 错误：未提供token"
        exit 1
    fi
    
    # 临时配置远程仓库使用token
    echo "⚙️ 配置远程仓库..."
    git remote set-url origin https://x-access-token:$GITHUB_TOKEN@github.com/915493744/data-asset-platform.git
    
    # 添加所有文件
    git add .
    
    # 提交
    git commit -m "feat: 数据资产平台完整版本 $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 推送
    echo "📤 上传代码..."
    git push -u origin main
    
    # 清理token
    unset GITHUB_TOKEN
    git remote set-url origin https://github.com/915493744/data-asset-platform.git
    
    echo "✅ 上传完成！token已清理"
    echo "🔗 仓库地址: https://github.com/915493744/data-asset-platform"
fi

echo ""
echo "🎉 上传完成！"
echo "📊 项目统计："
echo "   - 总代码量：~175KB"
echo "   - API端点：54+"
echo "   - 数据库表：20+"
echo "   - 完成度：~79%"
echo ""
echo "⚠️ 安全提醒："
echo "   1. 请立即撤销已泄露的token"
echo "   2. 启用GitHub双重认证"
echo "   3. 定期检查仓库安全设置"