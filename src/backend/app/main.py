"""
Data Asset Management Platform - Main Application Entry
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import engine, init_db
from app.core.scheduler import scheduler

# Import all routers
from app.api.v1.auth import router as auth_router
from app.api.v1.assets import router as assets_router
from app.api.v1.materials import router as materials_router
from app.api.v1.certificates import router as cert_router
from app.api.v1.workflow import router as workflow_router
from app.api.v1.assessment import router as assess_router
from app.api.v1.audit import router as audit_router
from app.api.v1.notifications import router as notify_router
from app.api.v1.statistics import router as stats_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Data Asset Management Platform...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Start scheduler
    if not scheduler.running:
        scheduler.start()
        print("✅ APScheduler started")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Data Asset Management Platform...")
    
    # Stop scheduler
    if scheduler.running:
        scheduler.shutdown()
        print("✅ APScheduler stopped")
    
    # Close database connections
    await engine.dispose()
    print("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Data Asset Management Platform",
    description="""
    ## 数据资产管理平台 API
    
    提供数据资产全生命周期管理功能：
    - 🔐 用户认证与权限管理
    - 📊 数据资产登记与管理
    - 📁 资料文件管理
    - 📜 登记证书管理
    - 🔄 工作流引擎
    - ✅ 数据资产评估
    - 📝 审计日志
    - 🔔 通知中心
    - 📈 统计分析
    - ⏰ 定时任务管理
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "data": {
                "errors": exc.errors(),
                "body": exc.body
            }
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "数据库操作失败",
            "data": {"detail": str(exc)}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": {"detail": str(exc)}
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Data Asset Management Platform",
        "version": "1.0.0",
        "scheduler_running": scheduler.running
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Data Asset Management Platform API",
        "docs": "/api/docs",
        "health": "/health"
    }


# Register all API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(materials_router, prefix="/api/v1/materials", tags=["Materials"])
app.include_router(cert_router, prefix="/api/v1/certificates", tags=["Certificates"])
app.include_router(workflow_router, prefix="/api/v1/workflow", tags=["Workflow"])
app.include_router(assess_router, prefix="/api/v1/assessment", tags=["Assessment"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(notify_router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(stats_router, prefix="/api/v1/statistics", tags=["Statistics"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Jobs"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
