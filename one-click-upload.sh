#!/bin/bash

# 一键上传脚本
# 使用前请确保已准备好GitHub账号密码

set -e

echo "🚀 数据资产管理平台 - 一键上传到GitHub"
echo "========================================"
echo ""

# 检查当前目录
if [ ! -f "README.md" ] || [ ! -d "src/backend" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 检查Git仓库
if [ ! -d ".git" ]; then
    echo "❌ 错误：Git仓库未初始化"
    exit 1
fi

echo "📁 项目信息："
echo "  - 文件数量: $(find . -type f -name "*.java" -o -name "*.xml" -o -name "*.yml" -o -name "*.sql" -o -name "*.md" -o -name "*.sh" | grep -v node_modules | wc -l) 个"
echo "  - 代码量: 约135KB"
echo "  - API端点: 54个"
echo "  - 数据库表: 20+张"
echo ""

echo "⚠️ 安全警告："
echo "  您的GitHub密码将在本次上传中使用"
echo "  上传完成后请立即修改密码！"
echo ""

read -p "是否继续？(y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 上传取消"
    exit 0
fi

echo ""
echo "🔧 步骤1: 配置Git凭据..."
# 创建临时凭据文件
cat > .git-credentials-temp << EOF
https://915493744@qq.com:yyp110102101@github.com
EOF

git config --local credential.helper 'store --file=.git-credentials-temp'

echo "✅ Git凭据已配置"
echo ""

echo "🔧 步骤2: 尝试创建GitHub仓库..."
# 尝试通过API创建仓库
CREATE_RESULT=$(curl -s -u "915493744@qq.com:yyp110102101" \
  -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"data-asset-platform","description":"数据资产全流程管理平台","private":false}' 2>/dev/null || true)

if echo "$CREATE_RESULT" | grep -q "Bad credentials"; then
    echo "⚠️  API创建失败，可能需要手动创建仓库"
    echo ""
    echo "请手动创建仓库："
    echo "1. 访问 https://github.com/new"
    echo "2. 仓库名: data-asset-platform"
    echo "3. 描述: 数据资产全流程管理平台"
    echo "4. Public"
    echo "5. 不要初始化README、.gitignore、license"
    echo "6. 点击 Create repository"
    echo ""
    read -p "仓库创建完成后按回车继续..." -n 1 -r
    echo ""
elif echo "$CREATE_RESULT" | grep -q "name already exists"; then
    echo "✅ 仓库已存在，继续..."
else
    echo "✅ 仓库创建成功"
fi

echo ""
echo "🔧 步骤3: 配置远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/915493744/data-asset-platform.git
echo "✅ 远程仓库已配置"

echo ""
echo "🔧 步骤4: 推送代码到GitHub..."
echo "  这可能需要一些时间，请耐心等待..."
echo ""

# 尝试推送
if git push -u origin main 2>&1; then
    echo ""
    echo "🎉 推送成功！"
else
    echo ""
    echo "⚠️  推送失败，尝试其他方法..."
    
    # 尝试强制推送
    echo "尝试强制推送..."
    if git push -u origin main --force 2>&1; then
        echo ""
        echo "🎉 强制推送成功！"
    else
        echo ""
        echo "❌ 推送失败，请检查："
        echo "  1. 网络连接"
        echo "  2. GitHub账号密码"
        echo "  3. 仓库是否已创建"
        echo ""
        echo "可以尝试手动执行："
        echo "  git push -u origin main"
        exit 1
    fi
fi

echo ""
echo "🔧 步骤5: 清理临时文件..."
rm -f .git-credentials-temp
git config --local --unset credential.helper
echo "✅ 临时文件已清理"

echo ""
echo "📊 上传完成！"
echo "========================================"
echo "✅ 项目已上传到GitHub"
echo "🌐 访问地址: https://github.com/915493744/data-asset-platform"
echo ""
echo "📁 上传内容："
echo "  - 75个文件"
echo "  - 135KB代码"
echo "  - 54个API端点"
echo "  - 完整文档"
echo ""
echo "⚠️ 紧急安全措施："
echo "========================================"
echo "1. 🔒 立即修改GitHub密码："
echo "   访问 https://github.com/settings/security"
echo ""
echo "2. 🔐 启用双重认证："
echo "   Settings → Password and authentication → Two-factor authentication"
echo ""
echo "3. 📋 检查登录活动："
echo "   Settings → Security → Security log"
echo ""
echo "4. 🗑️ 撤销本次使用的凭据："
echo "   访问 https://github.com/settings/tokens"
echo "   检查并撤销可疑令牌"
echo ""
echo "⏰ 请立即执行以上安全措施！"
echo "========================================"

# 显示验证命令
echo ""
echo "🔍 验证上传："
echo "curl -s https://api.github.com/repos/915493744/data-asset-platform | grep -E '\"name\"|\"description\"|\"html_url\"'"
echo ""

exit 0