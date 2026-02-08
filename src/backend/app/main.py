"""FastAPI应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="data-asset-platform",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {{"status": "ok", "version": "0.1.0"}}

# API路由注册（由蜂群Agent逐步添加）
# from app.api.v1 import auth, assets, materials, ...
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
