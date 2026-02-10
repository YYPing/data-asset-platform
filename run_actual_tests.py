#!/usr/bin/env python3
"""
实际功能测试运行脚本
"""
import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
backend_path = project_root / "src" / "backend"

print("🚀 开始实际功能测试")
print("="*60)
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"项目路径: {project_root}")
print("="*60)

# 测试模块配置
TEST_MODULES = [
    {
        "name": "认证模块",
        "file": "tests/test_auth_comprehensive.py",
        "description": "用户认证、登录、权限验证",
        "expected_tests": 22
    },
    {
        "name": "材料管理模块",
        "file": "tests/test_materials_comprehensive.py",
        "description": "材料上传、版本控制、审核流程",
        "expected_tests": 18
    }
]

def run_pytest(test_file, module_name):
    """运行pytest测试"""
    print(f"\n🧪 测试模块: {module_name}")
    print(f"文件: {test_file}")
    print("-"*40)
    
    test_path = backend_path / test_file
    if not test_path.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return {
            "status": "error",
            "message": f"测试文件不存在: {test_file}",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }
    
    try:
        # 运行pytest
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--disable-warnings"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=str(backend_path),
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        # 输出结果
        print("\n📋 测试输出:")
        print("-"*40)
        
        # 提取关键信息
        output_lines = result.stdout.split('\n')
        test_results = []
        
        for line in output_lines:
            if "PASSED" in line or "FAILED" in line or "ERROR" in line or "SKIPPED" in line:
                print(f"  {line}")
                test_results.append(line)
            elif "test_" in line and ("PASSED" in line or "FAILED" in line):
                print(f"  {line}")
        
        # 统计结果
        passed = result.stdout.count("PASSED")
        failed = result.stdout.count("FAILED")
        skipped = result.stdout.count("SKIPPED")
        errors = result.stdout.count("ERROR")
        total = passed + failed + skipped + errors
        
        # 状态
        if result.returncode == 0:
            status = "success"
            status_icon = "✅"
        else:
            status = "failed"
            status_icon = "❌"
        
        print("-"*40)
        print(f"{status_icon} 测试完成: 通过={passed}, 失败={failed}, 跳过={skipped}, 错误={errors}, 总计={total}")
        
        return {
            "status": status,
            "returncode": result.returncode,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "total": total,
            "output": result.stdout[-1000:] + result.stderr[-1000:]  # 保留最后2000字符
        }
        
    except subprocess.TimeoutExpired:
        print("❌ 测试超时（5分钟）")
        return {
            "status": "timeout",
            "message": "测试超时（5分钟）",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }
    except Exception as e:
        print(f"❌ 运行测试时出错: {str(e)}")
        return {
            "status": "error",
            "message": f"运行测试时出错: {str(e)}",
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }

def generate_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("📊 功能测试执行报告")
    print("="*60)
    
    total_passed = sum(r.get("passed", 0) for r in results.values())
    total_failed = sum(r.get("failed", 0) for r in results.values())
    total_skipped = sum(r.get("skipped", 0) for r in results.values())
    total_errors = sum(r.get("errors", 0) for r in results.values())
    total_tests = total_passed + total_failed + total_skipped + total_errors
    
    # 模块级别报告
    for module_name, result in results.items():
        status = result.get("status", "unknown")
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        skipped = result.get("skipped", 0)
        errors = result.get("errors", 0)
        total = passed + failed + skipped + errors
        
        if total > 0:
            pass_rate = (passed / total) * 100
        else:
            pass_rate = 0
        
        status_icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        
        print(f"\n{status_icon} {module_name}")
        print(f"   状态: {status}")
        print(f"   通过: {passed} / 失败: {failed} / 跳过: {skipped} / 错误: {errors} / 总计: {total}")
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
    print(f"⚠️  总错误数: {total_errors}")
    print(f"📋 总测试数: {total_tests}")
    print(f"📊 总体通过率: {overall_pass_rate:.1f}%")
    
    # 测试质量评估
    print("\n" + "="*60)
    print("📈 测试质量评估")
    print("="*60)
    
    if total_tests == 0:
        print("❌ 未执行任何测试")
        quality = "poor"
    elif overall_pass_rate >= 90:
        print("✅ 优秀：通过率90%以上")
        quality = "excellent"
    elif overall_pass_rate >= 80:
        print("✅ 良好：通过率80%以上")
        quality = "good"
    elif overall_pass_rate >= 70:
        print("⚠️  一般：通过率70%以上")
        quality = "fair"
    elif overall_pass_rate >= 50:
        print("⚠️  较差：通过率50%以上")
        quality = "poor"
    else:
        print("❌ 很差：通过率低于50%")
        quality = "very_poor"
    
    # 生成JSON报告
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_skipped": total_skipped,
        "total_errors": total_errors,
        "overall_pass_rate": overall_pass_rate,
        "quality": quality,
        "modules": results,
        "summary": {
            "status": "PASS" if total_failed == 0 and total_errors == 0 else "FAIL",
            "message": f"功能测试完成: {total_passed}通过, {total_failed}失败, {total_errors}错误"
        }
    }
    
    report_file = project_root / f"actual_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存: {report_file}")
    
    return report_data

def main():
    """主函数"""
    # 运行测试
    results = {}
    for module in TEST_MODULES:
        module_name = module["name"]
        test_file = module["file"]
        
        result = run_pytest(test_file, module_name)
        results[module_name] = result
    
    # 生成报告
    report = generate_report(results)
    
    # 返回状态码
    if report["total_failed"] > 0 or report["total_errors"] > 0:
        print("\n❌ 测试失败或存在错误！")
        return 1
    else:
        print("\n✅ 所有测试通过！")
        return 0

if __name__ == "__main__":
    sys.exit(main())