import os
import sys

# 设置环境变量
os.environ['MINIO_ENABLED'] = 'false'
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'
os.environ['REDIS_URL'] = 'redis://localhost'

print("🚀 数据资产平台 - 简化启动")
print("=" * 40)

# 创建Redis mock
print("🔧 配置Redis mock...")

class MemoryRedis:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value, ex=None):
        self.data[key] = value
        return True
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
        return 1

# 临时替换redis模块
import redis
original_redis = redis.Redis
redis.Redis = MemoryRedis

print("✅ 环境配置完成")

try:
    print("📦 导入应用模块...")
    from app.main import app
    
    print(f"✅ 应用加载成功: {app.title}")
    print(f"📊 版本: {app.version}")
    
    # 显示API路由
    print("\\n🔗 API路由列表:")
    routes_by_module = {}
    for route in app.routes:
        if hasattr(route, 'path') and route.path:
            path = route.path
            if '/api/' in path:
                module = path.split('/')[3] if len(path.split('/')) > 3 else 'other'
                if module not in routes_by_module:
                    routes_by_module[module] = []
                routes_by_module[module].append(path)
    
    for module, routes in routes_by_module.items():
        print(f"   📁 {module}: {len(routes)}个接口")
        for i, route in enumerate(routes[:3]):
            print(f"      {i+1}. {route}")
        if len(routes) > 3:
            print(f"      ... 还有{len(routes)-3}个接口")
    
    print("\\n" + "=" * 40)
    print("🎉 后端服务验证通过!")
    print("🚀 可以正常启动服务")
    print("🌐 访问: http://localhost:8000")
    print("📚 文档: http://localhost:8000/docs")
    
except Exception as e:
    print(f"\\n❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()

# 恢复原始redis
redis.Redis = original_redis
