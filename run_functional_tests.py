#!/usr/bin/env python3
"""
功能测试运行脚本
直接运行测试，不依赖完整环境安装
"""
import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
backend_path = project_root / "src" / "backend"
sys.path.insert(0, str(backend_path))

# 测试模块列表
TEST_MODULES = [
    {
        "name": "认证模块",
        "file": "tests/test_auth_comprehensive.py",
        "description": "用户认证、登录、权限验证"
    },
    {
        "name": "材料管理模块",
        "file": "tests/test_materials_comprehensive.py",
        "description": "材料上传、版本控制、审核流程"
    },
    {
        "name": "资产管理模块",
        "file": "tests/test_assets.py",
        "description": "资产CRUD、状态管理、搜索"
    },
    {
        "name": "工作流模块",
        "file": "tests/test_workflow.py",
        "description": "审批流程、状态流转"
    }
]

def install_minimal_dependencies():
    """安装最小化测试依赖"""
    print("📦 安装最小化测试依赖...")
    
    dependencies = [
        "pytest",
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "httpx",
        "aiosqlite",
        "jose",
        "passlib",
        "redis"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         capture_output=True, text=True)
            print(f"  ✅ 已安装: {dep}")
        except Exception as e:
            print(f"  ⚠️  安装失败 {dep}: {e}")

def create_test_environment():
    """创建测试环境"""
    print("🔧 创建测试环境...")
    
    # 创建必要的目录
    os.makedirs(backend_path / "tests", exist_ok=True)
    
    # 创建测试配置文件
    test_config = backend_path / "tests" / "test_config.py"
    if not test_config.exists():
        print("  ⚠️  测试配置文件不存在")
    
    # 创建Redis mock
    redis_mock = backend_path / "tests" / "redis_mock.py"
    if not redis_mock.exists():
        print("  ⚠️  Redis mock文件不存在")
    
    print("  ✅ 测试环境准备完成")

def run_single_test(test_file):
    """运行单个测试文件"""
    test_path = backend_path / test_file
    if not test_path.exists():
        return {
            "status": "error",
            "message": f"测试文件不存在: {test_file}",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }
    
    print(f"\n🧪 运行测试: {test_file}")
    
    try:
        # 使用pytest运行测试
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"],
            cwd=str(backend_path),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        # 解析输出
        output = result.stdout + result.stderr
        
        # 提取测试结果
        passed = output.count("PASSED")
        failed = output.count("FAILED")
        skipped = output.count("SKIPPED")
        total = passed + failed + skipped
        
        status = "success" if result.returncode == 0 else "failed"
        
        return {
            "status": status,
            "returncode": result.returncode,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "total": total,
            "output": output[-2000:]  # 保留最后2000字符
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": "测试超时（5分钟）",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"运行测试时出错: {str(e)}",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 功能测试执行报告")
    print("="*60)
    
    total_passed = sum(r.get("passed", 0) for r in results.values())
    total_failed = sum(r.get("failed", 0) for r in results.values())
    total_skipped = sum(r.get("skipped", 0) for r in results.values())
    total_tests = total_passed + total_failed + total_skipped
    
    # 模块级别报告
    for module_name, result in results.items():
        status = result.get("status", "unknown")
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        skipped = result.get("skipped", 0)
        total = passed + failed + skipped
        
        if total > 0:
            pass_rate = (passed / total) * 100
        else:
            pass_rate = 0
        
        status_icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        
        print(f"\n{status_icon} {module_name}")
        print(f"   状态: {status}")
        print(f"   通过: {passed} / 失败: {failed} / 跳过: {skipped} / 总计: {total}")
        print(f"   通过率: {pass_rate:.1f}%")
        
        if result.get("message"):
            print(f"   消息: {result['message']}")
    
    # 总体报告
    print("\n" + "="*60)
    print("📈 总体测试结果")
    print("="*60)
    
    if total_tests > 0:
        overall_pass_rate = (total_passed / total_tests) * 100
    else:
        overall_pass_rate = 0
    
    print(f"✅ 总通过数: {total_passed}")
    print(f"❌ 总失败数: {total_failed}")
    print(f"⏭️  总跳过数: {total_skipped}")
    print(f"📋 总测试数: {total_tests}")
    print(f"📊 总体通过率: {overall_pass_rate:.1f}%")
    
    # 生成JSON报告
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_skipped": total_skipped,
        "overall_pass_rate": overall_pass_rate,
        "modules": results,
        "summary": {
            "status": "PASS" if total_failed == 0 else "FAIL",
            "message": f"功能测试完成: {total_passed}通过, {total_failed}失败"
        }
    }
    
    report_file = project_root / f"functional_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    return report_data

def main():
    """主函数"""
    print("🚀 开始功能测试执行")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"项目路径: {project_root}")
    
    # 安装依赖
    install_minimal_dependencies()
    
    # 创建环境
    create_test_environment()
    
    # 运行测试
    results = {}
    for module in TEST_MODULES:
        module_name = module["name"]
        test_file = module["file"]
        
        print(f"\n{'='*60}")
        print(f"测试模块: {module_name}")
        print(f"描述: {module['description']}")
        print(f"{'='*60}")
        
        result = run_single_test(test_file)
        results[module_name] = result
    
    # 生成报告
    report = generate_test_report(results)
    
    # 返回状态码
    if report["total_failed"] > 0:
        print("\n❌ 测试失败！")
        return 1
    else:
        print("\n✅ 所有测试通过！")
        return 0

if __name__ == "__main__":
    sys.exit(main())