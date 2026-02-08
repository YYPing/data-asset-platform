"""
User service for business logic
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserQuery


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """User service class"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """Generate random password"""
        # At least one uppercase, one lowercase, one digit, one special char
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
                return password
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_users(
        db: AsyncSession,
        query: UserQuery
    ) -> tuple[list[User], int]:
        """List users with pagination and filters"""
        # Build base query
        stmt = select(User)
        count_stmt = select(func.count(User.id))
        
        # Apply filters
        if query.keyword:
            keyword_filter = or_(
                User.username.ilike(f"%{query.keyword}%"),
                User.real_name.ilike(f"%{query.keyword}%"),
                User.email.ilike(f"%{query.keyword}%"),
                User.phone.ilike(f"%{query.keyword}%")
            )
            stmt = stmt.where(keyword_filter)
            count_stmt = count_stmt.where(keyword_filter)
        
        if query.role:
            stmt = stmt.where(User.role == query.role)
            count_stmt = count_stmt.where(User.role == query.role)
        
        if query.status:
            stmt = stmt.where(User.status == query.status)
            count_stmt = count_stmt.where(User.status == query.status)
        
        if query.organization_id:
            stmt = stmt.where(User.organization_id == query.organization_id)
            count_stmt = count_stmt.where(User.organization_id == query.organization_id)
        
        # Get total count
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Apply pagination and ordering
        stmt = stmt.order_by(User.created_at.desc())
        stmt = stmt.offset((query.page - 1) * query.page_size).limit(query.page_size)
        
        # Execute query
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        return list(users), total
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create new user"""
        # Check if username exists
        existing_user = await UserService.get_user_by_username(db, user_data.username)
        if existing_user:
            raise ValueError(f"用户名 '{user_data.username}' 已存在")
        
        # Create user
        user = User(
            username=user_data.username,
            password_hash=UserService.hash_password(user_data.password),
            password_changed_at=datetime.utcnow(),
            password_expires_at=datetime.utcnow() + timedelta(days=90),  # 90 days expiry
            real_name=user_data.real_name,
            email=user_data.email,
            phone=user_data.phone,
            role=user_data.role,
            organization_id=user_data.organization_id,
            status=user_data.status
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[User]:
        """Update user"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Delete user"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        # Don't allow deleting admin user
        if user.username == "admin":
            raise ValueError("不能删除系统管理员账户")
        
        await db.delete(user)
        await db.commit()
        
        return True
    
    @staticmethod
    async def reset_password(db: AsyncSession, user_id: int) -> tuple[Optional[User], str]:
        """Reset user password"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return None, ""
        
        # Generate new random password
        new_password = UserService.generate_random_password()
        
        # Update user password
        user.password_hash = UserService.hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        user.password_expires_at = datetime.utcnow() + timedelta(days=90)
        user.failed_login_count = 0
        user.locked_until = None
        
        await db.commit()
        await db.refresh(user)
        
        return user, new_password
    
    @staticmethod
    async def update_login_info(
        db: AsyncSession,
        user_id: int,
        ip_address: str,
        success: bool = True
    ) -> None:
        """Update user login information"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            return
        
        if success:
            user.last_login_at = datetime.utcnow()
            user.last_login_ip = ip_address
            user.failed_login_count = 0
            user.locked_until = None
        else:
            user.failed_login_count += 1
            # Lock account after 5 failed attempts
            if user.failed_login_count >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        await db.commit()
