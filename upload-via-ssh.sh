#!/bin/bash

# 🔐 使用SSH方式上传GitHub
# 避免HTTPS网络问题

set -e

echo "🔑 GitHub SSH上传方案"
echo "========================"

# 检查SSH密钥
echo "🔍 检查SSH密钥..."
if [ -f ~/.ssh/id_ed25519 ] || [ -f ~/.ssh/id_rsa ]; then
    echo "✅ SSH密钥已存在"
else
    echo "❌ 未找到SSH密钥"
    echo ""
    echo "请生成SSH密钥："
    echo "ssh-keygen -t ed25519 -C \"915493744@qq.com\""
    echo ""
    echo "然后添加公钥到GitHub："
    echo "1. 访问 https://github.com/settings/keys"
    echo "2. 点击 'New SSH key'"
    echo "3. 标题: MacBook-$(hostname)"
    echo "4. 密钥类型: Authentication Key"
    echo "5. 粘贴: cat ~/.ssh/id_ed25519.pub"
    echo ""
    exit 1
fi

# 测试SSH连接
echo "🔗 测试SSH连接到GitHub..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ SSH连接成功"
else
    echo "❌ SSH连接失败"
    echo ""
    echo "可能原因："
    echo "1. SSH密钥未添加到GitHub"
    echo "2. SSH代理问题"
    echo "3. 网络限制"
    echo ""
    echo "请先添加SSH密钥到GitHub"
    exit 1
fi

# 配置SSH远程仓库
echo "⚙️ 配置SSH远程仓库..."
if git remote get-url origin &> /dev/null; then
    CURRENT_URL=$(git remote get-url origin)
    echo "当前远程仓库: $CURRENT_URL"
    
    if [[ "$CURRENT_URL" == *"https://"* ]]; then
        echo "切换为SSH协议..."
        git remote set-url origin git@github.com:915493744/data-asset-platform.git
    fi
else
    echo "添加SSH远程仓库..."
    git remote add origin git@github.com:915493744/data-asset-platform.git
fi

echo "✅ 远程仓库配置: $(git remote get-url origin)"

# 显示待上传内容
echo ""
echo "📦 准备上传内容："
echo "----------------"
git status --short
echo "----------------"

# 确认上传
read -p "是否上传到GitHub？(y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "❌ 上传取消"
    exit 0
fi

# 推送代码
echo "📤 上传代码到GitHub..."
if git push -u origin main; then
    echo ""
    echo "🎉 🎉 🎉 SSH上传成功！ 🎉 🎉 🎉"
    echo ""
    echo "✅ 项目已通过SSH安全上传"
    echo "🔗 仓库: https://github.com/915493744/data-asset-platform"
    echo "🔑 方式: SSH密钥认证"
    echo ""
    
    # 显示统计
    echo "📊 上传统计："
    echo "  - 提交: $(git log --oneline | wc -l)个"
    echo "  - 文件: $(git ls-files | wc -l)个"
    echo "  - 大小: $(du -sh . | cut -f1)"
    echo ""
    
else
    echo "❌ SSH上传失败"
    echo ""
    echo "可能原因："
    echo "1. 仓库权限问题"
    echo "2. 分支冲突"
    echo "3. SSH密钥权限不足"
    echo ""
    exit 1
fi

echo "🚀 下一步："
echo "1. 访问 https://github.com/915493744/data-asset-platform 验证"
echo "2. 继续开发价值评估模块"
echo "3. 设置仓库保护规则"
echo ""
echo "✅ SSH上传完成！"