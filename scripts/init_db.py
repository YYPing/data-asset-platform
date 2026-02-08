"""
Database initialization script
Creates tables and inserts default data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "backend"))

from datetime import datetime, timedelta
from sqlalchemy import text
from app.core.database import engine, async_session
from app.models.base import Base
from app.models.user import User, Organization
from app.models.asset import DataAsset, DataCategory
from app.models.workflow import WorkflowDefinition, WorkflowStep
from app.models.system import SystemConfig, DataDictionary
from app.services.user import UserService


async def create_tables():
    """Create all database tables"""
    print("📊 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully")


async def create_default_organization():
    """Create default organization"""
    print("🏢 Creating default organization...")
    async with async_session() as session:
        org = Organization(
            name="系统默认机构",
            code="DEFAULT",
            type="government",
            level=1,
            status="active"
        )
        session.add(org)
        await session.commit()
        await session.refresh(org)
        print(f"✅ Default organization created: {org.name} (ID: {org.id})")
        return org.id


async def create_default_users(org_id: int):
    """Create default users"""
    print("👤 Creating default users...")
    async with async_session() as session:
        # Admin user
        admin = User(
            username="admin",
            password_hash=UserService.hash_password("Admin@123456"),
            password_changed_at=datetime.utcnow(),
            password_expires_at=datetime.utcnow() + timedelta(days=365),
            real_name="系统管理员",
            email="admin@example.com",
            role="admin",
            organization_id=org_id,
            status="active"
        )
        session.add(admin)
        
        # Asset manager user
        manager = User(
            username="manager",
            password_hash=UserService.hash_password("Manager@123456"),
            password_changed_at=datetime.utcnow(),
            password_expires_at=datetime.utcnow() + timedelta(days=90),
            real_name="资产管理员",
            email="manager@example.com",
            role="asset_manager",
            organization_id=org_id,
            status="active"
        )
        session.add(manager)
        
        # Evaluator user
        evaluator = User(
            username="evaluator",
            password_hash=UserService.hash_password("Evaluator@123456"),
            password_changed_at=datetime.utcnow(),
            password_expires_at=datetime.utcnow() + timedelta(days=90),
            real_name="评估专家",
            email="evaluator@example.com",
            role="evaluator",
            organization_id=org_id,
            status="active"
        )
        session.add(evaluator)
        
        # Viewer user
        viewer = User(
            username="viewer",
            password_hash=UserService.hash_password("Viewer@123456"),
            password_changed_at=datetime.utcnow(),
            password_expires_at=datetime.utcnow() + timedelta(days=90),
            real_name="普通用户",
            email="viewer@example.com",
            role="viewer",
            organization_id=org_id,
            status="active"
        )
        session.add(viewer)
        
        await session.commit()
        print("✅ Default users created:")
        print("   - admin / Admin@123456 (系统管理员)")
        print("   - manager / Manager@123456 (资产管理员)")
        print("   - evaluator / Evaluator@123456 (评估专家)")
        print("   - viewer / Viewer@123456 (普通用户)")


async def create_data_categories():
    """Create default data categories"""
    print("📁 Creating data categories...")
    async with async_session() as session:
        categories = [
            {"name": "政务数据", "code": "GOV", "description": "政府部门业务数据"},
            {"name": "公共数据", "code": "PUBLIC", "description": "公共服务数据"},
            {"name": "企业数据", "code": "ENTERPRISE", "description": "企业经营数据"},
            {"name": "个人数据", "code": "PERSONAL", "description": "个人信息数据"},
            {"name": "科研数据", "code": "RESEARCH", "description": "科研项目数据"},
            {"name": "金融数据", "code": "FINANCE", "description": "金融交易数据"},
            {"name": "医疗数据", "code": "MEDICAL", "description": "医疗健康数据"},
            {"name": "教育数据", "code": "EDUCATION", "description": "教育培训数据"},
        ]
        
        for cat_data in categories:
            category = DataCategory(**cat_data, status="active")
            session.add(category)
        
        await session.commit()
        print(f"✅ Created {len(categories)} data categories")


async def create_workflow_definitions():
    """Create default workflow definitions"""
    print("🔄 Creating workflow definitions...")
    async with async_session() as session:
        # Asset registration workflow
        workflow = WorkflowDefinition(
            name="数据资产登记流程",
            code="ASSET_REGISTRATION",
            description="数据资产登记审批流程",
            version="1.0",
            status="active"
        )
        session.add(workflow)
        await session.flush()
        
        # Workflow steps
        steps = [
            {
                "workflow_id": workflow.id,
                "step_name": "提交申请",
                "step_code": "SUBMIT",
                "step_order": 1,
                "assignee_role": "asset_manager",
                "action_type": "submit",
                "is_required": True,
                "timeout_hours": 24
            },
            {
                "workflow_id": workflow.id,
                "step_name": "初审",
                "step_code": "INITIAL_REVIEW",
                "step_order": 2,
                "assignee_role": "asset_manager",
                "action_type": "approve",
                "is_required": True,
                "timeout_hours": 48
            },
            {
                "workflow_id": workflow.id,
                "step_name": "专家评估",
                "step_code": "EXPERT_REVIEW",
                "step_order": 3,
                "assignee_role": "evaluator",
                "action_type": "approve",
                "is_required": True,
                "timeout_hours": 72
            },
            {
                "workflow_id": workflow.id,
                "step_name": "终审",
                "step_code": "FINAL_REVIEW",
                "step_order": 4,
                "assignee_role": "admin",
                "action_type": "approve",
                "is_required": True,
                "timeout_hours": 24
            },
            {
                "workflow_id": workflow.id,
                "step_name": "完成",
                "step_code": "COMPLETE",
                "step_order": 5,
                "assignee_role": "system",
                "action_type": "complete",
                "is_required": True,
                "timeout_hours": 0
            }
        ]
        
        for step_data in steps:
            step = WorkflowStep(**step_data)
            session.add(step)
        
        await session.commit()
        print(f"✅ Created workflow: {workflow.name} with {len(steps)} steps")


async def create_system_configs():
    """Create default system configurations"""
    print("⚙️ Creating system configurations...")
    async with async_session() as session:
        configs = [
            {
                "config_key": "system.name",
                "config_value": "数据资产管理平台",
                "config_type": "string",
                "description": "系统名称"
            },
            {
                "config_key": "system.version",
                "config_value": "1.0.0",
                "config_type": "string",
                "description": "系统版本"
            },
            {
                "config_key": "security.password_expire_days",
                "config_value": "90",
                "config_type": "integer",
                "description": "密码过期天数"
            },
            {
                "config_key": "security.max_login_attempts",
                "config_value": "5",
                "config_type": "integer",
                "description": "最大登录尝试次数"
            },
            {
                "config_key": "security.account_lock_minutes",
                "config_value": "30",
                "config_type": "integer",
                "description": "账户锁定时长（分钟）"
            },
            {
                "config_key": "file.max_upload_size_mb",
                "config_value": "100",
                "config_type": "integer",
                "description": "最大上传文件大小（MB）"
            },
            {
                "config_key": "file.allowed_extensions",
                "config_value": "pdf,doc,docx,xls,xlsx,jpg,jpeg,png,zip",
                "config_type": "string",
                "description": "允许上传的文件扩展名"
            },
            {
                "config_key": "notification.email_enabled",
                "config_value": "false",
                "config_type": "boolean",
                "description": "是否启用邮件通知"
            },
            {
                "config_key": "notification.sms_enabled",
                "config_value": "false",
                "config_type": "boolean",
                "description": "是否启用短信通知"
            }
        ]
        
        for config_data in configs:
            config = SystemConfig(**config_data, is_public=False)
            session.add(config)
        
        await session.commit()
        print(f"✅ Created {len(configs)} system configurations")


async def create_data_dictionaries():
    """Create data dictionary entries"""
    print("📖 Creating data dictionaries...")
    async with async_session() as session:
        dictionaries = [
            # Asset status
            {"dict_type": "asset_status", "dict_code": "draft", "dict_value": "草稿", "sort_order": 1},
            {"dict_type": "asset_status", "dict_code": "pending", "dict_value": "待审核", "sort_order": 2},
            {"dict_type": "asset_status", "dict_code": "approved", "dict_value": "已通过", "sort_order": 3},
            {"dict_type": "asset_status", "dict_code": "rejected", "dict_value": "已驳回", "sort_order": 4},
            {"dict_type": "asset_status", "dict_code": "archived", "dict_value": "已归档", "sort_order": 5},
            
            # Data sensitivity
            {"dict_type": "data_sensitivity", "dict_code": "public", "dict_value": "公开", "sort_order": 1},
            {"dict_type": "data_sensitivity", "dict_code": "internal", "dict_value": "内部", "sort_order": 2},
            {"dict_type": "data_sensitivity", "dict_code": "confidential", "dict_value": "机密", "sort_order": 3},
            {"dict_type": "data_sensitivity", "dict_code": "secret", "dict_value": "秘密", "sort_order": 4},
            
            # Update frequency
            {"dict_type": "update_frequency", "dict_code": "realtime", "dict_value": "实时", "sort_order": 1},
            {"dict_type": "update_frequency", "dict_code": "daily", "dict_value": "每日", "sort_order": 2},
            {"dict_type": "update_frequency", "dict_code": "weekly", "dict_value": "每周", "sort_order": 3},
            {"dict_type": "update_frequency", "dict_code": "monthly", "dict_value": "每月", "sort_order": 4},
            {"dict_type": "update_frequency", "dict_code": "quarterly", "dict_value": "每季度", "sort_order": 5},
            {"dict_type": "update_frequency", "dict_code": "yearly", "dict_value": "每年", "sort_order": 6},
            
            # Storage type
            {"dict_type": "storage_type", "dict_code": "database", "dict_value": "数据库", "sort_order": 1},
            {"dict_type": "storage_type", "dict_code": "file", "dict_value": "文件", "sort_order": 2},
            {"dict_type": "storage_type", "dict_code": "api", "dict_value": "API接口", "sort_order": 3},
            {"dict_type": "storage_type", "dict_code": "cloud", "dict_value": "云存储", "sort_order": 4},
        ]
        
        for dict_data in dictionaries:
            dictionary = DataDictionary(**dict_data, status="active")
            session.add(dictionary)
        
        await session.commit()
        print(f"✅ Created {len(dictionaries)} data dictionary entries")


async def main():
    """Main initialization function"""
    print("=" * 60)
    print("🚀 Data Asset Management Platform - Database Initialization")
    print("=" * 60)
    print()
    
    try:
        # Create tables
        await create_tables()
        print()
        
        # Create default organization
        org_id = await create_default_organization()
        print()
        
        # Create default users
        await create_default_users(org_id)
        print()
        
        # Create data categories
        await create_data_categories()
        print()
        
        # Create workflow definitions
        await create_workflow_definitions()
        print()
        
        # Create system configurations
        await create_system_configs()
        print()
        
        # Create data dictionaries
        await create_data_dictionaries()
        print()
        
        print("=" * 60)
        print("✅ Database initialization completed successfully!")
        print("=" * 60)
        print()
        print("📝 Default login credentials:")
        print("   Admin:     admin / Admin@123456")
        print("   Manager:   manager / Manager@123456")
        print("   Evaluator: evaluator / Evaluator@123456")
        print("   Viewer:    viewer / Viewer@123456")
        print()
        print("🌐 Access the application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend:  http://localhost:8000")
        print("   API Docs: http://localhost:8000/api/docs")
        print()
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
