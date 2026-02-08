"""
认证模块测试
测试用户登录、Token验证、权限控制等功能
"""
import pytest
from fastapi.testclient import TestClient


class TestAuth:
    """认证功能测试"""
    
    def test_login_success(self, client: TestClient, db):
        """测试正确的用户名密码登录"""
        # 先创建测试用户
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            username="testuser",
            hashed_password=get_password_hash("Test@123456"),
            full_name="测试用户",
            email="test@example.com",
            role="viewer",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # 测试登录
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "Test@123456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client: TestClient, db):
        """测试错误密码登录"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            username="testuser",
            hashed_password=get_password_hash("Test@123456"),
            full_name="测试用户",
            email="test@example.com",
            role="viewer",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """测试不存在的用户登录"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "Test@123456"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, db, admin_headers):
        """测试获取当前用户信息"""
        # 创建管理员用户
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            username="admin",
            hashed_password=get_password_hash("Admin@123456"),
            full_name="管理员",
            email="admin@example.com",
            role="admin",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        response = client.get(
            "/api/v1/auth/me",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
    
    def test_access_without_token(self, client: TestClient):
        """测试未携带Token访问受保护接口"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    def test_access_with_invalid_token(self, client: TestClient):
        """测试使用无效Token访问"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_refresh_token(self, client: TestClient, db):
        """测试刷新Token"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            username="testuser",
            hashed_password=get_password_hash("Test@123456"),
            full_name="测试用户",
            email="test@example.com",
            role="viewer",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # 先登录获取refresh_token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "Test@123456"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # 使用refresh_token刷新
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestPermissions:
    """权限控制测试"""
    
    def test_admin_can_access_all(self, client: TestClient, db, admin_headers):
        """测试管理员可以访问所有资源"""
        # 创建管理员用户
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            username="admin",
            hashed_password=get_password_hash("Admin@123456"),
            full_name="管理员",
            email="admin@example.com",
            role="admin",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        # 测试访问用户列表（需要admin权限）
        response = client.get(
            "/api/v1/users/",
            headers=admin_headers
        )
        
        assert response.status_code == 200
    
    def test_viewer_cannot_create_asset(self, client: TestClient, db, viewer_headers):
        """测试普通用户不能创建资产"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            username="viewer",
            hashed_password=get_password_hash("Viewer@123456"),
            full_name="查看者",
            email="viewer@example.com",
            role="viewer",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        response = client.post(
            "/api/v1/assets/",
            headers=viewer_headers,
            json={
                "name": "测试资产",
                "description": "测试描述"
            }
        )
        
        # viewer角色没有创建权限，应该返回403
        assert response.status_code == 403
    
    def test_manager_can_create_asset(self, client: TestClient, db, manager_headers):
        """测试资产管理员可以创建资产"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        user = User(
            username="manager",
            hashed_password=get_password_hash("Manager@123456"),
            full_name="资产管理员",
            email="manager@example.com",
            role="asset_manager",
            is_active=True
        )
        db.add(user)
        db.commit()
        
        response = client.post(
            "/api/v1/assets/",
            headers=manager_headers,
            json={
                "name": "测试资产",
                "description": "测试描述",
                "data_classification": "内部",
                "sensitivity_level": "一般"
            }
        )
        
        # asset_manager角色有创建权限
        assert response.status_code in [200, 201]


class TestPasswordSecurity:
    """密码安全测试"""
    
    def test_weak_password_rejected(self, client: TestClient, db, admin_headers):
        """测试弱密码被拒绝"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        admin = User(
            username="admin",
            hashed_password=get_password_hash("Admin@123456"),
            full_name="管理员",
            email="admin@example.com",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        
        response = client.post(
            "/api/v1/users/",
            headers=admin_headers,
            json={
                "username": "newuser",
                "password": "123456",  # 弱密码
                "full_name": "新用户",
                "email": "new@example.com",
                "role": "viewer"
            }
        )
        
        # 应该返回400，密码不符合要求
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()
    
    def test_strong_password_accepted(self, client: TestClient, db, admin_headers):
        """测试强密码被接受"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        admin = User(
            username="admin",
            hashed_password=get_password_hash("Admin@123456"),
            full_name="管理员",
            email="admin@example.com",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        
        response = client.post(
            "/api/v1/users/",
            headers=admin_headers,
            json={
                "username": "newuser",
                "password": "Strong@Pass123",  # 强密码
                "full_name": "新用户",
                "email": "new@example.com",
                "role": "viewer"
            }
        )
        
        assert response.status_code in [200, 201]
