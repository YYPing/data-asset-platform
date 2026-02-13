# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

数据资产全生命周期管理平台 (Data Asset Lifecycle Management Platform) — a government-oriented platform for managing data assets through an 8-stage lifecycle with 6 RBAC roles.

## Architecture

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL (`backend/`)
- **Frontend**: React 19 + Vite + TypeScript + Ant Design 6 (`frontend/`)
- **Infra**: Docker Compose (PostgreSQL 16 + backend service)

### Key Domain Concepts

- **8-stage lifecycle** (defined in `backend/app/models/asset.py:AssetStage`): resource_inventory → asset_inventory → usage_scenario → compliance_assessment → quality_report → accounting_guidance → value_assessment → operation
- **6 RBAC roles** (defined in `backend/app/models/user.py:Role`): data_holder, registry_center, assessor, compliance, regulator, admin
- **State machine** in `backend/app/engine/lifecycle.py`: submit → approve (auto-advances stage) / reject
- **Material upload** with SHA-256 hash certification and version control
- **Audit logs** are insert-only (no UPDATE/DELETE) for compliance

### Backend Structure

```
backend/app/
├── api/v1/          # Route handlers (auth, assets, stages, materials, audit, statistics)
├── core/            # Config, database, security (bcrypt + JWT), audit helper
├── engine/          # Lifecycle state machine
├── models/          # SQLAlchemy models (user, organization, asset, stage, material, audit, approval)
├── services/        # Business logic (asset_service, material_service)
└── scripts/seed.py  # Demo data seeder
```

### Frontend Structure

```
frontend/src/
├── api/             # Axios client with JWT interceptor, typed API modules
├── components/      # AppLayout (Ant Design sidebar + header)
├── pages/           # All page components by domain
└── utils/           # Stage/role labels, auth helpers (localStorage)
```

## Commands

### Backend

```bash
cd backend
pip3 install -r requirements.txt
python3 -m pytest tests/ -v                    # Run all 30 tests
python3 -m pytest tests/test_auth.py -v        # Run single test file
python3 -m pytest tests/test_lifecycle.py::test_approve_advances_stage -v  # Single test
DATABASE_URL="sqlite:///./dev.db" python3 -m app.scripts.seed  # Seed demo data (SQLite)
python3 -m uvicorn app.main:app --reload       # Dev server (needs DATABASE_URL)
```

### Frontend

```bash
cd frontend
npm install
npm run build          # TypeScript check + production build
npm run dev            # Dev server at :5173 (proxies /api → :8000)
npm run lint           # ESLint
```

### Docker (full stack)

```bash
docker compose up -d db          # Start PostgreSQL only
docker compose up --build        # Start everything
```

## Testing Notes

- Tests use a shared SQLite DB via `backend/tests/conftest.py` — do NOT add per-file DB overrides
- `conftest.py` provides `client` fixture (TestClient) and auto-creates/drops tables per session
- Uses `bcrypt` directly (not passlib) due to bcrypt 5.x incompatibility — see `core/security.py`
- Pydantic models with nullable FK fields must use `Optional[int] = None`, not `int = None`

## Seed Accounts

All passwords: `123456`

| Username | Role | Description |
|----------|------|-------------|
| holder | data_holder | 数据持有方 |
| registry | registry_center | 登记中心 |
| assessor | assessor | 评估机构 |
| compliance | compliance | 合规人员 |
| regulator | regulator | 行业监管部门 |
| admin | admin | 系统管理员 |

## Known TODOs

- `// TODO: HARDCODED` markers in frontend for APIs that need backend support (ApprovalList pending list, AssessmentList)
- Alembic migrations not yet configured (using `create_all` for now)
- Frontend vite proxy assumes backend at localhost:8000
