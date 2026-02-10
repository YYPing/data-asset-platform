"""
数据库核心模块
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    from app.models.base import Base
    # 确保所有模型被导入，这样Base.metadata才有表定义
    import app.models.user
    import app.models.asset
    import app.models.system
    import app.models.workflow
    import app.models.certificate
    import app.models.organization
    
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ 数据库初始化完成")
    
    # 创建默认管理员用户
    await _create_default_admin()


async def _create_default_admin():
    """创建默认管理员用户（如果不存在）"""
    from app.models.user import User
    from app.core.security import get_password_hash
    from sqlalchemy import select
    
    try:
        async with AsyncSessionLocal() as session:
            # 检查admin是否已存在
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                admin = User(
                    username="admin",
                    password_hash=get_password_hash("SecureAdmin@2026!MVP"),
                    real_name="系统管理员",
                    email="admin@example.com",
                    phone="13800000000",
                    role="admin",
                    status="active",
                )
                session.add(admin)

                # 创建测试用户
                test_user = User(
                    username="user1",
                    password_hash=get_password_hash("SecureUser@2026!MVP"),
                    real_name="测试用户",
                    email="user1@example.com",
                    phone="13800000001",
                    role="data_holder",
                    status="active",
                )
                session.add(test_user)

                await session.commit()
                print("✅ 默认用户已创建: admin / SecureAdmin@2026!MVP, user1 / SecureUser@2026!MVP")
            else:
                print("✅ 管理员用户已存在")
    except Exception as e:
        print(f"⚠️ 创建默认用户失败: {e}")