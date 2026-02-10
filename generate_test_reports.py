#!/usr/bin/env python3
"""
生成模块测试报告
分析测试文件并生成报告，不实际运行测试
"""
import os
import sys
import json
import datetime
from pathlib import Path
import re

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "src" / "backend"

# 模块定义
MODULES = {
    "auth": {
        "name": "认证与权限模块",
        "description": "用户注册、登录、Token验证、权限控制、安全功能",
        "test_files": ["tests/test_auth.py", "tests/test_auth_comprehensive.py"],
        "source_dirs": ["app/core/", "app/models/user.py", "app/api/v1/auth.py", "app/services/auth.py"]
    },
    "assets": {
        "name": "数据资产管理模块",
        "description": "资产CRUD、版本控制、状态流转、搜索功能、审计日志",
        "test_files": ["tests/test_assets.py"],
        "source_dirs": ["app/models/asset.py", "app/api/v1/assets.py", "app/services/asset.py", "app/utils/search.py", "app/utils/audit.py"]
    },
    "workflow": {
        "name": "工作流管理模块",
        "description": "审批流程、任务分配、状态机管理、通知提醒",
        "test_files": ["tests/test_workflow.py"],
        "source_dirs": ["app/models/workflow.py", "app/api/v1/workflow.py", "app/services/workflow.py"]
    },
    "materials": {
        "name": "材料管理模块",
        "description": "材料上传、哈希存证、版本管理、MinIO集成",
        "test_files": ["tests/test_materials.py"],
        "source_dirs": ["app/models/material.py", "app/api/v1/materials.py", "app/services/material.py", "app/utils/minio_client.py", "app/utils/file_hash.py"]
    },
    "certificates": {
        "name": "证书管理模块",
        "description": "证书导入、OCR识别、有效期管理、证书验证",
        "test_files": ["tests/test_certificates.py"],
        "source_dirs": ["app/models/certificate.py", "app/api/v1/certificates.py", "app/services/certificate.py", "app/utils/ocr_processor.py", "app/utils/certificate_parser.py", "app/utils/expiry_manager.py", "app/utils/certificate_validator.py"]
    }
}

