#!/usr/bin/env python3
"""
快速测试验证脚本
验证测试环境是否正常工作
"""
import sys
import os

# 添加后端目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src/backend"))

def check_imports():
    """检查必要的导入"""
    print("🔍 检查Python导入...")
    
    imports_to_check = [
        ("pytest", "测试框架"),
        ("fastapi", "Web框架"),
        ("sqlalchemy", "ORM"),
        ("aiosqlite", "异步SQLite"),
    ]
    
    all_ok = True
    for module_name, description in imports_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {description} ({module_name})")
        except ImportError as e:
            print(f"  ❌ {description} ({module_name}): {e}")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    paths_to_check = [
        ("src/backend/app", "后端应用目录"),
        ("src/backend/app/models", "数据模型目录"),
        ("src/backend/app/api/v1", "API路由目录"),
        ("src/backend/tests", "测试目录"),
        ("src/frontend/src", "前端源码目录"),
    ]
    
    all_ok = True
    for path, description in paths_to_check:
        full_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(full_path):
            print(f"  ✅ {description}: {path}")
        else:
            print(f"  ❌ {description}: {path} (不存在)")
            all_ok = False
    
    return all_ok

def check_test_files():
    """检查测试文件"""
    print("\n🧪 检查测试文件...")
    
    test_files = [
        "tests/test_auth.py",
        "tests/test_assets.py",
        "tests/test_workflow.py",
        "tests/test_auth_comprehensive.py",
        "tests/test_config.py",
        "tests/test_db.py",
        "tests/test_client.py",
    ]
    
    all_ok = True
    for test_file in test_files:
        full_path = os.path.join(os.path.dirname(__file__), "src/backend", test_file)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"  ✅ {test_file} ({size} bytes)")
        else:
            print(f"  ❌ {test_file} (不存在)")
            all_ok = False
    
    return all_ok

def check_test_data():
    """检查测试数据"""
    print("\n📊 检查测试数据...")
    
    # 读取测试配置文件
    test_config_path = os.path.join(os.path.dirname(__file__), "src/backend/tests/test_config.py")
    if os.path.exists(test_config_path):
        with open(test_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            config_lines = len(content.split('\n'))
            print(f"  ✅ 测试配置文件: {config_lines} 行")
    else:
        print(f"  ❌ 测试配置文件不存在")
        return False
    
    # 读取测试数据库工具
    test_db_path = os.path.join(os.path.dirname(__file__), "src/backend/tests/test_db.py")
    if os.path.exists(test_db_path):
        with open(test_db_path, 'r', encoding='utf-8') as f:
            content = f.read()
            db_lines = len(content.split('\n'))
            print(f"  ✅ 测试数据库工具: {db_lines} 行")
    else:
        print(f"  ❌ 测试数据库工具不存在")
        return False
    
    # 读取测试客户端工具
    test_client_path = os.path.join(os.path.dirname(__file__), "src/backend/tests/test_client.py")
    if os.path.exists(test_client_path):
        with open(test_client_path, 'r', encoding='utf-8') as f:
            content = f.read()
            client_lines = len(content.split('\n'))
            print(f"  ✅ 测试客户端工具: {client_lines} 行")
    else:
        print(f"  ❌ 测试客户端工具不存在")
        return False
    
    return True

def check_auth_tests():
    """检查认证测试"""
    print("\n🔐 检查认证测试...")
    
    test_auth_path = os.path.join(os.path.dirname(__file__), "src/backend/tests/test_auth_comprehensive.py")
    if os.path.exists(test_auth_path):
        with open(test_auth_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 统计测试用例
            test_cases = content.count('def test_')
            lines = len(content.split('\n'))
            
            print(f"  ✅ 认证测试文件: {lines} 行")
            print(f"  ✅ 测试用例数量: {test_cases} 个")
            
            # 提取测试用例名称
            import re
            test_names = re.findall(r'def (test_[a-zA-Z0-9_]+)', content)
            print(f"  ✅ 测试用例列表:")
            for i, name in enumerate(test_names[:10], 1):  # 显示前10个
                print(f"     {i:2d}. {name}")
            
            if len(test_names) > 10:
                print(f"     ... 还有 {len(test_names) - 10} 个测试用例")
            
            return True
    else:
        print(f"  ❌ 认证测试文件不存在")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("数据资产平台测试环境验证")
    print("=" * 60)
    
    checks = [
        ("项目结构", check_project_structure),
        ("测试文件", check_test_files),
        ("测试数据", check_test_data),
        ("认证测试", check_auth_tests),
        ("Python导入", check_imports),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 检查: {check_name}")
        print("-" * 40)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ❌ 检查失败: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status}: {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有检查通过！测试环境准备就绪。")
        print("\n下一步:")
        print("  1. 安装测试依赖: pip install pytest pytest-asyncio")
        print("  2. 运行测试: pytest src/backend/tests/ -v")
        print("  3. 查看测试报告")
    else:
        print("⚠️  部分检查未通过，需要修复。")
        print("\n建议:")
        print("  1. 安装缺失的Python包")
        print("  2. 检查项目文件结构")
        print("  3. 重新运行验证")
    
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())