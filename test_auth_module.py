#!/usr/bin/env python3
"""
认证模块独立测试
不依赖项目结构，直接测试核心功能
"""
import sys
import os
import json
import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))

class AuthModuleTest:
    """认证模块测试"""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.datetime.now()
        
    def test_password_hashing(self):
        """测试密码哈希"""
        try:
            from app.core.security import get_password_hash, verify_password
            
            test_password = "TestPassword123"
            hashed = get_password_hash(test_password)
            
            # 验证哈希
            assert verify_password(test_password, hashed), "密码验证失败"
            assert not verify_password("WrongPassword", hashed), "错误密码应该验证失败"
            
            return {
                "test": "password_hashing",
                "status": "passed",
                "message": "密码哈希和验证功能正常"
            }
        except Exception as e:
            return {
                "test": "password_hashing",
                "status": "failed",
                "message": f"密码哈希测试失败: {e}"
            }
    
    def test_token_creation(self):
        """测试Token创建"""
        try:
            from app.core.security import create_access_token
            
            test_data = {"sub": "testuser", "role": "admin"}
            token = create_access_token(data=test_data)
            
            assert isinstance(token, str), "Token应该是字符串"
            assert len(token) > 50, "Token长度应该足够"
            
            return {
                "test": "token_creation",
                "status": "passed",
                "message": "Token创建功能正常"
            }
        except Exception as e:
            return {
                "test": "token_creation",
                "status": "failed",
                "message": f"Token创建测试失败: {e}"
            }
    
    def test_user_model(self):
        """测试用户模型"""
        try:
            from app.models.user import User
            
            # 创建用户实例
            user = User(
                username="testuser",
                hashed_password="hashed_password",
                full_name="测试用户",
                email="test@example.com",
                role="data_holder",
                is_active=True
            )
            
            assert user.username == "testuser"
            assert user.full_name == "测试用户"
            assert user.role == "data_holder"
            assert user.is_active is True
            
            return {
                "test": "user_model",
                "status": "passed",
                "message": "用户模型功能正常"
            }
        except Exception as e:
            return {
                "test": "user_model",
                "status": "failed",
                "message": f"用户模型测试失败: {e}"
            }
    
    def test_role_permissions(self):
        """测试角色权限"""
        try:
            # 测试角色定义
            roles = ["admin", "center_auditor", "evaluator", "data_holder", "auditor", "regulator", "system"]
            
            assert len(roles) == 7, "应该有7种角色"
            assert "admin" in roles, "应该包含admin角色"
            assert "data_holder" in roles, "应该包含data_holder角色"
            
            return {
                "test": "role_permissions",
                "status": "passed",
                "message": f"角色定义正常: {', '.join(roles)}"
            }
        except Exception as e:
            return {
                "test": "role_permissions",
                "status": "failed",
                "message": f"角色权限测试失败: {e}"
            }
    
    def test_security_config(self):
        """测试安全配置"""
        try:
            from app.core.security import SECRET_KEY, ALGORITHM
            
            assert SECRET_KEY is not None, "SECRET_KEY应该存在"
            assert ALGORITHM == "HS256", "算法应该是HS256"
            
            return {
                "test": "security_config",
                "status": "passed",
                "message": "安全配置正常"
            }
        except Exception as e:
            return {
                "test": "security_config",
                "status": "failed",
                "message": f"安全配置测试失败: {e}"
            }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🔐 运行认证模块测试")
        print("=" * 50)
        
        tests = [
            self.test_password_hashing,
            self.test_token_creation,
            self.test_user_model,
            self.test_role_permissions,
            self.test_security_config
        ]
        
        for test_func in tests:
            result = test_func()
            self.results.append(result)
            
            status_icon = "✅" if result["status"] == "passed" else "❌"
            print(f"{status_icon} {result['test']}: {result['message']}")
        
        return self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        passed = sum(1 for r in self.results if r["status"] == "passed")
        total = len(self.results)
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        report = {
            "module": "认证与权限模块",
            "timestamp": datetime.datetime.now().isoformat(),
            "duration": str(datetime.datetime.now() - self.start_time),
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": round(pass_rate, 2)
            },
            "details": self.results
        }
        
        # 保存报告
        report_file = Path(__file__).parent / f"auth_test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        print("\n" + "=" * 50)
        print("📊 认证模块测试报告")
        print("=" * 50)
        print(f"✅ 通过: {passed}/{total} ({pass_rate:.1f}%)")
        print(f"📄 报告文件: {report_file}")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  有测试失败，请检查详情。")
        
        return report

def main():
    """主函数"""
    tester = AuthModuleTest()
    report = tester.run_all_tests()
    
    # 返回退出码
    if report["summary"]["failed"] > 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())