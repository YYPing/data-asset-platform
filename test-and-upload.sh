#!/bin/bash

# 🧪 测试并上传GitHub

set -e

echo "🧪 GitHub上传测试"
echo "=================="

# 1. 测试网络连接
echo "1. 测试网络连接..."
if curl -s --connect-timeout 10 https://github.com > /dev/null; then
    echo "   ✅ GitHub网站可访问"
else
    echo "   ❌ 无法访问GitHub"
    exit 1
fi

# 2. 测试API连接
echo "2. 测试API连接..."
if curl -s --connect-timeout 10 https://api.github.com > /dev/null; then
    echo "   ✅ GitHub API可访问"
else
    echo "   ❌ 无法访问GitHub API"
    exit 1
fi

# 3. 检查Git配置
echo "3. 检查Git配置..."
if [ -d ".git" ]; then
    echo "   ✅ Git仓库已初始化"
else
    echo "   ❌ Git未初始化"
    exit 1
fi

# 4. 检查远程仓库
echo "4. 检查远程仓库..."
if git remote get-url origin &> /dev/null; then
    echo "   ✅ 远程仓库已配置: $(git remote get-url origin)"
else
    echo "   ⚠️  远程仓库未配置"
    
    # 选择协议
    echo ""
    echo "选择远程仓库协议:"
    echo "1. HTTPS (需要token)"
    echo "2. SSH (需要SSH密钥)"
    echo "3. 退出"
    read -p "选择 (1/2/3): " protocol
    
    case $protocol in
        1)
            read -sp "请输入GitHub Token: " TOKEN
            echo ""
            git remote add origin https://x-access-token:$TOKEN@github.com/915493744/data-asset-platform.git
            unset TOKEN
            ;;
        2)
            git remote add origin git@github.com:915493744/data-asset-platform.git
            ;;
        3)
            exit 0
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
    echo "   ✅ 远程仓库已配置"
fi

# 5. 测试远程连接
echo "5. 测试远程连接..."
if git ls-remote origin &> /dev/null; then
    echo "   ✅ 远程仓库可访问"
else
    echo "   ❌ 无法访问远程仓库"
    echo "   可能原因："
    echo "   - 仓库不存在"
    echo "   - 权限不足"
    echo "   - 网络问题"
    
    # 尝试创建仓库
    echo ""
    read -p "仓库可能不存在，是否尝试创建？(y/N): " create_repo
    if [[ "$create_repo" =~ ^[Yy]$ ]]; then
        echo "   尝试第一次推送创建仓库..."
    else
        exit 1
    fi
fi

# 6. 显示待上传内容
echo ""
echo "📦 准备上传内容："
echo "----------------"
git log --oneline -5
echo "----------------"
echo "变更文件："
git status --short
echo "----------------"

# 7. 确认上传
echo ""
read -p "是否上传到GitHub？(y/N): " confirm_upload
if [[ ! "$confirm_upload" =~ ^[Yy]$ ]]; then
    echo "❌ 上传取消"
    exit 0
fi

# 8. 执行上传
echo ""
echo "🚀 开始上传..."
echo "   仓库: https://github.com/915493744/data-asset-platform"
echo "   分支: main"
echo "   提交: $(git log --oneline -1 | cut -d' ' -f2-)"
echo ""

# 尝试上传
if git push -u origin main; then
    echo ""
    echo "🎉 🎉 🎉 上传成功！ 🎉 🎉 🎉"
    echo ""
    echo "✅ 项目已成功上传到GitHub"
    echo "🔗 访问: https://github.com/915493744/data-asset-platform"
    echo ""
    
    # 显示统计
    echo "📊 上传统计："
    echo "   - 提交总数: $(git log --oneline | wc -l)"
    echo "   - 文件总数: $(git ls-files | wc -l)"
    echo "   - 代码行数: $(find . -name "*.java" -exec cat {} \; | wc -l)"
    echo ""
    
else
    echo ""
    echo "❌ 上传失败"
    echo ""
    echo "详细错误信息："
    echo "--------------"
    # 这里会显示git push的错误信息
    echo "请检查："
    echo "1. 网络连接"
    echo "2. Token/SSH密钥权限"
    echo "3. 仓库是否已存在且冲突"
    echo ""
    exit 1
fi

echo "🚀 下一步："
echo "1. 验证上传: https://github.com/915493744/data-asset-platform"
echo "2. 撤销使用的token（如果使用HTTPS）"
echo "3. 继续开发价值评估模块"
echo ""
echo "✅ 测试和上传完成！"