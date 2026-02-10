"""
Alembic环境配置文件
数据资产管理平台 - 支持异步数据库迁移

Features:
- 异步数据库连接 (asyncpg)
- 自动检测模型变更
- 支持在线和离线迁移
"""
import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有模型以确保它们被注册
from app.models import Base
from app.models import (
    User, Organization,
    DataAsset, Material, RegistrationCertificate,
    WorkflowDefinition, WorkflowInstance, WorkflowNode, ApprovalRecord,
    AssessmentRecord,
    AuditLog, Permission, RolePermission, DataDictionary,
    Notification, SystemConfig, AsyncJob, OperationLog
)

# Alembic Config对象
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据
target_metadata = Base.metadata

# 从环境变量获取数据库URL
def get_url():
    """获取数据库连接URL"""
    url = os.getenv("DATABASE_URL")
    if url:
        # 确保使用asyncpg驱动
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """
    离线模式运行迁移
    
    在离线模式下，只生成SQL脚本而不实际执行
    适用于需要DBA审核SQL的场景
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 比较类型变更
        compare_type=True,
        # 比较服务器默认值
        compare_server_default=True,
        # 包含对象名称
        include_object=include_object,
        # 包含模式
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    过滤要包含在迁移中的对象
    
    可以用于排除某些表或对象
    """
    # 排除分区子表（由PostgreSQL自动管理）
    if type_ == "table" and name.startswith("audit_logs_"):
        if name != "audit_logs":
            return False
    
    return True


def do_run_migrations(connection: Connection) -> None:
    """
    执行迁移
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 比较类型变更
        compare_type=True,
        # 比较服务器默认值
        compare_server_default=True,
        # 包含对象
        include_object=include_object,
        # 包含模式
        include_schemas=True,
        # 渲染为批处理（用于SQLite等不支持ALTER的数据库）
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    异步模式运行迁移
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    在线模式运行迁移
    
    使用异步引擎连接数据库并执行迁移
    """
    asyncio.run(run_async_migrations())


# 根据上下文选择运行模式
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
