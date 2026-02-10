"""
材料管理模块全面测试
测试材料上传、哈希存证、版本管理、MinIO集成等
"""
import pytest
import io
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.material import Material, MaterialVersion, MaterialFile, MaterialHash
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialUploadRequest
from .test_client import test_client_manager


class TestMaterialsComprehensive:
    """材料管理功能全面测试"""
    
    # ==================== 材料创建测试 ====================
    
    def test_create_material_success(self, client: TestClient, db_session: AsyncSession):
        """测试创建材料记录成功"""
        response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-TEST-001",
                "material_name": "测试材料",
                "material_type": "report",
                "description": "这是一个测试材料",
                "tags": ["测试", "报告"],
                "confidential_level": "internal"
            }
        )
        
        assert response["status_code"] == 200
        data = response["data"]
        assert data["success"] is True
        assert "material_id" in data["data"]
        assert data["data"]["material_code"] == "MAT-TEST-001"
        assert data["data"]["material_name"] == "测试材料"
        assert data["data"]["status"] == "pending"
    
    def test_create_material_duplicate_code(self, client: TestClient, db_session: AsyncSession):
        """测试重复材料编码创建失败"""
        # 先创建一个材料
        response1 = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-DUP-001",
                "material_name": "第一个材料",
                "material_type": "report"
            }
        )
        assert response1["status_code"] == 200
        
        # 尝试用相同编码创建
        response2 = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-DUP-001",
                "material_name": "第二个材料",
                "material_type": "document"
            }
        )
        
        assert response2["status_code"] == 400
        data = response2["data"]
        assert data["success"] is False
        assert "材料编码已存在" in data["message"]
    
    def test_create_material_invalid_type(self, client: TestClient):
        """测试无效材料类型创建失败"""
        response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-INVALID-001",
                "material_name": "无效类型材料",
                "material_type": "invalid_type"  # 无效类型
            }
        )
        
        assert response["status_code"] == 422  # 验证错误
    
    # ==================== 材料查询测试 ====================
    
    def test_get_materials_list(self, client: TestClient, db_session: AsyncSession):
        """测试获取材料列表"""
        response = test_client_manager.get(
            "/api/v1/materials",
            username="holder"
        )
        
        assert response["status_code"] == 200
        data = response["data"]
        assert data["success"] is True
        assert "materials" in data["data"]
        assert "pagination" in data["data"]
    
    def test_get_material_detail(self, client: TestClient, db_session: AsyncSession):
        """测试获取材料详情"""
        # 先创建一个材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-DETAIL-001",
                "material_name": "详情测试材料",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # 获取详情
        detail_response = test_client_manager.get(
            f"/api/v1/materials/{material_id}",
            username="holder"
        )
        
        assert detail_response["status_code"] == 200
        data = detail_response["data"]
        assert data["success"] is True
        assert data["data"]["material_code"] == "MAT-DETAIL-001"
        assert data["data"]["material_name"] == "详情测试材料"
    
    def test_get_nonexistent_material(self, client: TestClient):
        """测试获取不存在的材料"""
        response = test_client_manager.get(
            "/api/v1/materials/999999",
            username="holder"
        )
        
        assert response["status_code"] == 404
        data = response["data"]
        assert data["success"] is False
        assert "材料不存在" in data["message"]
    
    # ==================== 材料更新测试 ====================
    
    def test_update_material_success(self, client: TestClient, db_session: AsyncSession):
        """测试更新材料信息"""
        # 先创建一个材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-UPDATE-001",
                "material_name": "原始名称",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # 更新材料
        update_response = test_client_manager.put(
            f"/api/v1/materials/{material_id}",
            username="holder",
            json={
                "material_name": "更新后的名称",
                "description": "更新描述",
                "tags": ["更新", "测试"]
            }
        )
        
        assert update_response["status_code"] == 200
        data = update_response["data"]
        assert data["success"] is True
        assert data["data"]["material_name"] == "更新后的名称"
        assert data["data"]["description"] == "更新描述"
    
    def test_update_material_status(self, client: TestClient, db_session: AsyncSession):
        """测试更新材料状态"""
        # 先创建一个材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-STATUS-001",
                "material_name": "状态测试材料",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # 提交审核
        submit_response = test_client_manager.post(
            f"/api/v1/materials/{material_id}/submit",
            username="holder"
        )
        
        assert submit_response["status_code"] == 200
        data = submit_response["data"]
        assert data["success"] is True
        assert data["data"]["status"] == "submitted"
    
    # ==================== 材料删除测试 ====================
    
    def test_delete_material_success(self, client: TestClient, db_session: AsyncSession):
        """测试删除材料（软删除）"""
        # 先创建一个材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-DELETE-001",
                "material_name": "删除测试材料",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # 删除材料
        delete_response = test_client_manager.delete(
            f"/api/v1/materials/{material_id}",
            username="holder"
        )
        
        assert delete_response["status_code"] == 200
        data = delete_response["data"]
        assert data["success"] is True
        assert "删除成功" in data["message"]
        
        # 验证材料已被标记为删除
        detail_response = test_client_manager.get(
            f"/api/v1/materials/{material_id}",
            username="holder"
        )
        
        assert detail_response["status_code"] == 404  # 已删除的材料应该返回404
    
    # ==================== 材料搜索测试 ====================
    
    def test_search_materials(self, client: TestClient, db_session: AsyncSession):
        """测试搜索材料"""
        # 创建几个测试材料
        test_materials = [
            {"material_code": "MAT-SEARCH-001", "material_name": "搜索测试材料一", "material_type": "report"},
            {"material_code": "MAT-SEARCH-002", "material_name": "搜索测试材料二", "material_type": "document"},
            {"material_code": "MAT-OTHER-001", "material_name": "其他材料", "material_type": "image"},
        ]
        
        for material_data in test_materials:
            test_client_manager.post(
                "/api/v1/materials",
                username="holder",
                json=material_data
            )
        
        # 搜索包含"搜索测试"的材料
        search_response = test_client_manager.get(
            "/api/v1/materials/search",
            username="holder",
            params={"keyword": "搜索测试"}
        )
        
        assert search_response["status_code"] == 200
        data = search_response["data"]
        assert data["success"] is True
        assert len(data["data"]["materials"]) >= 2  # 应该找到至少2个
    
    # ==================== 材料版本测试 ====================
    
    def test_create_material_version(self, client: TestClient, db_session: AsyncSession):
        """测试创建材料版本"""
        # 先创建一个材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-VERSION-001",
                "material_name": "版本测试材料",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # 创建新版本
        version_response = test_client_manager.post(
            f"/api/v1/materials/{material_id}/versions",
            username="holder",
            json={
                "version_notes": "第一版更新",
                "changes": "更新了材料内容和描述"
            }
        )
        
        assert version_response["status_code"] == 200
        data = version_response["data"]
        assert data["success"] is True
        assert "version_id" in data["data"]
    
    def test_get_material_versions(self, client: TestClient, db_session: AsyncSession):
        """测试获取材料版本历史"""
        # 先创建一个材料并添加版本
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-VERHIST-001",
                "material_name": "版本历史测试",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # 添加两个版本
        for i in range(2):
            test_client_manager.post(
                f"/api/v1/materials/{material_id}/versions",
                username="holder",
                json={
                    "version_notes": f"版本 {i+1}",
                    "changes": f"第 {i+1} 次更新"
                }
            )
        
        # 获取版本历史
        versions_response = test_client_manager.get(
            f"/api/v1/materials/{material_id}/versions",
            username="holder"
        )
        
        assert versions_response["status_code"] == 200
        data = versions_response["data"]
        assert data["success"] is True
        assert len(data["data"]["versions"]) >= 2  # 应该至少有2个版本
    
    # ==================== 材料审核测试 ====================
    
    def test_material_approval_workflow(self, client: TestClient, db_session: AsyncSession):
        """测试材料审核流程"""
        # holder创建材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-APPROVAL-001",
                "material_name": "审核测试材料",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # holder提交审核
        submit_response = test_client_manager.post(
            f"/api/v1/materials/{material_id}/submit",
            username="holder"
        )
        
        assert submit_response["status_code"] == 200
        assert submit_response["data"]["data"]["status"] == "submitted"
        
        # auditor审核通过
        approve_response = test_client_manager.post(
            f"/api/v1/materials/{material_id}/approve",
            username="auditor",
            json={
                "approval_notes": "审核通过，材料符合要求",
                "next_step": "可用于资产关联"
            }
        )
        
        assert approve_response["status_code"] == 200
        data = approve_response["data"]
        assert data["success"] is True
        assert data["data"]["status"] == "approved"
    
    def test_material_rejection(self, client: TestClient, db_session: AsyncSession):
        """测试材料审核驳回"""
        # holder创建并提交材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-REJECT-001",
                "material_name": "驳回测试材料",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        test_client_manager.post(
            f"/api/v1/materials/{material_id}/submit",
            username="holder"
        )
        
        # auditor审核驳回
        reject_response = test_client_manager.post(
            f"/api/v1/materials/{material_id}/reject",
            username="auditor",
            json={
                "rejection_reason": "材料内容不完整，需要补充",
                "suggestions": "请补充详细的数据来源说明"
            }
        )
        
        assert reject_response["status_code"] == 200
        data = reject_response["data"]
        assert data["success"] is True
        assert data["data"]["status"] == "rejected"
    
    # ==================== 权限测试 ====================
    
    def test_permission_checks(self, client: TestClient, db_session: AsyncSession):
        """测试材料操作权限"""
        # holder创建材料
        create_response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-PERM-001",
                "material_name": "权限测试材料",
                "material_type": "report"
            }
        )
        
        assert create_response["status_code"] == 200
        material_id = create_response["data"]["data"]["material_id"]
        
        # evaluator尝试删除（应该失败）
        delete_response = test_client_manager.delete(
            f"/api/v1/materials/{material_id}",
            username="evaluator"
        )
        
        # evaluator没有删除权限，应该返回403或404
        assert delete_response["status_code"] in [403, 404]
    
    # ==================== 边界条件测试 ====================
    
    def test_empty_material_name(self, client: TestClient):
        """测试空材料名称"""
        response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": "MAT-EMPTY-001",
                "material_name": "",  # 空名称
                "material_type": "report"
            }
        )
        
        assert response["status_code"] == 422  # 验证错误
    
    def test_long_material_code(self, client: TestClient):
        """测试超长材料编码"""
        long_code = "A" * 101  # 超过100字符
        
        response = test_client_manager.post(
            "/api/v1/materials",
            username="holder",
            json={
                "material_code": long_code,
                "material_name": "长编码测试",
                "material_type": "report"
            }
        )
        
        assert response["status_code"] == 422  # 验证错误
    
    # ==================== 性能测试 ====================
    
    def test_batch_material_operations(self, client: TestClient):
        """测试批量材料操作性能"""
        import time
        
        start_time = time.time()
        
        # 批量创建10个材料
        for i in range(10):
            response = test_client_manager.post(
                "/api/v1/materials",
                username="holder",
                json={
                    "material_code": f"MAT-BATCH-{i:03d}",
                    "material_name": f"批量测试材料 {i}",
                    "material_type": "report"
                }
            )
            assert response["status_code"] == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 10个材料创建应该在5秒内完成
        assert total_time < 5.0, f"批量操作太慢: {total_time:.2f}秒"
        print(f"✅ 批量操作性能测试通过: 10个材料创建耗时 {total_time:.2f}秒")


if __name__ == "__main__":
    """直接运行测试"""
    pytest.main([__file__, "-v"])