class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.reports = {}
        
    def analyze_test_file(self, file_path: Path) -> dict:
        """分析测试文件"""
        if not file_path.exists():
            return {
                "status": "missing",
                "message": "测试文件不存在"
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统计信息
            lines = len(content.split('\n'))
            size_kb = os.path.getsize(file_path) / 1024
            
            # 提取测试用例
            test_cases = re.findall(r'def (test_[a-zA-Z0-9_]+)', content)
            
            # 提取测试类
            test_classes = re.findall(r'class (Test[A-Za-z0-9_]+)', content)
            
            return {
                "status": "exists",
                "lines": lines,
                "size_kb": round(size_kb, 2),
                "test_cases": test_cases,
                "test_classes": test_classes,
                "test_case_count": len(test_cases),
                "test_class_count": len(test_classes)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def analyze_source_files(self, module_name: str, source_dirs: list) -> dict:
        """分析源代码文件"""
        source_files = []
        total_lines = 0
        total_size_kb = 0
        
        for source_path in source_dirs:
            full_path = BACKEND_DIR / source_path
            
            if full_path.is_file():
                # 单个文件
                if full_path.exists():
                    lines = len(open(full_path, 'r', encoding='utf-8').read().split('\n'))
                    size_kb = os.path.getsize(full_path) / 1024
                    
                    source_files.append({
                        "path": source_path,
                        "lines": lines,
                        "size_kb": round(size_kb, 2),
                        "type": "file"
                    })
                    
                    total_lines += lines
                    total_size_kb += size_kb
            elif full_path.is_dir():
                # 目录
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = Path(root) / file
                            rel_path = file_path.relative_to(BACKEND_DIR)
                            
                            lines = len(open(file_path, 'r', encoding='utf-8').read().split('\n'))
                            size_kb = os.path.getsize(file_path) / 1024
                            
                            source_files.append({
                                "path": str(rel_path),
                                "lines": lines,
                                "size_kb": round(size_kb, 2),
                                "type": "file"
                            })
                            
                            total_lines += lines
                            total_size_kb += size_kb
        
        return {
            "source_files": source_files,
            "total_files": len(source_files),
            "total_lines": total_lines,
            "total_size_kb": round(total_size_kb, 2)
        }
    
    def generate_module_report(self, module_name: str, module_config: dict) -> dict:
        """生成模块报告"""
        print(f"\n📋 分析模块: {module_config['name']}")
        print(f"  描述: {module_config['description']}")
        
        # 分析测试文件
        test_files_analysis = {}
        total_test_cases = 0
        
        for test_file in module_config['test_files']:
            analysis = self.analyze_test_file(BACKEND_DIR / test_file)
            test_files_analysis[test_file] = analysis
            
            if analysis["status"] == "exists":
                total_test_cases += analysis.get("test_case_count", 0)
        
        # 分析源代码文件
        source_analysis = self.analyze_source_files(module_name, module_config['source_dirs'])
        
        # 计算测试覆盖率（估算）
        test_coverage = 0
        if source_analysis["total_lines"] > 0:
            # 简单估算：每个测试用例覆盖约50行代码
            estimated_coverage = (total_test_cases * 50) / source_analysis["total_lines"] * 100
            test_coverage = min(round(estimated_coverage, 1), 100)
        
        report = {
            "module_name": module_config["name"],
            "description": module_config["description"],
            "analysis_time": datetime.datetime.now().isoformat(),
            "test_files": test_files_analysis,
            "source_files": source_analysis,
            "summary": {
                "test_file_count": len(test_files_analysis),
                "total_test_cases": total_test_cases,
                "source_file_count": source_analysis["total_files"],
                "source_lines": source_analysis["total_lines"],
                "estimated_test_coverage": test_coverage,
                "status": "analyzed"
            }
        }
        
        # 打印摘要
        print(f"  测试文件: {len(test_files_analysis)} 个")
        print(f"  测试用例: {total_test_cases} 个")
        print(f"  源代码文件: {source_analysis['total_files']} 个")
        print(f"  源代码行数: {source_analysis['total_lines']} 行")
        print(f"  估算测试覆盖率: {test_coverage}%")
        
        return report
    
    def generate_all_reports(self):
        """生成所有模块报告"""
        print("🚀 开始生成数据资产平台测试报告")
        print(f"📅 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        for module_name, module_config in MODULES.items():
            report = self.generate_module_report(module_name, module_config)
            self.reports[module_name] = report
        
        # 生成总体报告
        self.generate_overall_report()
        
        return self.reports
    
    def generate_overall_report(self):
        """生成总体报告"""
        print("\n" + "=" * 60)
        print("📊 总体测试分析报告")
        print("=" * 60)
        
        # 计算总体统计
        total_modules = len(self.reports)
        total_test_files = 0
        total_test_cases = 0
        total_source_files = 0
        total_source_lines = 0
        
        for module_report in self.reports.values():
            total_test_files += module_report["summary"]["test_file_count"]
            total_test_cases += module_report["summary"]["total_test_cases"]
            total_source_files += module_report["summary"]["source_file_count"]
            total_source_lines += module_report["summary"]["source_lines"]
        
        # 计算平均覆盖率
        avg_coverage = sum(r["summary"]["estimated_test_coverage"] for r in self.reports.values()) / total_modules
        
        # 生成报告数据
        overall_report = {
            "project": "数据资产全流程管理平台",
            "report_date": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": str(datetime.datetime.now() - self.start_time),
            "summary": {
                "total_modules": total_modules,
                "total_test_files": total_test_files,
                "total_test_cases": total_test_cases,
                "total_source_files": total_source_files,
                "total_source_lines": total_source_lines,
                "average_test_coverage": round(avg_coverage, 1)
            },
            "modules": self.reports
        }
        
        # 保存JSON报告
        json_report_file = PROJECT_ROOT / f"test_analysis_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(overall_report, f, ensure_ascii=False, indent=2)
        
        # 生成文本报告
        text_report_file = PROJECT_ROOT / f"test_analysis_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("数据资产平台测试分析报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"报告时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"分析时长: {datetime.datetime.now() - self.start_time}\n\n")
            
            f.write("📊 总体统计:\n")
            f.write(f"  测试模块数: {total_modules}\n")
            f.write(f"  测试文件数: {total_test_files}\n")
            f.write(f"  测试用例数: {total_test_cases}\n")
            f.write(f"  源代码文件数: {total_source_files}\n")
            f.write(f"  源代码行数: {total_source_lines}\n")
            f.write(f"  平均测试覆盖率: {avg_coverage:.1f}%\n\n")
            
            f.write("📋 模块详情:\n")
            for module_name, module_report in self.reports.items():
                f.write(f"\n  🔸 {module_report['module_name']}:\n")
                f.write(f"    描述: {module_report['description']}\n")
                f.write(f"    测试文件: {module_report['summary']['test_file_count']} 个\n")
                f.write(f"    测试用例: {module_report['summary']['total_test_cases']} 个\n")
                f.write(f"    源代码: {module_report['summary']['source_file_count']} 文件, {module_report['summary']['source_lines']} 行\n")
                f.write(f"    估算覆盖率: {module_report['summary']['estimated_test_coverage']}%\n")
                
                # 列出测试文件
                for test_file, analysis in module_report["test_files"].items():
                    if analysis["status"] == "exists":
                        f.write(f"    📄 {test_file}: {analysis.get('test_case_count', 0)} 个测试用例\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("报告结束\n")
            f.write("=" * 60 + "\n")
        
        # 打印总体结果
        print(f"✅ 测试模块: {total_modules}")
        print(f"✅ 测试文件: {total_test_files}")
        print(f"✅ 测试用例: {total_test_cases}")
        print(f"✅ 源代码文件: {total_source_files}")
        print(f"✅ 源代码行数: {total_source_lines}")
        print(f"✅ 平均测试覆盖率: {avg_coverage:.1f}%")
        
        print(f"\n📄 报告文件已生成:")
        print(f"  JSON报告: {json_report_file}")
        print(f"  文本报告: {text_report_file}")
        
        return overall_report

def main():
    """主函数"""
    generator = TestReportGenerator()
    
    try:
        reports = generator.generate_all_reports()
        
        print("\n🎉 测试分析报告生成完成！")
        return 0
        
    except Exception as e:
        print(f"\n🚨 报告生成异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())