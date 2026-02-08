"""
资产管理模块测试
测试资产的CRUD操作、搜索、版本控制等功能
"""
import pytest
from fastapi.testclient import TestClient


class TestAssetCRUD:
    """资产CRUD操作测试"""
    
    def test_create_asset(self, client: TestClient, db, manager_headers):
        """测试创建资产"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # 创建用户
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
        
        # 创建资产
        response = client.post(
            "/api/v1/assets/",
            headers=manager_headers,
            json={
                "name": "客户关系管理系统数据",
                "description": "CRM系统中的客户数据资产",
                "data_classification": "内部",
                "sensitivity_level": "一般",
                "data_source": "CRM系统",
                "data_format": "MySQL数据库",
                "estimated_volume": "100GB",
                "update_frequency": "实时"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["name"] == "客户关系管理系统数据"
        assert "id" in data
        assert "asset_code" in data  # 应该自动生成资产编码
    
    def test_get_asset_list(self, client: TestClient, db, manager_headers):
        """测试获取资产列表"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.core.security import get_password_hash
        
        # 创建用户
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
        
        # 创建测试资产
        asset1 = DataAsset(
            name="资产1",
            asset_code="DA202602090001",
            description="测试资产1",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        asset2 = DataAsset(
            name="资产2",
            asset_code="DA202602090002",
            description="测试资产2",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        db.add_all([asset1, asset2])
        db.commit()
        
        # 获取列表
        response = client.get(
            "/api/v1/assets/",
            headers=manager_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 2
    
    def test_get_asset_detail(self, client: TestClient, db, manager_headers):
        """测试获取资产详情"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.core.security import get_password_hash
        
        # 创建用户和资产
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
        
        asset = DataAsset(
            name="测试资产",
            asset_code="DA202602090001",
            description="测试描述",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        db.add(asset)
        db.commit()
        
        # 获取详情
        response = client.get(
            f"/api/v1/assets/{asset.id}",
            headers=manager_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == asset.id
        assert data["name"] == "测试资产"
    
    def test_update_asset(self, client: TestClient, db, manager_headers):
        """测试更新资产"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.core.security import get_password_hash
        
        # 创建用户和资产
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
        
        asset = DataAsset(
            name="原始名称",
            asset_code="DA202602090001",
            description="原始描述",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        db.add(asset)
        db.commit()
        
        # 更新资产
        response = client.put(
            f"/api/v1/assets/{asset.id}",
            headers=manager_headers,
            json={
                "name": "更新后的名称",
                "description": "更新后的描述"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的名称"
        assert data["description"] == "更新后的描述"
    
    def test_delete_asset(self, client: TestClient, db, manager_headers):
        """测试删除资产（逻辑删除）"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.core.security import get_password_hash
        
        # 创建用户和资产
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
        
        asset = DataAsset(
            name="待删除资产",
            asset_code="DA202602090001",
            description="测试删除",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        db.add(asset)
        db.commit()
        asset_id = asset.id
        
        # 删除资产
        response = client.delete(
            f"/api/v1/assets/{asset_id}",
            headers=manager_headers
        )
        
        assert response.status_code in [200, 204]
        
        # 验证已被逻辑删除（查询不到）
        get_response = client.get(
            f"/api/v1/assets/{asset_id}",
            headers=manager_headers
        )
        assert get_response.status_code == 404


class TestAssetSearch:
    """资产搜索测试"""
    
    def test_search_by_keyword(self, client: TestClient, db, manager_headers):
        """测试关键词搜索"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.core.security import get_password_hash
        
        # 创建用户和资产
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
        
        asset1 = DataAsset(
            name="客户数据",
            asset_code="DA202602090001",
            description="CRM系统客户数据",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        asset2 = DataAsset(
            name="订单数据",
            asset_code="DA202602090002",
            description="电商订单数据",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        db.add_all([asset1, asset2])
        db.commit()
        
        # 搜索"客户"
        response = client.get(
            "/api/v1/assets/?keyword=客户",
            headers=manager_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert any("客户" in item["name"] or "客户" in item["description"] 
                  for item in data["items"])
    
    def test_filter_by_status(self, client: TestClient, db, manager_headers):
        """测试按状态筛选"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.core.security import get_password_hash
        
        # 创建用户和不同状态的资产
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
        
        draft_asset = DataAsset(
            name="草稿资产",
            asset_code="DA202602090001",
            description="草稿状态",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="draft"
        )
        active_asset = DataAsset(
            name="活跃资产",
            asset_code="DA202602090002",
            description="活跃状态",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=user.id,
            status="active"
        )
        db.add_all([draft_asset, active_asset])
        db.commit()
        
        # 筛选草稿状态
        response = client.get(
            "/api/v1/assets/?status=draft",
            headers=manager_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "draft" for item in data["items"])
    
    def test_pagination(self, client: TestClient, db, manager_headers):
        """测试分页功能"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.core.security import get_password_hash
        
        # 创建用户和多个资产
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
        
        # 创建15个资产
        assets = [
            DataAsset(
                name=f"资产{i}",
                asset_code=f"DA20260209{i:04d}",
                description=f"测试资产{i}",
                data_classification="内部",
                sensitivity_level="一般",
                owner_id=user.id,
                status="draft"
            )
            for i in range(1, 16)
        ]
        db.add_all(assets)
        db.commit()
        
        # 测试第一页（每页10条）
        response = client.get(
            "/api/v1/assets/?page=1&page_size=10",
            headers=manager_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] >= 15
        assert data["page"] == 1


class TestAssetValidation:
    """资产数据验证测试"""
    
    def test_create_asset_missing_required_fields(self, client: TestClient, db, manager_headers):
        """测试缺少必填字段"""
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
        
        # 缺少name字段
        response = client.post(
            "/api/v1/assets/",
            headers=manager_headers,
            json={
                "description": "测试描述"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_asset_invalid_classification(self, client: TestClient, db, manager_headers):
        """测试无效的数据分类"""
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
                "data_classification": "无效分类",  # 无效值
                "sensitivity_level": "一般"
            }
        )
        
        assert response.status_code == 422
