#!/bin/bash
# GitHub SSH密钥配置脚本

echo "🔑 GitHub SSH密钥配置脚本"
echo "=========================="

# 检查SSH目录
if [ ! -d ~/.ssh ]; then
    echo "创建 ~/.ssh 目录..."
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
fi

echo ""
echo "请选择配置方式:"
echo "1. 使用现有密钥文件"
echo "2. 输入密钥文本内容"
echo "3. 生成新的SSH密钥"
echo "4. 使用HTTPS方式（推荐）"
read -p "请输入选择 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "📁 使用现有密钥文件"
        read -p "请输入密钥文件路径: " key_file
        
        if [ ! -f "$key_file" ]; then
            echo "❌ 密钥文件不存在: $key_file"
            exit 1
        fi
        
        # 复制密钥文件
        cp "$key_file" ~/.ssh/id_rsa
        chmod 600 ~/.ssh/id_rsa
        
        # 如果有公钥也复制
        if [ -f "${key_file}.pub" ]; then
            cp "${key_file}.pub" ~/.ssh/id_rsa.pub
            chmod 644 ~/.ssh/id_rsa.pub
        fi
        
        echo "✅ 密钥文件已复制到 ~/.ssh/"
        ;;
    
    2)
        echo ""
        echo "📝 输入密钥文本内容"
        echo "请粘贴SSH私钥内容（以-----BEGIN开头，-----END结尾）:"
        echo "（粘贴完成后按Ctrl+D结束）"
        
        # 读取多行输入
        cat > ~/.ssh/id_rsa.tmp
        mv ~/.ssh/id_rsa.tmp ~/.ssh/id_rsa
        chmod 600 ~/.ssh/id_rsa
        
        echo "✅ 密钥已保存到 ~/.ssh/id_rsa"
        ;;
    
    3)
        echo ""
        echo "🆕 生成新的SSH密钥"
        read -p "请输入邮箱地址（用于标识密钥）: " email
        
        ssh-keygen -t rsa -b 4096 -C "$email" -f ~/.ssh/id_rsa -N ""
        
        echo ""
        echo "✅ 新密钥已生成！"
        echo "公钥内容:"
        cat ~/.ssh/id_rsa.pub
        echo ""
        echo "请将上面的公钥添加到GitHub:"
        echo "1. 登录GitHub → Settings"
        echo "2. SSH and GPG keys → New SSH key"
        echo "3. 粘贴公钥内容"
        ;;
    
    4)
        echo ""
        echo "🌐 使用HTTPS方式"
        echo "切换到HTTPS远程地址..."
        
        cd /Users/yyp/.openclaw/workspace/data-asset-platform
        git remote set-url origin https://github.com/YYPing/data-asset-platform.git
        
        echo "✅ 已切换到HTTPS远程"
        echo ""
        echo "📋 使用说明:"
        echo "1. 需要GitHub Personal Access Token"
        echo "2. 生成Token: GitHub → Settings → Developer settings"
        echo "3. 权限: repo (完全控制仓库)"
        echo "4. 推送时使用Token作为密码"
        echo ""
        echo "推送命令: git push origin main"
        exit 0
        ;;
    
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🔍 测试SSH连接..."
ssh -T git@github.com

if [ $? -eq 0 ]; then
    echo "✅ SSH连接成功！"
    
    # 切换到SSH远程
    cd /Users/yyp/.openclaw/workspace/data-asset-platform
    git remote set-url origin git@github.com:YYPing/data-asset-platform.git
    
    echo ""
    echo "🚀 准备推送到GitHub..."
    echo "当前提交:"
    git log --oneline -3
    
    read -p "是否立即推送到GitHub? (y/n): " push_confirm
    if [ "$push_confirm" = "y" ] || [ "$push_confirm" = "Y" ]; then
        echo "正在推送..."
        git push origin main
        
        if [ $? -eq 0 ]; then
            echo "🎉 代码已成功推送到GitHub!"
            echo "仓库地址: https://github.com/YYPing/data-asset-platform"
        else
            echo "❌ 推送失败，请检查错误信息"
        fi
    else
        echo "⏸️  推送已取消"
        echo "手动推送命令: git push origin main"
    fi
else
    echo "❌ SSH连接失败"
    echo "请检查:"
    echo "1. 密钥是否正确"
    echo "2. 公钥是否已添加到GitHub"
    echo "3. 网络连接是否正常"
fi

echo ""
echo "📋 有用的命令:"
echo "查看SSH密钥指纹: ssh-keygen -lf ~/.ssh/id_rsa"
echo "测试GitHub连接: ssh -T git@github.com"
echo "查看Git远程: git remote -v"
echo "推送代码: git push origin main"