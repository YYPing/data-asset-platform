import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Numeric, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class AssetStage(str, enum.Enum):
    RESOURCE_INVENTORY = "resource_inventory"        # 1.数据资源梳理
    ASSET_INVENTORY = "asset_inventory"              # 2.数据资产梳理
    USAGE_SCENARIO = "usage_scenario"                # 3.数据使用场景报告
    COMPLIANCE_ASSESSMENT = "compliance_assessment"  # 4.合规评估报告
    QUALITY_REPORT = "quality_report"                # 5.数据质量报告
    ACCOUNTING_GUIDANCE = "accounting_guidance"       # 6.入账指导意见
    VALUE_ASSESSMENT = "value_assessment"             # 7.数据价值评估
    OPERATION = "operation"                          # 8.运营阶段


STAGE_ORDER = list(AssetStage)


class DataAsset(Base):
    __tablename__ = "data_assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    current_stage = Column(Enum(AssetStage), default=AssetStage.RESOURCE_INVENTORY)
    asset_type = Column(String(100))
    data_classification = Column(String(50))  # 公共/内部/敏感
    valuation_amount = Column(Numeric(18, 2))
    accounting_type = Column(String(50))      # 无形资产/存货
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", backref="assets")
    stage_records = relationship("StageRecord", backref="asset", order_by="StageRecord.created_at")
