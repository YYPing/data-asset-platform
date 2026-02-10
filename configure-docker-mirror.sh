#!/bin/bash
# Docker镜像加速配置脚本

echo "配置Docker镜像加速..."
echo ""

# 检查Docker Desktop配置目录
DOCKER_CONFIG="$HOME/.docker/daemon.json"

if [ -f "$DOCKER_CONFIG" ]; then
    echo "备份现有配置..."
    cp "$DOCKER_CONFIG" "$DOCKER_CONFIG.backup"
fi

# 写入镜像配置
cat > "$DOCKER_CONFIG" << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

echo "✅ 配置已写入: $DOCKER_CONFIG"
echo ""
echo "请重启Docker Desktop使配置生效："
echo "  1. 点击菜单栏的Docker图标"
echo "  2. 选择 'Restart'"
echo ""
echo "或者运行: killall Docker && open -a Docker"
