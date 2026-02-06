#!/bin/bash

# 🔐 立即使用token上传GitHub
# 注意：使用后请立即撤销token！

set -e

echo "🚀 立即上传数据资产平台到GitHub..."
echo "⚠️ 警告：请确保已撤销之前泄露的token！"

# 检查项目目录
if [ ! -f "README.md" ]; then
    echo "❌ 错误：请在项目根目录运行"
    exit 1
fi

# 检查Git配置
if [ ! -d ".git" ]; then
    echo "❌ 错误：Git仓库未初始化"
    exit 1
fi

# 显示当前状态
echo "📊 项目状态："
echo "   - 目录：$(pwd)"
echo "   - 文件数：$(find . -type f -name "*.java" | wc -l)个Java文件"
echo "   - 代码量：$(find . -type f -name "*.java" -exec cat {} \; | wc -l)行Java代码"
echo ""

# 安全警告
echo "🔒 安全警告："
echo "   1. 请确保已撤销token: ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
echo "   2. 生成新的token：https://github.com/settings/tokens"
echo "   3. 设置过期时间：7天"
echo "   4. 仅授予repo权限"
echo ""

# 读取新token
read -sp "请输入新的GitHub Personal Access Token: " NEW_TOKEN
echo ""

if [ -z "$NEW_TOKEN" ]; then
    echo "❌ 错误：未提供token"
    exit 1
fi

# 验证token格式
if [[ ! "$NEW_TOKEN" =~ ^ghp_[a-zA-Z0-9]{36}$ ]] && [[ ! "$NEW_TOKEN" =~ ^gho_[a-zA-Z0-9]{36}$ ]] && [[ ! "$NEW_TOKEN" =~ ^github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}$ ]]; then
    echo "⚠️ 警告：token格式可能不正确，但继续尝试..."
fi

echo "⚙️ 配置Git远程仓库..."
# 临时使用token配置远程仓库
git remote set-url origin https://x-access-token:$NEW_TOKEN@github.com/915493744/data-asset-platform.git

echo "📦 添加文件到Git..."
git add .

echo "💾 提交更改..."
git commit -m "feat: 数据资产平台完整版本 - 包含设计和实现

- 完整设计文档（8个文档，~80k字）
- Spring Boot后端架构
- 客户管理模块（29个API端点）
- 系统注册模块（25个API端点）
- 价值评估模块（多模型AI集成）
- Docker容器化配置
- 测试计划和API脚本
- 总代码量：~175KB，54+ API端点

完成度：~79%
时间：$(date '+%Y-%m-%d %H:%M:%S')"

echo "📤 上传到GitHub..."
if git push -u origin main; then
    echo "✅ 上传成功！"
    
    # 显示仓库信息
    echo ""
    echo "🎉 项目已成功上传到GitHub！"
    echo "🔗 仓库地址：https://github.com/915493744/data-asset-platform"
    echo "📊 查看文件：https://github.com/915493744/data-asset-platform/tree/main"
    echo ""
    
    # 清理token
    echo "🧹 清理token配置..."
    unset NEW_TOKEN
    git remote set-url origin https://github.com/915493744/data-asset-platform.git
    
    echo "✅ Token已清理"
    
    # 安全建议
    echo ""
    echo "🔒 立即执行以下安全措施："
    echo "   1. 访问 https://github.com/settings/tokens"
    echo "   2. 撤销刚才使用的token"
    echo "   3. 生成新的token用于后续使用"
    echo "   4. 启用双重认证：https://github.com/settings/security"
    echo "   5. 修改GitHub密码：https://github.com/settings/security"
    
else
    echo "❌ 上传失败！"
    echo "可能的原因："
    echo "   1. Token权限不足"
    echo "   2. 网络问题"
    echo "   3. 仓库已存在"
    echo ""
    echo "请检查："
    echo "   - Token是否有repo权限"
    echo "   - 仓库是否已存在：https://github.com/915493744/data-asset-platform"
    echo "   - 网络连接"
    
    # 清理token
    unset NEW_TOKEN
    git remote set-url origin https://github.com/915493744/data-asset-platform.git
    exit 1
fi

echo ""
echo "📋 下一步："
echo "   1. 立即撤销使用的token"
echo "   2. 继续完成价值评估模块开发"
echo "   3. 完善用户认证系统"
echo "   4. 进行整体测试"
echo ""
echo "🚀 开发继续！"