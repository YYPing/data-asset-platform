# 数据资产全生命周期管理平台 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建覆盖全市的数据资产全生命周期管理平台，支持6种角色、8阶段生命周期、材料哈希存证、双大屏展示。

**Architecture:** FastAPI后端提供RESTful API，React前端按角色提供工作台。核心是8阶段生命周期状态机引擎，每个阶段绑定材料要求和审批流。PostgreSQL存储所有数据，审计日志只INSERT不DELETE。

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL, React 18, Vite, Ant Design 5, Docker Compose

---

## Phase 1: 项目骨架与基础设施

### Task 1: 后端项目初始化

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`

**Step 1: 创建 requirements.txt**

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
alembic==1.13.0
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic-settings==2.5.0
```

**Step 2: 创建 config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "数据资产管理平台"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/data_asset"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 3: 创建 database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 4: 创建 main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
```

**Step 5: 运行验证**

Run: `cd backend && pip install -r requirements.txt && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
Expected: 服务启动，访问 /api/health 返回 {"status": "ok"}

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: initialize backend with FastAPI, config, database setup"
```

---

### Task 2: Docker Compose 环境

**Files:**
- Create: `docker-compose.yml`
- Create: `init.sh`
- Create: `.env.example`

**Step 1: 创建 docker-compose.yml**

```yaml
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: data_asset
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/data_asset
    depends_on:
      - db
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads

volumes:
  pgdata:
```

**Step 2: 创建 init.sh**

```bash
#!/bin/bash
set -e

echo "=== 数据资产管理平台 - 环境启动 ==="

# 启动数据库
docker compose up -d db
echo "等待数据库就绪..."
sleep 3

# 安装后端依赖并启动
cd backend
pip install -r requirements.txt -q
python -m alembic upgrade head 2>/dev/null || true
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 安装前端依赖并启动
cd frontend
npm install -q 2>/dev/null || true
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== 服务已启动 ==="
echo "后端: http://localhost:8000"
echo "前端: http://localhost:5173"
echo "API文档: http://localhost:8000/docs"
```

**Step 3: Commit**

```bash
git add docker-compose.yml init.sh .env.example
git commit -m "feat: add Docker Compose and init.sh for dev environment"
```

---

### Task 3: 数据库模型 — 用户与组织

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/organization.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Test: `backend/tests/test_models_user.py`

**Step 1: 写失败测试**

```python
# backend/tests/test_models_user.py
from app.models.user import User, Role
from app.models.organization import Organization

def test_user_model_exists():
    user = User(username="test", role=Role.DATA_HOLDER)
    assert user.username == "test"
    assert user.role == Role.DATA_HOLDER

def test_organization_model_exists():
    org = Organization(name="测试机构", org_type="enterprise")
    assert org.name == "测试机构"
```

**Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_models_user.py -v`
Expected: FAIL — ImportError

**Step 3: 实现 Organization 模型**

```python
# backend/app/models/organization.py
from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    org_type = Column(String(50), nullable=False)  # enterprise, government, institution
    credit_code = Column(String(50), unique=True)   # 统一社会信用代码
    contact_person = Column(String(100))
    contact_phone = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

**Step 4: 实现 User 模型**

```python
# backend/app/models/user.py
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(str, enum.Enum):
    DATA_HOLDER = "data_holder"           # 数据持有方
    REGISTRY_CENTER = "registry_center"   # 登记中心
    ASSESSOR = "assessor"                 # 评估机构
    COMPLIANCE = "compliance"             # 合规人员
    REGULATOR = "regulator"              # 行业监管部门
    ADMIN = "admin"                       # 系统管理员

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False, default="")
    real_name = Column(String(100))
    role = Column(Enum(Role), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

    organization = relationship("Organization", backref="users")
```

**Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_models_user.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/models/ backend/tests/
git commit -m "feat: add User and Organization models with RBAC roles"
```

---

### Task 4: 数据库模型 — 资产与生命周期

**Files:**
- Create: `backend/app/models/asset.py`
- Create: `backend/app/models/stage.py`
- Create: `backend/app/models/material.py`
- Test: `backend/tests/test_models_asset.py`

<!-- PLACEHOLDER_TASK4 -->

**Step 1: 写失败测试**

```python
# backend/tests/test_models_asset.py
from app.models.asset import DataAsset, AssetStage

def test_asset_stage_enum():
    assert AssetStage.RESOURCE_INVENTORY.value == "resource_inventory"
    assert AssetStage.OPERATION.value == "operation"

def test_data_asset_model():
    asset = DataAsset(name="测试数据资产", current_stage=AssetStage.RESOURCE_INVENTORY)
    assert asset.name == "测试数据资产"
```

**Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/test_models_asset.py -v`
Expected: FAIL

**Step 3: 实现资产模型**

```python
# backend/app/models/asset.py
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Numeric, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class AssetStage(str, enum.Enum):
    RESOURCE_INVENTORY = "resource_inventory"       # 1.数据资源梳理
    ASSET_INVENTORY = "asset_inventory"             # 2.数据资产梳理
    USAGE_SCENARIO = "usage_scenario"               # 3.数据使用场景报告
    COMPLIANCE_ASSESSMENT = "compliance_assessment"  # 4.合规评估报告
    QUALITY_REPORT = "quality_report"               # 5.数据质量报告
    ACCOUNTING_GUIDANCE = "accounting_guidance"      # 6.入账指导意见
    VALUE_ASSESSMENT = "value_assessment"            # 7.数据价值评估
    OPERATION = "operation"                         # 8.运营阶段

STAGE_ORDER = list(AssetStage)

class DataAsset(Base):
    __tablename__ = "data_assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    current_stage = Column(Enum(AssetStage), default=AssetStage.RESOURCE_INVENTORY)
    asset_type = Column(String(100))          # 资产类型分类
    data_classification = Column(String(50))  # 数据分类（公共/内部/敏感）
    valuation_amount = Column(Numeric(18, 2)) # 估值金额
    accounting_type = Column(String(50))      # 入账类型（无形资产/存货）
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", backref="assets")
    stage_records = relationship("StageRecord", backref="asset", order_by="StageRecord.created_at")
```

**Step 4: 实现阶段记录和材料模型**

```python
# backend/app/models/stage.py
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.asset import AssetStage

class StageStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class StageRecord(Base):
    __tablename__ = "stage_records"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("data_assets.id"), nullable=False)
    stage = Column(Enum(AssetStage), nullable=False)
    status = Column(Enum(StageStatus), default=StageStatus.DRAFT)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    reject_reason = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    materials = relationship("StageMaterial", backref="stage_record")
