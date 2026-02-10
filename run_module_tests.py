#!/usr/bin/env python3
"""
模块化测试运行脚本
按功能模块运行测试并生成报告
"""
import os
import sys
import subprocess
import json
import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "src" / "backend"

# 测试模块配置
TEST_MODULES = {
    "auth": {
        "name": "认证与权限模块",
        "test_files": ["tests/test_auth.py", "tests/test_auth_comprehensive.py"],
        "description": "用户注册、登录、Token验证、权限控制、安全功能",
        "expected_tests": 30
    },
    "assets": {
        "name": "数据资产管理模块",
        "test_files": ["tests/test_assets.py"],
        "description": "资产CRUD、版本控制、状态流转、搜索功能、审计日志",
        "expected_tests": 15
    },
    "workflow": {
        "name": "工作流管理模块",
        "test_files": ["tests/test_workflow.py"],
        "description": "审批流程、任务分配、状态机管理、通知提醒",
        "expected_tests": 10
    },
    "materials": {
        "name": "材料管理模块",
        "test_files": ["tests/test_materials.py"],
        "description": "材料上传、哈希存证、版本管理、MinIO集成",
        "expected_tests": 12
    },
    "certificates": {
        "name": "证书管理模块",
        "test_files": ["tests/test_certificates.py"],
        "description": "证书导入、OCR识别、有效期管理、证书验证",
        "expected_tests": 12
    }
}

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.datetime.now()
        
    def run_module_test(self, module_name: str, module_config: dict) -> dict:
        """运行单个模块测试"""
        print(f"\n{'='*60}")
        print(f"🧪 测试模块: {module_config['name']}")
        print(f"📝 描述: {module_config['description']}")
        print(f"{'='*60}")
        
        module_result = {
            "module_name": module_config["name"],
            "description": module_config["description"],
            "test_files": module_config["test_files"],
            "start_time": datetime.datetime.now().isoformat(),
            "results": {}
        }
        
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_tests = 0
        
        for test_file in module_config["test_files"]:
            test_file_path = BACKEND_DIR / test_file
            if not test_file_path.exists():
                print(f"⚠️  测试文件不存在: {test_file}")
                module_result["results"][test_file] = {
                    "status": "missing",
                    "message": "测试文件不存在"
                }
                continue
            
            print(f"\n📄 运行测试文件: {test_file}")
            
            # 运行pytest
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_file_path),
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=none"
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=str(BACKEND_DIR),
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
                errors = output.count("ERROR")
                
                total_passed += passed
                total_failed += failed
                total_skipped += skipped
                total_tests += (passed + failed + skipped + errors)
                
                module_result["results"][test_file] = {
                    "status": "completed",
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "errors": errors,
                    "return_code": result.returncode,
                    "summary": f"通过: {passed}, 失败: {failed}, 跳过: {skipped}, 错误: {errors}"
                }
                
                print(f"  ✅ 通过: {passed}, ❌ 失败: {failed}, ⚠️ 跳过: {skipped}, 🚨 错误: {errors}")
                
                # 如果有失败或错误，显示详细信息
                if failed > 0 or errors > 0:
                    print("\n🔍 失败/错误详情:")
                    for line in output.split('\n'):
                        if "FAILED" in line or "ERROR" in line:
                            print(f"  {line}")
                
            except subprocess.TimeoutExpired:
                print(f"  ⏰ 测试超时（5分钟）")
                module_result["results"][test_file] = {
                    "status": "timeout",
                    "message": "测试执行超时"
                }
            except Exception as e:
                print(f"  🚨 测试执行异常: {e}")
                module_result["results"][test_file] = {
                    "status": "error",
                    "message": str(e)
                }
        
        # 计算通过率
        if total_tests > 0:
            pass_rate = (total_passed / total_tests) * 100
        else:
            pass_rate = 0
        
        module_result.update({
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "pass_rate": round(pass_rate, 2),
            "end_time": datetime.datetime.now().isoformat(),
            "status": "completed" if total_failed == 0 else "has_failures"
        })
        
        print(f"\n📊 模块测试汇总:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过: {total_passed} ({pass_rate:.1f}%)")
        print(f"  失败: {total_failed}")
        print(f"  跳过: {total_skipped}")
        print(f"  状态: {'✅ 通过' if total_failed == 0 else '❌ 有失败'}")
        
        return module_result
    
    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'='*60}")
        print("📋 测试报告生成")
        print(f"{'='*60}")
        
        # 计算总体统计
        total_modules = len(self.results)
        completed_modules = sum(1 for r in self.results.values() if r["status"] == "completed")
        modules_with_failures = sum(1 for r in self.results.values() if r.get("total_failed", 0) > 0)
        
        total_tests = sum(r.get("total_tests", 0) for r in self.results.values())
        total_passed = sum(r.get("total_passed", 0) for r in self.results.values())
        total_failed = sum(r.get("total_failed", 0) for r in self.results.values())
        
        if total_tests > 0:
            overall_pass_rate = (total_passed / total_tests) * 100
        else:
            overall_pass_rate = 0
        
        # 生成报告文件
        report_data = {
            "project": "数据资产全流程管理平台",
            "test_date": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": str(datetime.datetime.now() - self.start_time),
            "summary": {
                "total_modules": total_modules,
                "completed_modules": completed_modules,
                "modules_with_failures": modules_with_failures,
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "overall_pass_rate": round(overall_pass_rate, 2)
            },
            "modules": self.results
        }
        
        # 保存JSON报告
        report_file = PROJECT_ROOT / f"test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # 生成文本报告
        text_report = PROJECT_ROOT / f"test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_report, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("数据资产平台功能测试报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"测试时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试时长: {datetime.datetime.now() - self.start_time}\n\n")
            
            f.write("📊 测试汇总:\n")
            f.write(f"  测试模块数: {total_modules}\n")
            f.write(f"  完成模块数: {completed_modules}\n")
            f.write(f"  有失败的模块: {modules_with_failures}\n")
            f.write(f"  总测试用例: {total_tests}\n")
            f.write(f"  通过用例: {total_passed}\n")
            f.write(f"  失败用例: {total_failed}\n")
            f.write(f"  总体通过率: {overall_pass_rate:.1f}%\n\n")
            
            f.write("📋 模块详情:\n")
            for module_name, module_result in self.results.items():
                f.write(f"\n  🔸 {module_result['module_name']}:\n")
                f.write(f"    描述: {module_result['description']}\n")
                f.write(f"    状态: {module_result['status']}\n")
                f.write(f"    测试数: {module_result.get('total_tests', 0)}\n")
                f.write(f"    通过数: {module_result.get('total_passed', 0)}\n")
                f.write(f"    失败数: {module_result.get('total_failed', 0)}\n")
                f.write(f"    通过率: {module_result.get('pass_rate', 0):.1f}%\n")
                
                for test_file, file_result in module_result.get('results', {}).items():
                    f.write(f"    📄 {test_file}: {file_result.get('summary', 'N/A')}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("报告结束\n")
            f.write("=" * 60 + "\n")
        
        print(f"\n📄 报告文件已生成:")
        print(f"  JSON报告: {report_file}")
        print(f"  文本报告: {text_report}")
        
        # 显示总体结果
        print(f"\n{'='*60}")
        print("🎯 总体测试结果")
        print(f"{'='*60}")
        print(f"✅ 测试模块: {completed_modules}/{total_modules}")
        print(f"✅ 总测试用例: {total_tests}")
        print(f"✅ 通过用例: {total_passed} ({overall_pass_rate:.1f}%)")
        print(f"❌ 失败用例: {total_failed}")
        
        if total_failed == 0:
            print(f"\n🎉 所有测试通过！")
        else:
            print(f"\n⚠️  有 {total_failed} 个测试用例失败，需要检查。")
        
        return report_data
    
    def run_all_modules(self):
        """运行所有模块测试"""
        print("🚀 开始数据资产平台功能测试")
        print(f"📅 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        for module_name, module_config in TEST_MODULES.items():
            module_result = self.run_module_test(module_name, module_config)
            self.results[module_name] = module_result
        
        # 生成报告
        report = self.generate_report()
        
        return report

def main():
    """主函数"""
    runner = TestRunner()
    
    try:
        report = runner.run_all_modules()
        
        # 返回退出码
        if report["summary"]["total_failed"] > 0:
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n🚨 测试运行异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())