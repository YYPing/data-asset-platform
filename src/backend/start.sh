#!/bin/bash

echo "🚀 数据资产平台 - 后端服务启动"
echo "================================"

# 设置环境变量
export MINIO_ENABLED=false
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export REDIS_URL=""
export DEBUG=true

echo "🔧 环境配置:"
echo "   数据库: SQLite内存模式"
echo "   MinIO: 禁用 (使用mock)"
echo "   Redis: 内存模式"
echo "   调试模式: 启用"

echo ""
echo "📦 检查应用导入..."
python3 -c "
import os
print('正在导入应用...')
try:
    from app.main import app
    print(f'✅ 应用: {app.title}')
    print(f'📊 版本: {app.version}')
    
    # 统计路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and route.path:
            routes.append(route.path)
    
    api_routes = [r for r in routes if '/api/' in r]
    print(f'🔗 API路由: {len(api_routes)}个')
    
    # 按模块统计
    modules = {}
    for route in api_routes:
        parts = route.split('/')
        if len(parts) > 3:
            module = parts[3]
            if module not in modules:
                modules[module] = 0
            modules[module] += 1
    
    print('📁 功能模块:')
    for module, count in sorted(modules.items()):
        print(f'   • {module}: {count}个接口')
    
    print('\\n🎉 应用检查通过，可以启动!')
    
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

echo ""
echo "================================"
echo "🚀 启动FastAPI服务..."
echo "🌐 访问地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo "🔑 测试账号: admin / Admin@123456"
echo "================================"

# 启动服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
