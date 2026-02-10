"""数据库连接管理"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# 根据数据库类型调整参数
if "sqlite" in settings.DATABASE_URL:
    # SQLite不需要连接池参数
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
else:
    # PostgreSQL等需要连接池
    engine = create_async_engine(
        settings.DATABASE_URL, 
        echo=settings.DEBUG, 
        pool_size=10, 
        max_overflow=40
    )

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
