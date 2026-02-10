"""
MinIO 对象存储客户端封装
提供文件上传、下载、删除等操作
"""
import io
import logging
from pathlib import Path
from typing import BinaryIO, Optional
from datetime import timedelta

from minio import Minio
from minio.error import S3Error
from minio.commonconfig import CopySource

from app.config import settings

logger = logging.getLogger(__name__)


class MinIOClient:
    """MinIO 客户端封装类"""
    
    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        secure: bool = False
    ):
        """
        初始化 MinIO 客户端
        
        Args:
            endpoint: MinIO 服务地址
            access_key: 访问密钥
            secret_key: 密钥
            secure: 是否使用 HTTPS
        """
        self.endpoint = endpoint or settings.MINIO_ENDPOINT
        self.access_key = access_key or settings.MINIO_ACCESS_KEY
        self.secret_key = secret_key or settings.MINIO_SECRET_KEY
        self.secure = secure
        
        # 创建 MinIO 客户端
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )
        
        logger.info(f"MinIO 客户端初始化成功: {self.endpoint}")
    
    def ensure_bucket(self, bucket_name: str) -> None:
        """
        确保存储桶存在，不存在则创建
        
        Args:
            bucket_name: 存储桶名称
        """
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"创建存储桶: {bucket_name}")
            else:
                logger.debug(f"存储桶已存在: {bucket_name}")
        except S3Error as e:
            logger.error(f"确保存储桶失败: {e}")
            raise
    
    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: str | Path,
        content_type: str = "application/octet-stream",
        metadata: dict = None
    ) -> str:
        """
        上传文件到 MinIO
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            file_path: 本地文件路径
            content_type: 内容类型
            metadata: 元数据
            
        Returns:
            str: 对象名称
            
        Raises:
            S3Error: 上传失败
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 确保存储桶存在
            self.ensure_bucket(bucket_name)
            
            # 上传文件
            self.client.fput_object(
                bucket_name,
                object_name,
                str(file_path),
                content_type=content_type,
                metadata=metadata
            )
            
            logger.info(f"文件上传成功: {bucket_name}/{object_name}")
            return object_name
            
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            raise
    
    def upload_stream(
        self,
        bucket_name: str,
        object_name: str,
        data: BinaryIO,
        length: int,
        content_type: str = "application/octet-stream",
        metadata: dict = None
    ) -> str:
        """
        上传数据流到 MinIO
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            data: 二进制数据流
            length: 数据长度
            content_type: 内容类型
            metadata: 元数据
            
        Returns:
            str: 对象名称
            
        Raises:
            S3Error: 上传失败
        """
        try:
            # 确保存储桶存在
            self.ensure_bucket(bucket_name)
            
            # 上传数据流
            self.client.put_object(
                bucket_name,
                object_name,
                data,
                length,
                content_type=content_type,
                metadata=metadata
            )
            
            logger.info(f"数据流上传成功: {bucket_name}/{object_name}")
            return object_name
            
        except S3Error as e:
            logger.error(f"数据流上传失败: {e}")
            raise
    
    def upload_bytes(
        self,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: dict = None
    ) -> str:
        """
        上传字节数据到 MinIO
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            data: 字节数据
            content_type: 内容类型
            metadata: 元数据
            
        Returns:
            str: 对象名称
        """
        stream = io.BytesIO(data)
        return self.upload_stream(
            bucket_name,
            object_name,
            stream,
            len(data),
            content_type,
            metadata
        )
    
    def download_file(
        self,
        bucket_name: str,
        object_name: str,
        file_path: str | Path
    ) -> Path:
        """
        从 MinIO 下载文件
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            file_path: 本地保存路径
            
        Returns:
            Path: 本地文件路径
            
        Raises:
            S3Error: 下载失败
        """
        try:
            file_path = Path(file_path)
            
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            self.client.fget_object(
                bucket_name,
                object_name,
                str(file_path)
            )
            
            logger.info(f"文件下载成功: {bucket_name}/{object_name} -> {file_path}")
            return file_path
            
        except S3Error as e:
            logger.error(f"文件下载失败: {e}")
            raise
    
    def download_stream(
        self,
        bucket_name: str,
        object_name: str
    ) -> bytes:
        """
        从 MinIO 下载文件为字节数据
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            
        Returns:
            bytes: 文件内容
            
        Raises:
            S3Error: 下载失败
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            
            logger.info(f"数据流下载成功: {bucket_name}/{object_name}")
            return data
            
        except S3Error as e:
            logger.error(f"数据流下载失败: {e}")
            raise
    
    def delete_file(
        self,
        bucket_name: str,
        object_name: str
    ) -> None:
        """
        删除 MinIO 中的文件
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            
        Raises:
            S3Error: 删除失败
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"文件删除成功: {bucket_name}/{object_name}")
            
        except S3Error as e:
            logger.error(f"文件删除失败: {e}")
            raise
    
    def file_exists(
        self,
        bucket_name: str,
        object_name: str
    ) -> bool:
        """
        检查文件是否存在
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            
        Returns:
            bool: 文件是否存在
        """
        try:
            self.client.stat_object(bucket_name, object_name)
            return True
        except S3Error:
            return False
    
    def get_file_info(
        self,
        bucket_name: str,
        object_name: str
    ) -> dict:
        """
        获取文件信息
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            
        Returns:
            dict: 文件信息（大小、修改时间等）
            
        Raises:
            S3Error: 获取失败
        """
        try:
            stat = self.client.stat_object(bucket_name, object_name)
            return {
                "size": stat.size,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "last_modified": stat.last_modified,
                "metadata": stat.metadata
            }
        except S3Error as e:
            logger.error(f"获取文件信息失败: {e}")
            raise
    
    def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """
        生成预签名 URL（用于临时访问）
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称（存储路径）
            expires: 过期时间
            
        Returns:
            str: 预签名 URL
            
        Raises:
            S3Error: 生成失败
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name,
                object_name,
                expires=expires
            )
            logger.info(f"生成预签名 URL: {bucket_name}/{object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"生成预签名 URL 失败: {e}")
            raise
    
    def copy_file(
        self,
        source_bucket: str,
        source_object: str,
        dest_bucket: str,
        dest_object: str
    ) -> None:
        """
        复制文件
        
        Args:
            source_bucket: 源存储桶
            source_object: 源对象名称
            dest_bucket: 目标存储桶
            dest_object: 目标对象名称
            
        Raises:
            S3Error: 复制失败
        """
        try:
            # 确保目标存储桶存在
            self.ensure_bucket(dest_bucket)
            
            # 复制文件
            self.client.copy_object(
                dest_bucket,
                dest_object,
                CopySource(source_bucket, source_object)
            )
            
            logger.info(
                f"文件复制成功: {source_bucket}/{source_object} -> "
                f"{dest_bucket}/{dest_object}"
            )
            
        except S3Error as e:
            logger.error(f"文件复制失败: {e}")
            raise
    
    def list_objects(
        self,
        bucket_name: str,
        prefix: str = "",
        recursive: bool = True
    ) -> list[dict]:
        """
        列出存储桶中的对象
        
        Args:
            bucket_name: 存储桶名称
            prefix: 对象名称前缀
            recursive: 是否递归列出
            
        Returns:
            list: 对象信息列表
        """
        try:
            objects = self.client.list_objects(
                bucket_name,
                prefix=prefix,
                recursive=recursive
            )
            
            result = []
            for obj in objects:
                result.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "etag": obj.etag,
                    "last_modified": obj.last_modified,
                    "is_dir": obj.is_dir
                })
            
            return result
            
        except S3Error as e:
            logger.error(f"列出对象失败: {e}")
            raise


# 全局 MinIO 客户端实例
minio_client = MinIOClient()
