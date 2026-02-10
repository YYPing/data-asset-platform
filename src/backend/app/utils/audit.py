"""
审计日志工具模块
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.system import OperationLog


class AuditLogger:
    """审计日志记录器"""
    
    @staticmethod
    async def log_operation(
        db: AsyncSession,
        user_id: Optional[int],
        operation_type: str,
        target_type: str,
        target_id: Optional[int] = None,
        description: Optional[str] = None,
        result: str = "success",
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OperationLog:
        """
        记录操作日志
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            operation_type: 操作类型（create/update/delete/submit/approve/reject等）
            target_type: 目标类型（asset/material/certificate等）
            target_id: 目标ID
            description: 操作描述
            result: 操作结果（success/failure/partial）
            error_message: 错误信息
            ip_address: 客户端IP
            user_agent: User-Agent
            
        Returns:
            OperationLog: 创建的日志记录
        """
        log = OperationLog(
            user_id=user_id,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            result=result,
            error_message=error_message,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        return log
    
    @staticmethod
    def get_client_info(request: Request) -> Dict[str, Optional[str]]:
        """
        从请求中提取客户端信息
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            dict: 包含ip_address和user_agent的字典
        """
        # 获取真实IP（考虑代理）
        ip_address = request.headers.get("X-Real-IP") or \
                    request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or \
                    request.client.host if request.client else None
        
        # 获取User-Agent
        user_agent = request.headers.get("User-Agent")
        
        return {
            "ip_address": ip_address,
            "user_agent": user_agent
        }
    
    @staticmethod
    async def log_asset_create(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产创建操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="create",
            target_type="asset",
            target_id=asset_id,
            description=f"创建资产: {asset_code}",
            **client_info
        )
    
    @staticmethod
    async def log_asset_update(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        changes: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产更新操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        description = f"更新资产: {asset_code}"
        if changes:
            changed_fields = ", ".join(changes.keys())
            description += f" (修改字段: {changed_fields})"
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="update",
            target_type="asset",
            target_id=asset_id,
            description=description,
            **client_info
        )
    
    @staticmethod
    async def log_asset_delete(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产删除操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="delete",
            target_type="asset",
            target_id=asset_id,
            description=f"删除资产: {asset_code}",
            **client_info
        )
    
    @staticmethod
    async def log_asset_submit(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产提交审核操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="submit",
            target_type="asset",
            target_id=asset_id,
            description=f"提交资产审核: {asset_code}",
            **client_info
        )
    
    @staticmethod
    async def log_asset_approve(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        comment: Optional[str] = None,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产审核通过操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        description = f"审核通过资产: {asset_code}"
        if comment:
            description += f" (意见: {comment})"
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="approve",
            target_type="asset",
            target_id=asset_id,
            description=description,
            **client_info
        )
    
    @staticmethod
    async def log_asset_reject(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        reason: Optional[str] = None,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产审核驳回操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        description = f"驳回资产: {asset_code}"
        if reason:
            description += f" (原因: {reason})"
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="reject",
            target_type="asset",
            target_id=asset_id,
            description=description,
            **client_info
        )
    
    @staticmethod
    async def log_asset_register(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产登记操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="register",
            target_type="asset",
            target_id=asset_id,
            description=f"完成资产登记: {asset_code}",
            **client_info
        )
    
    @staticmethod
    async def log_asset_cancel(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        reason: Optional[str] = None,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录资产注销操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        description = f"注销资产: {asset_code}"
        if reason:
            description += f" (原因: {reason})"
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="cancel",
            target_type="asset",
            target_id=asset_id,
            description=description,
            **client_info
        )
    
    @staticmethod
    async def log_version_create(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        version: int,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录版本创建操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="create_version",
            target_type="asset",
            target_id=asset_id,
            description=f"创建资产版本: {asset_code} v{version}",
            **client_info
        )
    
    @staticmethod
    async def log_version_rollback(
        db: AsyncSession,
        user_id: int,
        asset_id: int,
        asset_code: str,
        from_version: int,
        to_version: int,
        request: Optional[Request] = None
    ) -> OperationLog:
        """记录版本回滚操作"""
        client_info = AuditLogger.get_client_info(request) if request else {}
        
        return await AuditLogger.log_operation(
            db=db,
            user_id=user_id,
            operation_type="rollback_version",
            target_type="asset",
            target_id=asset_id,
            description=f"回滚资产版本: {asset_code} v{from_version} -> v{to_version}",
            **client_info
        )
