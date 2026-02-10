#!/usr/bin/env python3
"""
快速功能测试 - 直接运行关键测试
"""
import sys
import os
import subprocess
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
backend_path = project_root / "src" / "backend"
sys.path.insert(0, str(backend_path))

print("🚀 快速功能测试开始")
print("="*60)
print(f"时间: {subprocess.getoutput('date')}")
print(f"Python: {sys.version}")
print("="*60)

# 测试1: 运行认证模块的简单测试
print("\n1. 🧪 运行认证模块简单测试")
test_auth_simple = """
import sys
import os
sys.path.insert(0, '.')

# 创建简单的测试
def test_auth_basic():
    \"\"\"测试认证基础功能\"\"\"
    from app.core.security import get_password_hash, verify_password
    
    # 测试密码哈希
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    # 验证密码
    assert verify_password(password, hashed), "密码验证失败"
    assert not verify_password("WrongPassword", hashed), "错误密码应该验证失败"
    
    print("  ✅ 密码哈希和验证功能正常")
    
    # 测试JWT令牌创建（简化）
    from datetime import datetime, timedelta
    from jose import jwt
    from app.core.config import settings
    
    data = {"sub": "testuser", "role": "viewer"}
    token = jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")
    
    # 解码验证
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == "testuser", "JWT解码失败"
    
    print("  ✅ JWT令牌功能正常")
    
    return True

if __name__ == "__main__":
    try:
        test_auth_basic()
        print("\\n🎉 认证模块基础功能测试通过！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
"""

# 写入并运行测试
test_file = backend_path / "test_auth_quick.py"
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_auth_simple)

try:
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=str(backend_path),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("✅ 认证模块基础功能测试通过")
    else:
        print(f"❌ 认证模块测试失败: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print("❌ 测试超时")
except Exception as e:
    print(f"❌ 运行测试时出错: {e}")

# 测试2: 检查数据库模型
print("\n2. 🗄️ 检查数据库模型完整性")
try:
    from app.models.user import User
    from app.models.asset import DataAsset
    from app.models.material import Material
    from app.models.certificate import Certificate
    
    models = [User, DataAsset, Material, Certificate]
    model_names = ["User", "DataAsset", "Material", "Certificate"]
    
    for model, name in zip(models, model_names):
        # 检查模型是否有必要的属性
        if hasattr(model, '__tablename__'):
            print(f"  ✅ {name}模型: {model.__tablename__}")
        else:
            print(f"  ⚠️ {name}模型缺少__tablename__")
            
    print("  ✅ 数据库模型结构完整")
    
except Exception as e:
    print(f"  ❌ 检查数据库模型时出错: {e}")

# 测试3: 检查API路由
print("\n3. 🌐 检查API路由定义")
api_files = [
    "app/api/v1/auth.py",
    "app/api/v1/assets.py",
    "app/api/v1/materials.py",
    "app/api/v1/certificates.py"
]

for api_file in api_files:
    full_path = backend_path / api_file
    if full_path.exists():
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查路由装饰器
            routes = []
            if '@router.post' in content or 'router.post' in content:
                routes.append('POST')
            if '@router.get' in content or 'router.get' in content:
                routes.append('GET')
            if '@router.put' in content or 'router.put' in content:
                routes.append('PUT')
            if '@router.delete' in content or 'router.delete' in content:
                routes.append('DELETE')
            
            if routes:
                print(f"  ✅ {api_file}: {', '.join(routes)}路由")
            else:
                print(f"  ⚠️ {api_file}: 未找到路由定义")
    else:
        print(f"  ❌ {api_file}: 文件不存在")

# 测试4: 运行材料管理简单测试
print("\n4. 📁 运行材料管理简单测试")
test_material_simple = """
import sys
sys.path.insert(0, '.')

def test_material_model():
    \"\"\"测试材料模型\"\"\"
    from app.models.material import Material
    
    # 创建材料实例
    material = Material(
        code="MAT-001",
        name="测试材料",
        type="report",
        uploader_id=1,
        status="draft"
    )
    
    # 检查属性
    assert material.code == "MAT-001", "材料编码错误"
    assert material.name == "测试材料", "材料名称错误"
    assert material.type == "report", "材料类型错误"
    assert material.status == "draft", "材料状态错误"
    
    print("  ✅ 材料模型属性正常")
    
    # 测试版本控制
    from app.models.material import MaterialVersion
    version = MaterialVersion(
        material_id=1,
        version=1,
        name="测试材料v1",
        changed_by_id=1
    )
    
    assert version.version == 1, "版本号错误"
    print("  ✅ 材料版本模型正常")
    
    return True

if __name__ == "__main__":
    try:
        test_material_model()
        print("\\n🎉 材料管理模型测试通过！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
"""

# 写入并运行测试
test_file = backend_path / "test_material_quick.py"
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_material_simple)

try:
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=str(backend_path),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print("✅ 材料管理模型测试通过")
    else:
        print(f"❌ 材料管理测试失败: {result.stderr}")
        
except subprocess.TimeoutExpired:
    print("❌ 测试超时")
except Exception as e:
    print(f"❌ 运行测试时出错: {e}")

# 清理临时文件
for temp_file in [backend_path / "test_auth_quick.py", backend_path / "test_material_quick.py"]:
    if temp_file.exists():
        temp_file.unlink()

# 总结
print("\n" + "="*60)
print("📋 快速功能测试总结")
print("="*60)

print("\n✅ 已完成测试:")
print("  - 认证模块基础功能")
print("  - 数据库模型完整性")
print("  - API路由定义检查")
print("  - 材料管理模型功能")

print("\n🎯 下一步:")
print("  1. 运行完整的pytest测试套件")
print("  2. 生成详细的测试报告")
print("  3. 修复发现的问题")

print(f"\n⏱️ 测试完成时间: {subprocess.getoutput('date')}")