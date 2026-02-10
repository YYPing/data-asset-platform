"""
测试数据库工具
提供测试用的数据库会话和初始化功能
"""
import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from app.models.base import Base
from app.models.user import User
from app.models.asset import Asset, AssetVersion, AssetMaterial, AssetCertificate
from app.models.material import Material, MaterialVersion, MaterialFile, MaterialHash
from app.models.certificate import Certificate, CertificateFile, CertificateAsset, CertificateValidation, ExpiryAlert
from app.models.workflow import WorkflowDefinition, WorkflowInstance, WorkflowNode, ApprovalRecord
from app.models.assessment import AssessmentRecord
from app.models.system import Permission, RolePermission, Organization, OperationLog
from app.core.security import get_password_hash

from .test_config import test_settings


class TestDatabase:
    """测试数据库管理类"""
    
    def __init__(self):
        # 创建异步引擎
        self.engine = create_async_engine(
            test_settings.DATABASE_URL,
            echo=test_settings.DATABASE_ECHO,
            future=True
        )
        
        # 创建会话工厂
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # 测试数据
        self.test_users = []
        self.test_assets = []
        self.test_materials = []
        self.test_certificates = []
    
    async def init_database(self):
        """初始化数据库（创建所有表）"""
        async with self.engine.begin() as conn:
            # 删除所有表（如果存在）
            await conn.run_sync(Base.metadata.drop_all)
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ 测试数据库初始化完成")
    
    async def create_test_data(self):
        """创建测试数据"""
        async with self.AsyncSessionLocal() as session:
            # 创建测试用户
            test_users_data = [
                {
                    "username": "admin",
                    "password": "Admin1234",
                    "full_name": "系统管理员",
                    "email": "admin@example.com",
                    "role": "admin",
                    "organization": "系统管理部"
                },
                {
                    "username": "auditor",
                    "password": "Auditor123",
                    "full_name": "审核员张三",
                    "email": "auditor@example.com",
                    "role": "center_auditor",
                    "organization": "登记中心"
                },
                {
                    "username": "evaluator",
                    "password": "Evaluator123",
                    "full_name": "评估师李四",
                    "email": "evaluator@example.com",
                    "role": "evaluator",
                    "organization": "评估机构"
                },
                {
                    "username": "holder",
                    "password": "Holder1234",
                    "full_name": "数据持有方王五",
                    "email": "holder@example.com",
                    "role": "data_holder",
                    "organization": "数据公司"
                }
            ]
            
            for user_data in test_users_data:
                user = User(
                    username=user_data["username"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    role=user_data["role"],
                    organization=user_data["organization"],
                    is_active=True,
                    is_locked=False
                )
                session.add(user)
                self.test_users.append(user)
            
            await session.commit()
            
            # 创建测试资产
            test_assets_data = [
                {
                    "asset_code": "ASSET-2024-001",
                    "asset_name": "客户数据资产",
                    "category": "customer",
                    "data_classification": "level2",
                    "sensitivity_level": "medium",
                    "description": "客户基本信息数据资产",
                    "data_source": "CRM系统",
                    "data_volume": "10GB",
                    "data_format": "structured",
                    "update_frequency": "daily",
                    "asset_type": "data",
                    "estimated_value": 500000,
                    "status": "draft",
                    "created_by": self.test_users[3].id  # holder用户
                },
                {
                    "asset_code": "ASSET-2024-002",
                    "asset_name": "交易数据资产",
                    "category": "transaction",
                    "data_classification": "level3",
                    "sensitivity_level": "high",
                    "description": "交易记录数据资产",
                    "data_source": "交易系统",
                    "data_volume": "50GB",
                    "data_format": "structured",
                    "update_frequency": "real_time",
                    "asset_type": "data",
                    "estimated_value": 1000000,
                    "status": "submitted",
                    "created_by": self.test_users[3].id  # holder用户
                }
            ]
            
            for asset_data in test_assets_data:
                asset = Asset(**asset_data)
                session.add(asset)
                self.test_assets.append(asset)
            
            await session.commit()
            
            # 创建测试材料
            test_materials_data = [
                {
                    "material_code": "MAT-2024-001",
                    "material_name": "数据质量报告",
                    "material_type": "report",
                    "file_name": "data_quality_report.pdf",
                    "file_size": 2048000,  # 2MB
                    "file_hash": "a1b2c3d4e5f678901234567890123456",
                    "hash_algorithm": "sha256",
                    "status": "approved",
                    "created_by": self.test_users[3].id  # holder用户
                },
                {
                    "material_code": "MAT-2024-002",
                    "material_name": "合规评估报告",
                    "material_type": "report",
                    "file_name": "compliance_report.pdf",
                    "file_size": 3072000,  # 3MB
                    "file_hash": "b2c3d4e5f678901234567890123456a1",
                    "hash_algorithm": "sha256",
                    "status": "pending",
                    "created_by": self.test_users[3].id  # holder用户
                }
            ]
            
            for material_data in test_materials_data:
                material = Material(**material_data)
                session.add(material)
                self.test_materials.append(material)
            
            await session.commit()
            
            # 创建测试证书
            test_certificates_data = [
                {
                    "certificate_no": "CERT-2024-001",
                    "certificate_name": "数据资产登记证书",
                    "certificate_type": "registration",
                    "holder_name": "数据公司",
                    "issuing_authority": "数据资产登记中心",
                    "issue_date": "2024-01-15",
                    "expiry_date": "2025-01-14",
                    "status": "valid",
                    "created_by": self.test_users[1].id  # auditor用户
                },
                {
                    "certificate_no": "CERT-2024-002",
                    "certificate_name": "合规评估证书",
                    "certificate_type": "compliance",
                    "holder_name": "数据公司",
                    "issuing_authority": "合规评估机构",
                    "issue_date": "2024-02-01",
                    "expiry_date": "2025-01-31",
                    "status": "valid",
                    "created_by": self.test_users[2].id  # evaluator用户
                }
            ]
            
            for cert_data in test_certificates_data:
                certificate = Certificate(**cert_data)
                session.add(certificate)
                self.test_certificates.append(certificate)
            
            await session.commit()
            
            print("✅ 测试数据创建完成")
            print(f"  创建用户: {len(self.test_users)} 个")
            print(f"  创建资产: {len(self.test_assets)} 个")
            print(f"  创建材料: {len(self.test_materials)} 个")
            print(f"  创建证书: {len(self.test_certificates)} 个")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    async def cleanup(self):
        """清理测试数据"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        print("✅ 测试数据库清理完成")


# 全局测试数据库实例
test_db = TestDatabase()


async def init_test_database():
    """初始化测试数据库（供外部调用）"""
    await test_db.init_database()
    await test_db.create_test_data()


async def cleanup_test_database():
    """清理测试数据库（供外部调用）"""
    await test_db.cleanup()


def get_test_db() -> TestDatabase:
    """获取测试数据库实例"""
    return test_db