```

```python
# backend/app/models/material.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, func
from app.core.database import Base

class StageMaterial(Base):
    __tablename__ = "stage_materials"

    id = Column(Integer, primary_key=True, index=True)
    stage_record_id = Column(Integer, ForeignKey("stage_records.id"), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(BigInteger)
    file_type = Column(String(50))
    hash_sha256 = Column(String(64), nullable=False)  # SHA-256哈希存证
    version = Column(Integer, default=1)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
```

**Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/test_models_asset.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/models/ backend/tests/
git commit -m "feat: add DataAsset, StageRecord, StageMaterial models with 8-stage lifecycle"
```

---

### Task 5: 数据库模型 — 审计日志与审批

**Files:**
- Create: `backend/app/models/audit.py`
- Create: `backend/app/models/approval.py`
- Test: `backend/tests/test_models_audit.py`

**Step 1: 实现审计日志模型**

```python
# backend/app/models/audit.py
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)     # create/update/delete/approve/reject/upload
    resource_type = Column(String(100), nullable=False)  # asset/material/stage/user
    resource_id = Column(Integer)
    detail = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    # 注意：此表无 UPDATE/DELETE 操作，只有 INSERT
```

**Step 2: Commit**

```bash
git add backend/app/models/
git commit -m "feat: add AuditLog model (insert-only for tamper-proof audit trail)"
```

---

## Phase 2: 认证与核心API

### Task 6: JWT认证

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/auth.py`
- Test: `backend/tests/test_auth.py`

**Step 1: 实现 security.py（JWT + 密码哈希）**
**Step 2: 实现 auth.py（登录/注册/获取当前用户）**
**Step 3: 写测试验证登录流程**
**Step 4: Commit**

---

### Task 7: 资产CRUD API

**Files:**
- Create: `backend/app/api/v1/assets.py`
- Create: `backend/app/services/asset_service.py`
- Test: `backend/tests/test_assets.py`

**Step 1: 实现资产创建/列表/详情/更新API**
**Step 2: 实现RBAC权限检查（数据持有方只能看自己组织的资产）**
**Step 3: 写测试**
**Step 4: Commit**

---

### Task 8: 生命周期状态机引擎

**Files:**
- Create: `backend/app/engine/lifecycle.py`
- Create: `backend/app/api/v1/stages.py`
- Test: `backend/tests/test_lifecycle.py`

**Step 1: 实现状态机（阶段推进、退回、验证）**
**Step 2: 实现阶段API（提交、审批、退回）**
**Step 3: 写测试验证阶段流转**
**Step 4: Commit**

---

### Task 9: 材料上传与哈希存证

**Files:**
- Create: `backend/app/api/v1/materials.py`
- Create: `backend/app/services/material_service.py`
- Test: `backend/tests/test_materials.py`

**Step 1: 实现文件上传 + SHA-256自动计算**
**Step 2: 实现版本控制（同名文件新版本）**
**Step 3: 实现材料列表和下载**
**Step 4: 写测试**
**Step 5: Commit**

---

### Task 10: 审批流API

**Files:**
- Create: `backend/app/api/v1/approvals.py`
- Create: `backend/app/services/approval_service.py`
- Test: `backend/tests/test_approvals.py`

**Step 1: 实现审批提交/通过/退回**
**Step 2: 审批通过后自动推进阶段**
**Step 3: 写测试**
**Step 4: Commit**

---

### Task 11: 审计日志中间件

**Files:**
- Create: `backend/app/core/audit_middleware.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_audit.py`

**Step 1: 实现审计日志记录（装饰器或中间件）**
**Step 2: 所有关键操作自动记录**
**Step 3: 实现审计日志查询API**
**Step 4: Commit**

---

### Task 12: 统计分析API

**Files:**
- Create: `backend/app/api/v1/statistics.py`
- Create: `backend/app/services/stats_service.py`
- Test: `backend/tests/test_statistics.py`

**Step 1: 全市统计（资产总量、行业分布、阶段分布、趋势）**
**Step 2: 持有方统计（盘点情况、阶段进度、估值入账情况）**
**Step 3: 写测试**
**Step 4: Commit**

---

## Phase 3: 前端

### Task 13: 前端项目初始化

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`

**Step 1: `npm create vite@latest frontend -- --template react-ts`**
**Step 2: 安装 antd, react-router-dom, axios, @ant-design/charts**
**Step 3: 配置路由和布局骨架**
**Step 4: Commit**

---

### Task 14: 登录页与认证

**Files:**
- Create: `frontend/src/pages/auth/Login.tsx`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/store/auth.ts`

**Step 1: 登录表单（用户名+密码+角色选择）**
**Step 2: JWT token 存储和自动刷新**
**Step 3: 路由守卫（未登录跳转登录页）**
**Step 4: Commit**

---

### Task 15: 数据持有方工作台

**Files:**
- Create: `frontend/src/pages/asset/AssetList.tsx`
- Create: `frontend/src/pages/asset/AssetDetail.tsx`
- Create: `frontend/src/pages/asset/AssetCreate.tsx`
- Create: `frontend/src/pages/asset/StageProgress.tsx`
- Create: `frontend/src/pages/material/MaterialUpload.tsx`

**Step 1: 资产列表页（表格+搜索+筛选）**
**Step 2: 资产创建表单**
**Step 3: 资产详情页（8阶段进度条+当前阶段材料）**
**Step 4: 材料上传组件（显示哈希值）**
**Step 5: Commit**

---

### Task 16: 登记中心审批台

**Files:**
- Create: `frontend/src/pages/approval/ApprovalList.tsx`
- Create: `frontend/src/pages/approval/ApprovalDetail.tsx`

**Step 1: 待审批列表**
**Step 2: 审批详情（查看材料+通过/退回）**
**Step 3: Commit**

---

### Task 17: 评估机构工作台

**Files:**
- Create: `frontend/src/pages/assess/AssessmentList.tsx`
- Create: `frontend/src/pages/assess/AssessmentForm.tsx`

**Step 1: 待评估资产列表**
**Step 2: 评估表单（合规评估/价值评估）**
**Step 3: Commit**

---

### Task 18: 系统管理

**Files:**
- Create: `frontend/src/pages/admin/UserManage.tsx`
- Create: `frontend/src/pages/admin/OrgManage.tsx`
- Create: `frontend/src/pages/admin/AuditLogView.tsx`

**Step 1: 用户管理（CRUD+角色分配）**
**Step 2: 组织管理**
**Step 3: 审计日志查看（只读，支持筛选）**
**Step 4: Commit**

---

## Phase 4: 大屏

### Task 19: 全市监管大屏

**Files:**
- Create: `frontend/src/pages/monitor/CityDashboard.tsx`

**Step 1: 全市资产总量卡片**
**Step 2: 行业分布饼图**
**Step 3: 阶段分布柱状图**
**Step 4: 月度趋势折线图**
**Step 5: Commit**

---

### Task 20: 持有方大屏

**Files:**
- Create: `frontend/src/pages/dashboard/HolderDashboard.tsx`

**Step 1: 数据资产盘点情况概览**
**Step 2: 资产数量统计卡片**
**Step 3: 各阶段进度（8阶段进度条/环形图）**
**Step 4: 资产估值与入账情况（金额、无形资产/存货占比）**
**Step 5: 年度更新提醒列表**
**Step 6: Commit**

---

## Phase 5: 收尾

### Task 21: 种子数据与初始化脚本

**Files:**
- Create: `backend/app/scripts/seed.py`

**Step 1: 创建默认管理员账号**
**Step 2: 创建示例组织和用户**
**Step 3: 创建示例资产数据（覆盖各阶段）**
**Step 4: Commit**

---

### Task 22: CLAUDE.md 与文档

**Files:**
- Create: `CLAUDE.md`
- Update: `README.md`

**Step 1: 写 CLAUDE.md（构建/测试/架构说明）**
**Step 2: 写 README.md（项目说明+快速开始）**
**Step 3: Commit**
