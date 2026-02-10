"""
测试客户端工具
提供测试用的FastAPI TestClient和认证工具
"""
import asyncio
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token
from .test_config import test_settings
from .test_db import test_db


class TestClientManager:
    """测试客户端管理类"""
    
    def __init__(self):
        # 创建测试客户端
        self.client = TestClient(app)
        
        # 用户Token缓存
        self.user_tokens: Dict[str, Dict[str, str]] = {}
    
    def get_auth_headers(self, username: str = "admin") -> Dict[str, str]:
        """获取认证头"""
        if username not in self.user_tokens:
            # 创建测试Token
            token_data = {
                "sub": username,
                "username": username,
                "role": self._get_user_role(username)
            }
            
            access_token = create_access_token(
                data=token_data,
                expires_delta=None  # 使用默认过期时间
            )
            
            self.user_tokens[username] = {
                "access_token": access_token,
                "token_type": "bearer"
            }
        
        token_info = self.user_tokens[username]
        return {
            "Authorization": f"{token_info['token_type']} {token_info['access_token']}"
        }
    
    def _get_user_role(self, username: str) -> str:
        """根据用户名获取角色"""
        role_map = {
            "admin": "admin",
            "auditor": "center_auditor",
            "evaluator": "evaluator",
            "holder": "data_holder"
        }
        return role_map.get(username, "data_holder")
    
    async def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.user_tokens[username] = {
                "access_token": token_data["access_token"],
                "refresh_token": token_data["refresh_token"],
                "token_type": token_data["token_type"]
            }
        
        return response.json()
    
    def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发起请求（自动添加认证头）"""
        # 获取用户名（默认为admin）
        username = kwargs.pop("username", "admin")
        
        # 获取认证头
        headers = kwargs.get("headers", {})
        auth_headers = self.get_auth_headers(username)
        headers.update(auth_headers)
        kwargs["headers"] = headers
        
        # 发起请求
        method_func = getattr(self.client, method.lower())
        response = method_func(url, **kwargs)
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else {},
            "headers": dict(response.headers)
        }
    
    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        return self.make_request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        return self.make_request("POST", url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        return self.make_request("PUT", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        return self.make_request("DELETE", url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> Dict[str, Any]:
        """PATCH请求"""
        return self.make_request("PATCH", url, **kwargs)
    
    async def create_test_user(self, session: AsyncSession, user_data: Dict[str, Any]) -> User:
        """创建测试用户"""
        from app.core.security import get_password_hash
        
        user = User(
            username=user_data["username"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data.get("full_name", "测试用户"),
            email=user_data.get("email", f"{user_data['username']}@example.com"),
            role=user_data.get("role", "data_holder"),
            organization=user_data.get("organization", "测试组织"),
            is_active=user_data.get("is_active", True),
            is_locked=user_data.get("is_locked", False)
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user
    
    async def create_test_asset(self, session: AsyncSession, asset_data: Dict[str, Any], user_id: int) -> Any:
        """创建测试资产"""
        from app.models.asset import Asset
        
        asset = Asset(
            asset_code=asset_data.get("asset_code", f"TEST-ASSET-{user_id}"),
            asset_name=asset_data.get("asset_name", "测试资产"),
            category=asset_data.get("category", "customer"),
            data_classification=asset_data.get("data_classification", "level2"),
            sensitivity_level=asset_data.get("sensitivity_level", "medium"),
            description=asset_data.get("description", "测试数据资产"),
            data_source=asset_data.get("data_source", "测试系统"),
            data_volume=asset_data.get("data_volume", "1GB"),
            data_format=asset_data.get("data_format", "structured"),
            update_frequency=asset_data.get("update_frequency", "monthly"),
            asset_type=asset_data.get("asset_type", "data"),
            estimated_value=asset_data.get("estimated_value", 100000),
            status=asset_data.get("status", "draft"),
            created_by=user_id
        )
        
        session.add(asset)
        await session.commit()
        await session.refresh(asset)
        
        return asset
    
    async def create_test_material(self, session: AsyncSession, material_data: Dict[str, Any], user_id: int) -> Any:
        """创建测试材料"""
        from app.models.material import Material
        
        material = Material(
            material_code=material_data.get("material_code", f"TEST-MAT-{user_id}"),
            material_name=material_data.get("material_name", "测试材料"),
            material_type=material_data.get("material_type", "report"),
            file_name=material_data.get("file_name", "test_file.pdf"),
            file_size=material_data.get("file_size", 1024000),  # 1MB
            file_hash=material_data.get("file_hash", "testhash1234567890"),
            hash_algorithm=material_data.get("hash_algorithm", "sha256"),
            status=material_data.get("status", "pending"),
            created_by=user_id
        )
        
        session.add(material)
        await session.commit()
        await session.refresh(material)
        
        return material
    
    async def create_test_certificate(self, session: AsyncSession, certificate_data: Dict[str, Any], user_id: int) -> Any:
        """创建测试证书"""
        from app.models.certificate import Certificate
        
        certificate = Certificate(
            certificate_no=certificate_data.get("certificate_no", f"TEST-CERT-{user_id}"),
            certificate_name=certificate_data.get("certificate_name", "测试证书"),
            certificate_type=certificate_data.get("certificate_type", "registration"),
            holder_name=certificate_data.get("holder_name", "测试持有人"),
            issuing_authority=certificate_data.get("issuing_authority", "测试机构"),
            issue_date=certificate_data.get("issue_date", "2024-01-01"),
            expiry_date=certificate_data.get("expiry_date", "2025-01-01"),
            status=certificate_data.get("status", "valid"),
            created_by=user_id
        )
        
        session.add(certificate)
        await session.commit()
        await session.refresh(certificate)
        
        return certificate


# 全局测试客户端实例
test_client_manager = TestClientManager()


def get_test_client() -> TestClientManager:
    """获取测试客户端实例"""
    return test_client_manager


# pytest fixtures
import pytest
from .test_db import test_db


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """设置测试数据库"""
    await test_db.init_database()
    await test_db.create_test_data()
    yield
    await test_db.cleanup()


@pytest.fixture
def client():
    """获取测试客户端"""
    return test_client_manager.client


@pytest.fixture
def auth_headers():
    """获取认证头"""
    return test_client_manager.get_auth_headers()


@pytest.fixture
def admin_headers():
    """获取管理员认证头"""
    return test_client_manager.get_auth_headers("admin")


@pytest.fixture
def auditor_headers():
    """获取审核员认证头"""
    return test_client_manager.get_auth_headers("auditor")


@pytest.fixture
def evaluator_headers():
    """获取评估师认证头"""
    return test_client_manager.get_auth_headers("evaluator")


@pytest.fixture
def holder_headers():
    """获取数据持有方认证头"""
    return test_client_manager.get_auth_headers("holder")


@pytest.fixture
async def db_session():
    """获取数据库会话"""
    async for session in test_db.get_session():
        yield session


@pytest.fixture
def test_users():
    """获取测试用户"""
    return test_db.test_users


@pytest.fixture
def test_assets():
    """获取测试资产"""
    return test_db.test_assets


@pytest.fixture
def test_materials():
    """获取测试材料"""
    return test_db.test_materials


@pytest.fixture
def test_certificates():
    """获取测试证书"""
    return test_db.test_certificates