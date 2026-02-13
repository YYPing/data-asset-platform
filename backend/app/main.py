from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.auth import router as auth_router
from app.api.v1.assets import router as assets_router
from app.api.v1.stages import router as stages_router
from app.api.v1.materials import router as materials_router
from app.api.v1.audit import router as audit_router
from app.api.v1.statistics import router as stats_router

# Import all models so Base.metadata knows about them
from app.models import user, organization, asset, stage, material, audit, approval  # noqa

app = FastAPI(title=settings.PROJECT_NAME)

# Auto-create tables on startup (dev convenience, use Alembic in production)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(stages_router)
app.include_router(materials_router)
app.include_router(audit_router)
app.include_router(stats_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
