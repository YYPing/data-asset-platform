#!/bin/bash

# 安全GitHub上传脚本
# 使用前请确保已修改GitHub密码并启用双重认证

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 安全警告
warning "================================================"
warning "⚠️  安全警告 ⚠️"
warning "================================================"
warning "您的GitHub密码可能已泄露！"
warning "请立即执行以下安全措施："
warning "1. 立即修改GitHub密码"
warning "2. 启用双重认证 (2FA)"
warning "3. 检查账号登录活动"
warning "4. 撤销可能泄露的访问令牌"
warning "================================================"
echo ""

# 检查GitHub CLI
check_gh_cli() {
    log "检查GitHub CLI..."
    if command -v gh &> /dev/null; then
        GH_VERSION=$(gh --version | head -1 | cut -d' ' -f3)
        success "GitHub CLI已安装: $GH_VERSION"
        return 0
    else
        error "GitHub CLI未安装"
        return 1
    fi
}

# 检查SSH配置
check_ssh_config() {
    log "检查SSH配置..."
    
    if [ -f ~/.ssh/id_ed25519.pub ] || [ -f ~/.ssh/id_rsa.pub ]; then
        success "SSH密钥已存在"
        
        # 测试SSH连接
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            success "SSH连接到GitHub已配置"
            return 0
        else
            warning "SSH连接到GitHub未配置"
            return 1
        fi
    else
        error "SSH密钥未生成"
        return 1
    fi
}

# 方法1: 使用GitHub CLI (最安全)
method_gh_cli() {
    log "使用方法1: GitHub CLI"
    
    # 检查登录状态
    if gh auth status &> /dev/null; then
        success "GitHub CLI已登录"
    else
        warning "GitHub CLI未登录，请按提示登录"
        gh auth login
    fi
    
    # 创建仓库
    log "创建GitHub仓库..."
    if gh repo create data-asset-platform \
        --description="数据资产全流程管理平台 - 企业级数据资产管理解决方案" \
        --public \
        --source=. \
        --remote=origin \
        --push; then
        success "仓库创建并推送成功"
        return 0
    else
        error "仓库创建失败"
        return 1
    fi
}

# 方法2: 使用SSH
method_ssh() {
    log "使用方法2: SSH"
    
    # 检查远程仓库是否已配置
    if git remote get-url origin &> /dev/null; then
        log "远程仓库已配置: $(git remote get-url origin)"
    else
        # 添加SSH远程仓库
        git remote add origin git@github.com:915493744/data-asset-platform.git
        success "SSH远程仓库已添加"
    fi
    
    # 推送代码
    log "推送代码到GitHub..."
    if git push -u origin main; then
        success "代码推送成功"
        return 0
    else
        error "代码推送失败"
        return 1
    fi
}

# 方法3: 手动步骤
method_manual() {
    log "使用方法3: 手动步骤"
    
    echo ""
    echo "请手动执行以下步骤:"
    echo ""
    echo "1. 访问 https://github.com/new 创建仓库"
    echo "   仓库名: data-asset-platform"
    echo "   描述: 数据资产全流程管理平台"
    echo "   可见性: Public"
    echo "   不要初始化README、.gitignore或license"
    echo ""
    echo "2. 创建后，执行以下命令:"
    echo "   cd /Users/guiping/.openclaw/workspace/data-asset-platform"
    echo "   git remote add origin https://github.com/915493744/data-asset-platform.git"
    echo "   git push -u origin main"
    echo ""
    echo "3. 或者使用SSH:"
    echo "   git remote add origin git@github.com:915493744/data-asset-platform.git"
    echo "   git push -u origin main"
    echo ""
    
    return 2  # 需要手动操作
}

# 安全建议
security_advice() {
    echo ""
    warning "🔒 安全建议 🔒"
    echo ""
    echo "1. 立即修改GitHub密码:"
    echo "   访问 https://github.com/settings/security"
    echo ""
    echo "2. 启用双重认证 (2FA):"
    echo "   Settings → Password and authentication → Two-factor authentication"
    echo ""
    echo "3. 检查登录活动:"
    echo "   Settings → Security → Security log"
    echo ""
    echo "4. 生成新的SSH密钥 (如果已泄露):"
    echo "   ssh-keygen -t ed25519 -C \"915493744@qq.com\""
    echo "   然后添加到GitHub Settings → SSH and GPG keys"
    echo ""
    echo "5. 使用Personal Access Token代替密码:"
    echo "   Settings → Developer settings → Personal access tokens"
    echo ""
}

# 主函数
main() {
    log "数据资产管理平台 - 安全GitHub上传脚本"
    echo ""
    
    # 显示安全警告
    security_advice
    
    read -p "是否已修改GitHub密码并采取安全措施？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "请先修改GitHub密码并采取安全措施"
        exit 1
    fi
    
    # 检查当前目录
    if [ ! -f "README.md" ] || [ ! -d "src/backend" ]; then
        error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 检查Git状态
    if [ ! -d ".git" ]; then
        error "Git仓库未初始化"
        exit 1
    fi
    
    # 选择上传方法
    echo "请选择上传方法:"
    echo "1. GitHub CLI (推荐，最安全)"
    echo "2. SSH密钥"
    echo "3. 显示手动步骤"
    echo ""
    read -p "选择 (1/2/3): " method
    
    case $method in
        1)
            if check_gh_cli; then
                method_gh_cli
            else
                error "GitHub CLI不可用"
                method_manual
            fi
            ;;
        2)
            if check_ssh_config; then
                method_ssh
            else
                error "SSH配置不可用"
                method_manual
            fi
            ;;
        3)
            method_manual
            ;;
        *)
            error "无效选择"
            method_manual
            ;;
    esac
    
    # 显示结果
    echo ""
    log "上传完成！"
    log "仓库地址: https://github.com/915493744/data-asset-platform"
    log "请访问GitHub验证文件是否完整上传"
    echo ""
    success "✅ 安全上传完成"
}

# 运行主函数
main "$@"