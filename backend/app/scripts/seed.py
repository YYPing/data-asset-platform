"""
Seed script: creates demo organizations, users, and sample assets.
Usage: cd backend && python -m app.scripts.seed
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.core.database import engine, SessionLocal, Base
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.user import User, Role
from app.models.asset import DataAsset, AssetStage
from app.models.stage import StageRecord
from app.models.material import StageMaterial  # noqa
from app.models.audit import AuditLog  # noqa
from app.models.approval import ApprovalRecord  # noqa


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if already seeded
    if db.query(User).first():
        print("Database already has data, skipping seed.")
        db.close()
        return

    # --- Organizations ---
    orgs = [
        Organization(name="示范数据集团", org_type="enterprise", credit_code="91110000MA01ABCD01", contact_person="张三"),
        Organization(name="市大数据中心", org_type="government", credit_code="91110000MA01ABCD02", contact_person="李四"),
        Organization(name="信达评估事务所", org_type="institution", credit_code="91110000MA01ABCD03", contact_person="王五"),
    ]
    db.add_all(orgs)
    db.flush()

    pwd = get_password_hash("123456")

    # --- Users (one per role) ---
    users = [
        User(username="holder", hashed_password=pwd, real_name="张三", role=Role.DATA_HOLDER, org_id=orgs[0].id),
        User(username="registry", hashed_password=pwd, real_name="李四", role=Role.REGISTRY_CENTER, org_id=orgs[1].id),
        User(username="assessor", hashed_password=pwd, real_name="王五", role=Role.ASSESSOR, org_id=orgs[2].id),
        User(username="compliance", hashed_password=pwd, real_name="赵六", role=Role.COMPLIANCE, org_id=orgs[1].id),
        User(username="regulator", hashed_password=pwd, real_name="钱七", role=Role.REGULATOR, org_id=orgs[1].id),
        User(username="admin", hashed_password=pwd, real_name="管理员", role=Role.ADMIN, org_id=orgs[1].id),
    ]
    db.add_all(users)
    db.flush()

    # --- Sample Assets at various stages ---
    assets = [
        DataAsset(
            name="城市交通流量数据集",
            description="包含全市主要路口的实时交通流量数据",
            org_id=orgs[0].id, created_by=users[0].id,
            current_stage=AssetStage.COMPLIANCE_ASSESSMENT,
            asset_type="数据集", data_classification="公共",
        ),
        DataAsset(
            name="企业信用评分模型",
            description="基于多维度数据的企业信用评分算法模型",
            org_id=orgs[0].id, created_by=users[0].id,
            current_stage=AssetStage.VALUE_ASSESSMENT,
            asset_type="算法模型", data_classification="内部",
        ),
        DataAsset(
            name="政务服务接口集合",
            description="统一政务服务平台对外开放的API接口",
            org_id=orgs[0].id, created_by=users[0].id,
            current_stage=AssetStage.RESOURCE_INVENTORY,
            asset_type="API服务", data_classification="公共",
        ),
        DataAsset(
            name="医疗健康档案数据",
            description="脱敏后的居民健康档案统计数据",
            org_id=orgs[0].id, created_by=users[0].id,
            current_stage=AssetStage.OPERATION,
            asset_type="数据集", data_classification="敏感",
            valuation_amount=1500000, accounting_type="无形资产",
        ),
    ]
    db.add_all(assets)
    db.commit()

    print(f"Seed complete: {len(orgs)} orgs, {len(users)} users, {len(assets)} assets")
    print("All user passwords: 123456")
    print("Accounts: holder / registry / assessor / compliance / regulator / admin")
    db.close()


if __name__ == "__main__":
    seed()
