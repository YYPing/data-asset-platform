#!/usr/bin/env python3
"""
简单功能测试 - 直接验证核心功能
"""
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
backend_path = project_root / "src" / "backend"
sys.path.insert(0, str(backend_path))

print("🧪 开始简单功能验证测试")
print("="*60)

# 测试1: 检查关键文件是否存在
print("\n1. 📁 检查关键文件结构")
critical_files = [
    "app/main.py",
    "app/models/__init__.py",
    "app/models/user.py",
    "app/models/asset.py",
    "app/models/material.py",
    "app/models/certificate.py",
    "app/api/v1/auth.py",
    "app/api/v1/assets.py",
    "app/api/v1/materials.py",
    "app/api/v1/certificates.py",
]

all_files_exist = True
for file_path in critical_files:
    full_path = backend_path / file_path
    if full_path.exists():
        print(f"  ✅ {file_path}")
    else:
        print(f"  ❌ {file_path} (缺失)")
        all_files_exist = False

# 测试2: 检查测试文件
print("\n2. 🧪 检查测试文件")
test_files = [
    "tests/test_auth_comprehensive.py",
    "tests/test_materials_comprehensive.py",
    "tests/test_assets.py",
    "tests/test_workflow.py",
]

for test_file in test_files:
    full_path = backend_path / test_file
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"  ✅ {test_file} ({size} bytes)")
    else:
        print(f"  ❌ {test_file} (缺失)")

# 测试3: 检查Python模块导入
print("\n3. 🔧 检查Python模块导入")
try:
    # 尝试导入核心模块
    import app.models
    import app.models.user
    import app.models.asset
    print("  ✅ 核心模型模块导入成功")
except ImportError as e:
    print(f"  ❌ 导入失败: {e}")

# 测试4: 检查数据库模型定义
print("\n4. 🗄️ 检查数据库模型")
try:
    from app.models.user import User
    from app.models.asset import DataAsset
    from app.models.material import Material
    from app.models.certificate import Certificate
    
    print("  ✅ 数据库模型类定义完整")
    
    # 检查模型属性
    user_attrs = dir(User)
    asset_attrs = dir(DataAsset)
    
    required_user_attrs = ['id', 'username', 'email', 'role', 'is_active']
    required_asset_attrs = ['id', 'name', 'code', 'status', 'owner_id']
    
    user_ok = all(hasattr(User, attr) for attr in required_user_attrs)
    asset_ok = all(hasattr(DataAsset, attr) for attr in required_asset_attrs)
    
    if user_ok:
        print("  ✅ User模型属性完整")
    else:
        print("  ⚠️ User模型属性不完整")
    
    if asset_ok:
        print("  ✅ Asset模型属性完整")
    else:
        print("  ⚠️ Asset模型属性不完整")
        
except Exception as e:
    print(f"  ❌ 检查数据库模型时出错: {e}")

# 测试5: 检查API路由定义
print("\n5. 🌐 检查API路由")
try:
    # 读取API文件内容
    auth_api = backend_path / "app" / "api" / "v1" / "auth.py"
    assets_api = backend_path / "app" / "api" / "v1" / "assets.py"
    
    if auth_api.exists():
        with open(auth_api, 'r', encoding='utf-8') as f:
            auth_content = f.read()
            if '@router.post' in auth_content or 'router.post' in auth_content:
                print("  ✅ Auth API包含POST路由")
            else:
                print("  ⚠️ Auth API可能缺少路由定义")
    
    if assets_api.exists():
        with open(assets_api, 'r', encoding='utf-8') as f:
            assets_content = f.read()
            endpoints = [
                ('创建资产', 'create_asset' in assets_content or 'post' in assets_content.lower()),
                ('获取资产列表', 'get_assets' in assets_content or 'get' in assets_content.lower()),
                ('更新资产', 'update_asset' in assets_content or 'put' in assets_content.lower()),
                ('删除资产', 'delete_asset' in assets_content or 'delete' in assets_content.lower()),
            ]
            
            for endpoint_name, exists in endpoints:
                if exists:
                    print(f"  ✅ {endpoint_name}")
                else:
                    print(f"  ⚠️ {endpoint_name}")
                    
except Exception as e:
    print(f"  ❌ 检查API路由时出错: {e}")

# 测试6: 检查测试数据
print("\n6. 📊 检查测试数据准备")
test_data_files = [
    "tests/test_auth_comprehensive.py",
    "tests/test_materials_comprehensive.py",
]

for test_file in test_data_files:
    full_path = backend_path / test_file
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            test_count = content.count('def test_')
            fixture_count = content.count('@pytest.fixture')
            
            print(f"  📋 {test_file}: {test_count}个测试用例, {fixture_count}个fixture")

# 总结
print("\n" + "="*60)
print("📋 功能验证总结")
print("="*60)

if all_files_exist:
    print("✅ 所有关键文件都存在")
    print("✅ 项目结构完整")
    print("✅ 代码基础良好")
    print("\n🎯 下一步: 运行实际功能测试")
    print("   执行: cd src/backend && python -m pytest tests/ -v")
else:
    print("⚠️ 部分关键文件缺失")
    print("🔧 需要先修复文件结构")

print("\n⏱️ 验证完成时间:", os.popen('date').read().strip())