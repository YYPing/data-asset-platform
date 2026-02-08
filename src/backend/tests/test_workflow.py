"""
工作流模块测试
测试工作流创建、审批、状态转换等功能
"""
import pytest
from fastapi.testclient import TestClient


class TestWorkflowBasic:
    """工作流基础功能测试"""
    
    def test_create_workflow_instance(self, client: TestClient, db, manager_headers):
        """测试创建工作流实例"""
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
        
        # 创建工作流实例
        response = client.post(
            "/api/v1/workflow/instances",
            headers=manager_headers,
            json={
                "asset_id": asset.id,
                "workflow_type": "registration",
                "title": "数据资产登记审批"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"  # 初始状态应该是pending
    
    def test_get_workflow_list(self, client: TestClient, db, manager_headers):
        """测试获取工作流列表"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.models.workflow import WorkflowInstance
        from app.core.security import get_password_hash
        
        # 创建用户、资产和工作流
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
        
        workflow = WorkflowInstance(
            asset_id=asset.id,
            workflow_type="registration",
            title="测试审批",
            status="pending",
            current_step="initial_review",
            initiator_id=user.id
        )
        db.add(workflow)
        db.commit()
        
        # 获取列表
        response = client.get(
            "/api/v1/workflow/instances",
            headers=manager_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1


class TestWorkflowApproval:
    """工作流审批测试"""
    
    def test_approve_workflow(self, client: TestClient, db, admin_headers):
        """测试审批通过"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.models.workflow import WorkflowInstance
        from app.core.security import get_password_hash
        
        # 创建管理员和资产
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
        
        asset = DataAsset(
            name="测试资产",
            asset_code="DA202602090001",
            description="测试描述",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=admin.id,
            status="draft"
        )
        db.add(asset)
        db.commit()
        
        workflow = WorkflowInstance(
            asset_id=asset.id,
            workflow_type="registration",
            title="测试审批",
            status="pending",
            current_step="initial_review",
            initiator_id=admin.id
        )
        db.add(workflow)
        db.commit()
        
        # 审批通过
        response = client.post(
            f"/api/v1/workflow/instances/{workflow.id}/approve",
            headers=admin_headers,
            json={
                "comment": "审批通过",
                "decision": "approve"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["approved", "in_progress"]  # 可能进入下一步或完成
    
    def test_reject_workflow(self, client: TestClient, db, admin_headers):
        """测试审批驳回"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.models.workflow import WorkflowInstance
        from app.core.security import get_password_hash
        
        # 创建管理员和资产
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
        
        asset = DataAsset(
            name="测试资产",
            asset_code="DA202602090001",
            description="测试描述",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=admin.id,
            status="draft"
        )
        db.add(asset)
        db.commit()
        
        workflow = WorkflowInstance(
            asset_id=asset.id,
            workflow_type="registration",
            title="测试审批",
            status="pending",
            current_step="initial_review",
            initiator_id=admin.id
        )
        db.add(workflow)
        db.commit()
        
        # 审批驳回
        response = client.post(
            f"/api/v1/workflow/instances/{workflow.id}/reject",
            headers=admin_headers,
            json={
                "comment": "材料不完整，请补充",
                "reason": "材料缺失"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
    
    def test_workflow_without_permission(self, client: TestClient, db, viewer_headers):
        """测试无权限用户不能审批"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.models.workflow import WorkflowInstance
        from app.core.security import get_password_hash
        
        # 创建用户和工作流
        viewer = User(
            username="viewer",
            hashed_password=get_password_hash("Viewer@123456"),
            full_name="查看者",
            email="viewer@example.com",
            role="viewer",
            is_active=True
        )
        db.add(viewer)
        db.commit()
        
        asset = DataAsset(
            name="测试资产",
            asset_code="DA202602090001",
            description="测试描述",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=viewer.id,
            status="draft"
        )
        db.add(asset)
        db.commit()
        
        workflow = WorkflowInstance(
            asset_id=asset.id,
            workflow_type="registration",
            title="测试审批",
            status="pending",
            current_step="initial_review",
            initiator_id=viewer.id
        )
        db.add(workflow)
        db.commit()
        
        # 尝试审批
        response = client.post(
            f"/api/v1/workflow/instances/{workflow.id}/approve",
            headers=viewer_headers,
            json={
                "comment": "审批通过",
                "decision": "approve"
            }
        )
        
        # viewer没有审批权限
        assert response.status_code == 403


class TestWorkflowStateTransition:
    """工作流状态转换测试"""
    
    def test_workflow_state_machine(self, client: TestClient, db, admin_headers):
        """测试工作流状态机转换"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.models.workflow import WorkflowInstance
        from app.core.security import get_password_hash
        
        # 创建管理员和资产
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
        
        asset = DataAsset(
            name="测试资产",
            asset_code="DA202602090001",
            description="测试描述",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=admin.id,
            status="draft"
        )
        db.add(asset)
        db.commit()
        
        workflow = WorkflowInstance(
            asset_id=asset.id,
            workflow_type="registration",
            title="测试审批",
            status="pending",
            current_step="initial_review",
            initiator_id=admin.id
        )
        db.add(workflow)
        db.commit()
        workflow_id = workflow.id
        
        # 第一步：初审通过
        response1 = client.post(
            f"/api/v1/workflow/instances/{workflow_id}/approve",
            headers=admin_headers,
            json={"comment": "初审通过"}
        )
        assert response1.status_code == 200
        
        # 获取当前状态
        get_response = client.get(
            f"/api/v1/workflow/instances/{workflow_id}",
            headers=admin_headers
        )
        assert get_response.status_code == 200
        current_data = get_response.json()
        
        # 验证状态已转换
        assert current_data["current_step"] != "initial_review"
    
    def test_invalid_state_transition(self, client: TestClient, db, admin_headers):
        """测试无效的状态转换"""
        from app.models.user import User
        from app.models.asset import DataAsset
        from app.models.workflow import WorkflowInstance
        from app.core.security import get_password_hash
        
        # 创建已完成的工作流
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
        
        asset = DataAsset(
            name="测试资产",
            asset_code="DA202602090001",
            description="测试描述",
            data_classification="内部",
            sensitivity_level="一般",
            owner_id=admin.id,
            status="active"
        )
        db.add(asset)
        db.commit()
        
        workflow = WorkflowInstance(
            asset_id=asset.id,
            workflow_type="registration",
            title="已完成的审批",
            status="completed",  # 已完成
            current_step="completed",
            initiator_id=admin.id
        )
        db.add(workflow)
        db.commit()
        
        # 尝试再次审批已完成的工作流
        response = client.post(
            f"/api/v1/workflow/instances/{workflow.id}/approve",
            headers=admin_headers,
            json={"comment": "再次审批"}
        )
        
        # 应该返回错误，不能审批已完成的工作流
        assert response.status_code == 400
