"""
认证模块全面测试
测试用户认证、权限控制、安全功能等
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import get_password_hash
from .test_client import test_client_manager


class TestAuthComprehensive:
    """认证功能全面测试"""
    
    # ==================== 用户注册测试 ====================
    
    def test_register_success(self, client: TestClient, db_session: AsyncSession):
        """测试用户注册成功"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "password": "NewUser@123",
                "full_name": "新用户",
                "email": "newuser@example.com",
                "role": "data_holder",
                "organization": "测试公司"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data["data"]
        assert data["message"] == "用户注册成功"
    
    def test_register_duplicate_username(self, client: TestClient, db_session: AsyncSession):
        """测试重复用户名注册失败"""
        # 先创建一个用户
        response1 = client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicateuser",
                "password": "Password@123",
                "full_name": "重复用户",
                "email": "user1@example.com",
                "role": "data_holder",
                "organization": "测试公司"
            }
        )
        assert response1.status_code == 200
        
        # 尝试用相同用户名注册
        response2 = client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicateuser",
                "password": "Another@123",
                "full_name": "另一个用户",
                "email": "user2@example.com",
                "role": "data_holder",
                "organization": "另一公司"
            }
        )
        
        assert response2.status_code == 400
        data = response2.json()
        assert data["success"] is False
        assert "用户名已存在" in data["message"]
    
    def test_register_weak_password(self, client: TestClient):
        """测试弱密码注册失败"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "weakpassuser",
                "password": "123",  # 太短
                "full_name": "弱密码用户",
                "email": "weak@example.com",
                "role": "data_holder",
                "organization": "测试公司"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "密码" in data["message"] and "弱" in data["message"]
    
    # ==================== 用户登录测试 ====================
    
    def test_login_success(self, client: TestClient, db_session: AsyncSession):
        """测试正确的用户名密码登录"""
        # 使用测试客户端管理器的登录方法
        result = test_client_manager.login_user("admin", "Admin1234")
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient):
        """测试错误密码登录失败"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "用户名或密码错误" in data["message"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """测试不存在的用户登录失败"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "用户名或密码错误" in data["message"]
    
    # ==================== Token验证测试 ====================
    
    def test_token_validation(self, client: TestClient):
        """测试Token验证"""
        # 先登录获取Token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "Admin1234"
            }
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # 使用Token访问受保护端点
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == "admin"
        assert data["data"]["role"] == "admin"
    
    def test_invalid_token(self, client: TestClient):
        """测试无效Token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "认证令牌" in data["message"]
    
    def test_missing_token(self, client: TestClient):
        """测试缺少Token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "认证" in data["message"]
    
    # ==================== Token刷新测试 ====================
    
    def test_token_refresh(self, client: TestClient):
        """测试Token刷新"""
        # 先登录获取refresh_token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "Admin1234"
            }
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        refresh_token = token_data["refresh_token"]
        
        # 刷新Token
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )
        
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        assert "access_token" in refresh_data
        assert "refresh_token" in refresh_data
        assert refresh_data["token_type"] == "bearer"
    
    # ==================== 密码管理测试 ====================
    
    def test_change_password(self, client: TestClient):
        """测试修改密码"""
        # 使用holder用户测试
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "holder",
                "password": "Holder1234"
            }
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # 修改密码
        change_response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": "Holder1234",
                "new_password": "NewHolder@123"
            }
        )
        
        assert change_response.status_code == 200
        change_data = change_response.json()
        assert change_data["success"] is True
        assert "密码修改成功" in change_data["message"]
        
        # 用新密码登录测试
        new_login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "holder",
                "password": "NewHolder@123"
            }
        )
        
        assert new_login_response.status_code == 200
    
    def test_change_password_wrong_old(self, client: TestClient):
        """测试修改密码时旧密码错误"""
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "holder",
                "password": "Holder1234"
            }
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # 尝试用错误的旧密码修改
        change_response = client.post(
            "/api/v1/auth/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "old_password": "WrongOldPassword",
                "new_password": "NewPassword@123"
            }
        )
        
        assert change_response.status_code == 400
        change_data = change_response.json()
        assert change_data["success"] is False
        assert "旧密码错误" in change_data["message"]
    
    # ==================== 权限测试 ====================
    
    def test_admin_permissions(self, client: TestClient):
        """测试管理员权限"""
        # 管理员应该可以访问用户列表
        response = test_client_manager.get(
            "/api/v1/users",
            username="admin"
        )
        
        assert response["status_code"] == 200
        assert response["data"]["success"] is True
    
    def test_holder_permissions(self, client: TestClient):
        """测试数据持有方权限"""
        # 数据持有方不应该可以访问用户列表
        response = test_client_manager.get(
            "/api/v1/users",
            username="holder"
        )
        
        assert response["status_code"] == 403  # 禁止访问
        assert response["data"]["success"] is False
    
    # ==================== 用户管理测试 ====================
    
    def test_get_current_user(self, client: TestClient):
        """测试获取当前用户信息"""
        response = test_client_manager.get(
            "/api/v1/auth/me",
            username="admin"
        )
        
        assert response["status_code"] == 200
        data = response["data"]
        assert data["success"] is True
        assert data["data"]["username"] == "admin"
        assert data["data"]["role"] == "admin"
        assert data["data"]["full_name"] == "系统管理员"
    
    def test_logout(self, client: TestClient):
        """测试用户登出"""
        response = test_client_manager.post(
            "/api/v1/auth/logout",
            username="admin"
        )
        
        assert response["status_code"] == 200
        data = response["data"]
        assert data["success"] is True
        assert "登出成功" in data["message"]
    
    # ==================== 安全功能测试 ====================
    
    def test_password_policy(self, client: TestClient):
        """测试密码策略"""
        test_cases = [
            ("short", "123", False),  # 太短
            ("noupper", "lowercase123", False),  # 没有大写
            ("nolower", "UPPERCASE123", False),  # 没有小写
            ("nodigit", "NoDigitsHere", False),  # 没有数字
            ("valid", "ValidPass123", True),  # 有效密码
            ("special", "Valid@Pass123", True),  # 包含特殊字符
        ]
        
        for username_base, password, should_succeed in test_cases:
            username = f"test_{username_base}"
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": username,
                    "password": password,
                    "full_name": f"测试用户{username_base}",
                    "email": f"{username}@example.com",
                    "role": "data_holder",
                    "organization": "测试公司"
                }
            )
            
            if should_succeed:
                assert response.status_code == 200, f"密码 '{password}' 应该通过但失败了"
            else:
                assert response.status_code == 400, f"密码 '{password}' 应该失败但通过了"
    
    # ==================== 边界条件测试 ====================
    
    def test_empty_credentials(self, client: TestClient):
        """测试空凭证"""
        # 空用户名
        response1 = client.post(
            "/api/v1/auth/login",
            json={
                "username": "",
                "password": "SomePassword123"
            }
        )
        assert response1.status_code == 422  # 验证错误
        
        # 空密码
        response2 = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": ""
            }
        )
        assert response2.status_code == 422  # 验证错误
    
    def test_long_inputs(self, client: TestClient):
        """测试长输入"""
        long_username = "a" * 100
        long_password = "A" * 100 + "1"  # 确保包含数字
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": long_username,
                "password": long_password,
                "full_name": "长输入测试用户",
                "email": "long@example.com",
                "role": "data_holder",
                "organization": "测试公司"
            }
        )
        
        # 长输入应该被拒绝或成功，但不应该崩溃
        assert response.status_code in [200, 400, 422]
    
    # ==================== 性能测试 ====================
    
    def test_login_performance(self, client: TestClient):
        """测试登录性能"""
        import time
        
        start_time = time.time()
        
        for i in range(5):  # 测试5次登录
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "admin",
                    "password": "Admin1234"
                }
            )
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 5次登录应该在3秒内完成
        assert total_time < 3.0, f"登录性能太慢: {total_time:.2f}秒"
        print(f"✅ 登录性能测试通过: 5次登录耗时 {total_time:.2f}秒")
    
    # ==================== 错误处理测试 ====================
    
    def test_malformed_json(self, client: TestClient):
        """测试畸形JSON"""
        response = client.post(
            "/api/v1/auth/login",
            data="{malformed json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # 验证错误
    
    def test_wrong_content_type(self, client: TestClient):
        """测试错误的内容类型"""
        response = client.post(
            "/api/v1/auth/login",
            data="username=admin&password=Admin1234",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422  # 验证错误


if __name__ == "__main__":
    """直接运行测试"""
    pytest.main([__file__, "-v"])