#!/bin/bash

# 🔍 检查并上传GitHub脚本

set -e

echo "🔍 GitHub上传环境检查..."
echo "================================"

# 检查目录
if [ ! -f "README.md" ]; then
    echo "❌ 错误：不在项目根目录"
    exit 1
fi

echo "✅ 项目目录：$(pwd)"

# 检查Git
if [ ! -d ".git" ]; then
    echo "❌ 错误：Git未初始化"
    exit 1
fi

echo "✅ Git已初始化"

# 检查GitHub CLI
echo "🔧 检查GitHub CLI..."
if command -v gh &> /dev/null; then
    GH_VERSION=$(gh --version | head -1)
    echo "✅ GitHub CLI已安装：$GH_VERSION"
    
    # 检查登录状态
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI已登录"
        USE_GH=true
    else
        echo "⚠️ GitHub CLI未登录"
        USE_GH=false
    fi
else
    echo "⚠️ GitHub CLI未安装"
    USE_GH=false
fi

echo ""
echo "📊 项目状态："
echo "------------------------"
git status --short
echo "------------------------"

echo ""
echo "🚀 上传选项："
echo "1. 使用GitHub CLI（如果已安装和登录）"
echo "2. 使用Personal Access Token（立即上传）"
echo "3. 显示手动步骤"
echo "4. 退出"
echo ""

read -p "请选择 (1/2/3/4): " choice

case $choice in
    1)
        if [ "$USE_GH" = true ]; then
            echo "📤 使用GitHub CLI上传..."
            
            # 添加文件
            git add .
            
            # 提交
            git commit -m "feat: 数据资产平台完整版本 $(date '+%Y-%m-%d %H:%M:%S')"
            
            # 创建仓库并推送
            gh repo create data-asset-platform \
                --description="数据资产全流程管理平台 - 企业级解决方案" \
                --public \
                --source=. \
                --remote=origin \
                --push
                
            echo "✅ 上传完成！"
            echo "🔗 https://github.com/915493744/data-asset-platform"
        else
            echo "❌ GitHub CLI不可用"
            echo "请选择其他选项"
            exit 1
        fi
        ;;
        
    2)
        echo "🔐 使用Personal Access Token上传..."
        
        # 安全警告
        echo "⚠️ 安全提醒："
        echo "   1. 请确保已撤销泄露的token"
        echo "   2. 生成新的7天token"
        echo "   3. 仅授予repo权限"
        echo ""
        
        read -sp "请输入新的GitHub Token: " GITHUB_TOKEN
        echo ""
        
        if [ -z "$GITHUB_TOKEN" ]; then
            echo "❌ 未提供token"
            exit 1
        fi
        
        # 临时配置
        git remote set-url origin https://x-access-token:$GITHUB_TOKEN@github.com/915493744/data-asset-platform.git
        
        # 添加和提交
        git add .
        git commit -m "feat: 数据资产平台 $(date '+%Y-%m-%d %H:%M:%S')"
        
        # 推送
        echo "📤 上传中..."
        git push -u origin main
        
        # 清理
        unset GITHUB_TOKEN
        git remote set-url origin https://github.com/915493744/data-asset-platform.git
        
        echo "✅ 上传完成！token已清理"
        echo "🔗 https://github.com/915493744/data-asset-platform"
        ;;
        
    3)
        echo "📋 手动上传步骤："
        echo ""
        echo "1. 访问 https://github.com/new"
        echo "   创建仓库：data-asset-platform"
        echo "   描述：数据资产全流程管理平台"
        echo "   公开仓库"
        echo ""
        echo "2. 在终端执行："
        echo "   cd $(pwd)"
        echo "   git remote add origin https://github.com/915493744/data-asset-platform.git"
        echo "   git add ."
        echo "   git commit -m '初始提交'"
        echo "   git push -u origin main"
        echo ""
        echo "3. 或使用SSH："
        echo "   git remote add origin git@github.com:915493744/data-asset-platform.git"
        echo "   git push -u origin main"
        ;;
        
    4)
        echo "👋 退出"
        exit 0
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 完成！"
echo "📊 下一步："
echo "   1. 立即撤销使用的token（如果用了token）"
echo "   2. 修改GitHub密码"
echo "   3. 启用双重认证"
echo "   4. 继续开发价值评估模块"