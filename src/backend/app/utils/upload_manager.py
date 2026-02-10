"""
文件上传管理器
支持分片上传、断点续传
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
import json

from app.utils.minio_client import minio_client
from app.utils.file_hash import calculate_stream_hash, calculate_bytes_hash

logger = logging.getLogger(__name__)


class UploadSession:
    """上传会话"""
    
    def __init__(
        self,
        session_id: str,
        file_name: str,
        file_size: int,
        total_chunks: int,
        bucket_name: str,
        object_name: str
    ):
        self.session_id = session_id
        self.file_name = file_name
        self.file_size = file_size
        self.total_chunks = total_chunks
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.uploaded_chunks: set[int] = set()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.chunk_hashes: dict[int, str] = {}  # 每个分片的哈希值
    
    def add_chunk(self, chunk_index: int, chunk_hash: str) -> None:
        """添加已上传的分片"""
        self.uploaded_chunks.add(chunk_index)
        self.chunk_hashes[chunk_index] = chunk_hash
        self.updated_at = datetime.utcnow()
    
    def is_complete(self) -> bool:
        """检查是否所有分片都已上传"""
        return len(self.uploaded_chunks) == self.total_chunks
    
    def get_missing_chunks(self) -> list[int]:
        """获取缺失的分片索引"""
        all_chunks = set(range(self.total_chunks))
        return sorted(list(all_chunks - self.uploaded_chunks))
    
    def get_progress(self) -> float:
        """获取上传进度（0-100）"""
        if self.total_chunks == 0:
            return 100.0
        return (len(self.uploaded_chunks) / self.total_chunks) * 100
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "total_chunks": self.total_chunks,
            "bucket_name": self.bucket_name,
            "object_name": self.object_name,
            "uploaded_chunks": list(self.uploaded_chunks),
            "chunk_hashes": self.chunk_hashes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "progress": self.get_progress()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UploadSession":
        """从字典创建"""
        session = cls(
            session_id=data["session_id"],
            file_name=data["file_name"],
            file_size=data["file_size"],
            total_chunks=data["total_chunks"],
            bucket_name=data["bucket_name"],
            object_name=data["object_name"]
        )
        session.uploaded_chunks = set(data.get("uploaded_chunks", []))
        session.chunk_hashes = data.get("chunk_hashes", {})
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.updated_at = datetime.fromisoformat(data["updated_at"])
        return session


class UploadManager:
    """
    文件上传管理器
    支持分片上传和断点续传
    """
    
    # 默认分片大小：5MB
    DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024
    
    # 最大文件大小：1GB
    MAX_FILE_SIZE = 1024 * 1024 * 1024
    
    # 会话过期时间：24小时
    SESSION_EXPIRE_HOURS = 24
    
    def __init__(self):
        """初始化上传管理器"""
        self.sessions: dict[str, UploadSession] = {}
        self.chunk_size = self.DEFAULT_CHUNK_SIZE
    
    def create_session(
        self,
        session_id: str,
        file_name: str,
        file_size: int,
        bucket_name: str,
        object_name: str,
        chunk_size: int = None
    ) -> UploadSession:
        """
        创建上传会话
        
        Args:
            session_id: 会话ID
            file_name: 文件名
            file_size: 文件大小（字节）
            bucket_name: 存储桶名称
            object_name: 对象名称
            chunk_size: 分片大小（字节）
            
        Returns:
            UploadSession: 上传会话
            
        Raises:
            ValueError: 文件大小超过限制
        """
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"文件大小超过限制: {file_size} > {self.MAX_FILE_SIZE}"
            )
        
        chunk_size = chunk_size or self.chunk_size
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        session = UploadSession(
            session_id=session_id,
            file_name=file_name,
            file_size=file_size,
            total_chunks=total_chunks,
            bucket_name=bucket_name,
            object_name=object_name
        )
        
        self.sessions[session_id] = session
        logger.info(
            f"创建上传会话: {session_id}, 文件: {file_name}, "
            f"大小: {file_size}, 分片数: {total_chunks}"
        )
        
        return session
    
    def get_session(self, session_id: str) -> Optional[UploadSession]:
        """获取上传会话"""
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> None:
        """删除上传会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"删除上传会话: {session_id}")
    
    def upload_chunk(
        self,
        session_id: str,
        chunk_index: int,
        chunk_data: bytes
    ) -> dict:
        """
        上传分片
        
        Args:
            session_id: 会话ID
            chunk_index: 分片索引（从0开始）
            chunk_data: 分片数据
            
        Returns:
            dict: 上传结果
            
        Raises:
            ValueError: 会话不存在或分片索引无效
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"上传会话不存在: {session_id}")
        
        if chunk_index < 0 or chunk_index >= session.total_chunks:
            raise ValueError(
                f"分片索引无效: {chunk_index}, "
                f"有效范围: 0-{session.total_chunks - 1}"
            )
        
        # 计算分片哈希
        chunk_hash = calculate_bytes_hash(chunk_data, "sha256")
        
        # 上传分片到 MinIO（使用临时路径）
        chunk_object_name = f"{session.object_name}.part{chunk_index}"
        
        try:
            minio_client.upload_bytes(
                bucket_name=session.bucket_name,
                object_name=chunk_object_name,
                data=chunk_data,
                metadata={
                    "session_id": session_id,
                    "chunk_index": str(chunk_index),
                    "chunk_hash": chunk_hash
                }
            )
            
            # 记录已上传的分片
            session.add_chunk(chunk_index, chunk_hash)
            
            logger.info(
                f"分片上传成功: {session_id}, 分片: {chunk_index}, "
                f"进度: {session.get_progress():.2f}%"
            )
            
            return {
                "session_id": session_id,
                "chunk_index": chunk_index,
                "chunk_hash": chunk_hash,
                "uploaded_chunks": len(session.uploaded_chunks),
                "total_chunks": session.total_chunks,
                "progress": session.get_progress(),
                "is_complete": session.is_complete()
            }
            
        except Exception as e:
            logger.error(f"分片上传失败: {session_id}, 分片: {chunk_index}, 错误: {e}")
            raise
    
    async def complete_upload(
        self,
        session_id: str,
        verify_hash: str = None
    ) -> dict:
        """
        完成上传（合并所有分片）
        
        Args:
            session_id: 会话ID
            verify_hash: 验证哈希值（可选）
            
        Returns:
            dict: 完成结果
            
        Raises:
            ValueError: 会话不存在或上传未完成
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"上传会话不存在: {session_id}")
        
        if not session.is_complete():
            missing = session.get_missing_chunks()
            raise ValueError(
                f"上传未完成，缺失分片: {missing[:10]}"
                f"{'...' if len(missing) > 10 else ''}"
            )
        
        try:
            # 下载所有分片并合并
            merged_data = bytearray()
            
            for chunk_index in range(session.total_chunks):
                chunk_object_name = f"{session.object_name}.part{chunk_index}"
                chunk_data = minio_client.download_stream(
                    session.bucket_name,
                    chunk_object_name
                )
                merged_data.extend(chunk_data)
            
            # 验证文件大小
            if len(merged_data) != session.file_size:
                raise ValueError(
                    f"文件大小不匹配: 期望 {session.file_size}, "
                    f"实际 {len(merged_data)}"
                )
            
            # 计算完整文件哈希
            file_hash = calculate_bytes_hash(bytes(merged_data), "sha256")
            
            # 如果提供了验证哈希，进行验证
            if verify_hash and file_hash != verify_hash:
                raise ValueError(
                    f"文件哈希不匹配: 期望 {verify_hash}, 实际 {file_hash}"
                )
            
            # 上传合并后的文件
            minio_client.upload_bytes(
                bucket_name=session.bucket_name,
                object_name=session.object_name,
                data=bytes(merged_data),
                metadata={
                    "session_id": session_id,
                    "file_name": session.file_name,
                    "file_size": str(session.file_size),
                    "file_hash": file_hash
                }
            )
            
            # 删除临时分片文件
            for chunk_index in range(session.total_chunks):
                chunk_object_name = f"{session.object_name}.part{chunk_index}"
                try:
                    minio_client.delete_file(
                        session.bucket_name,
                        chunk_object_name
                    )
                except Exception as e:
                    logger.warning(f"删除临时分片失败: {chunk_object_name}, 错误: {e}")
            
            # 删除会话
            self.delete_session(session_id)
            
            logger.info(
                f"上传完成: {session_id}, 文件: {session.file_name}, "
                f"哈希: {file_hash}"
            )
            
            return {
                "session_id": session_id,
                "file_name": session.file_name,
                "file_size": session.file_size,
                "file_hash": file_hash,
                "object_name": session.object_name,
                "bucket_name": session.bucket_name
            }
            
        except Exception as e:
            logger.error(f"完成上传失败: {session_id}, 错误: {e}")
            raise
    
    def cancel_upload(self, session_id: str) -> None:
        """
        取消上传（删除所有临时文件）
        
        Args:
            session_id: 会话ID
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"上传会话不存在: {session_id}")
            return
        
        try:
            # 删除所有临时分片文件
            for chunk_index in range(session.total_chunks):
                chunk_object_name = f"{session.object_name}.part{chunk_index}"
                try:
                    if minio_client.file_exists(
                        session.bucket_name,
                        chunk_object_name
                    ):
                        minio_client.delete_file(
                            session.bucket_name,
                            chunk_object_name
                        )
                except Exception as e:
                    logger.warning(f"删除临时分片失败: {chunk_object_name}, 错误: {e}")
            
            # 删除会话
            self.delete_session(session_id)
            
            logger.info(f"取消上传: {session_id}")
            
        except Exception as e:
            logger.error(f"取消上传失败: {session_id}, 错误: {e}")
            raise
    
    def cleanup_expired_sessions(self) -> int:
        """
        清理过期的上传会话
        
        Returns:
            int: 清理的会话数量
        """
        now = datetime.utcnow()
        expire_time = now - timedelta(hours=self.SESSION_EXPIRE_HOURS)
        
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if session.updated_at < expire_time
        ]
        
        for session_id in expired_sessions:
            try:
                self.cancel_upload(session_id)
            except Exception as e:
                logger.error(f"清理过期会话失败: {session_id}, 错误: {e}")
        
        logger.info(f"清理过期会话: {len(expired_sessions)} 个")
        return len(expired_sessions)


# 全局上传管理器实例
upload_manager = UploadManager()
