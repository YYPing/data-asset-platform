#!/bin/bash

# 🚀 创建GitHub仓库并推送代码

set -e

echo "🚀 GitHub仓库创建与推送"
echo "========================"

# 检查SSH连接
echo "🔑 检查SSH认证..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ SSH认证成功"
else
    echo "❌ SSH认证失败"
    echo "请先添加SSH公钥到GitHub："
    echo "1. cat ~/.ssh/id_rsa.pub"
    echo "2. 访问 https://github.com/settings/keys"
    echo "3. 粘贴并保存"
    exit 1
fi

# 检查仓库是否存在
echo "🔍 检查仓库状态..."
if git ls-remote git@github.com:915493744/data-asset-platform.git &> /dev/null; then
    echo "✅ 仓库已存在"
    REPO_EXISTS=true
else
    echo "📦 仓库不存在，需要创建"
    REPO_EXISTS=false
fi

# 显示待推送内容
echo ""
echo "📦 准备推送内容："
echo "----------------"
echo "提交: $(git log --oneline -1)"
echo "文件: $(git ls-files | wc -l)个"
echo "大小: $(du -sh . | cut -f1)"
echo "----------------"

# 确认操作
echo ""
if [ "$REPO_EXISTS" = false ]; then
    echo "将执行以下操作："
    echo "1. 创建GitHub仓库: data-asset-platform"
    echo "2. 推送所有代码到main分支"
    echo "3. 设置远程跟踪"
else
    echo "将执行以下操作："
    echo "1. 推送代码到现有仓库"
    echo "2. 更新远程分支"
fi

read -p "是否继续？(y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "❌ 操作取消"
    exit 0
fi

# 配置SSH远程仓库
echo ""
echo "⚙️ 配置远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin git@github.com:915493744/data-asset-platform.git
echo "✅ 远程仓库: git@github.com:915493744/data-asset-platform.git"

# 如果仓库不存在，需要先创建
if [ "$REPO_EXISTS" = false ]; then
    echo ""
    echo "📦 创建GitHub仓库..."
    echo ""
    echo "⚠️ 注意：由于仓库不存在，需要先通过网页创建"
    echo ""
    echo "请立即："
    echo "1. 访问 https://github.com/new"
    echo "2. 仓库名: data-asset-platform"
    echo "3. 描述: 数据资产全流程管理平台"
    echo "4. 公开仓库"
    echo "5. 不要初始化README/.gitignore/license"
    echo "6. 点击 'Create repository'"
    echo ""
    echo "创建完成后，按回车继续..."
    read -p "按回车键继续..."
fi

# 推送代码
echo ""
echo "📤 推送代码到GitHub..."
if git push -u origin main; then
    echo ""
    echo "🎉 🎉 🎉 推送成功！ 🎉 🎉 🎉"
    echo ""
    echo "✅ 项目已成功上传到GitHub"
    echo "🔗 仓库: https://github.com/915493744/data-asset-platform"
    echo "🔑 方式: SSH密钥认证"
    echo ""
    
    # 显示统计
    echo "📊 项目统计："
    echo "   - 提交: $(git log --oneline | wc -l)个"
    echo "   - 文件: $(git ls-files | wc -l)个"
    echo "   - Java代码: $(find . -name "*.java" | wc -l)个文件"
    echo "   - 设计文档: 8个 (~80k字)"
    echo "   - 完成度: ~79%"
    echo ""
    
else
    echo ""
    echo "❌ 推送失败"
    echo ""
    echo "可能原因："
    echo "1. 仓库仍未创建"
    echo "2. 分支冲突"
    echo "3. 网络问题"
    echo ""
    echo "请确保："
    echo "1. 仓库已创建：https://github.com/915493744/data-asset-platform"
    echo "2. 仓库为空（没有初始化文件）"
    echo "3. 网络连接正常"
    exit 1
fi

echo "🚀 下一步："
echo "1. 验证: https://github.com/915493744/data-asset-platform"
echo "2. 设置仓库保护规则"
echo "3. 继续开发价值评估模块"
echo ""
echo "✅ 完成！"