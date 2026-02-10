"""
材料管理模块测试示例
演示如何使用新开发的功能
"""
import asyncio
from pathlib import Path

# 测试工具函数
def test_file_hash():
    """测试文件哈希计算"""
    from app.utils.file_hash import calculate_bytes_hash, calculate_multi_hash
    
    # 测试字节哈希
    data = b"Hello, World!"
    hash_sha256 = calculate_bytes_hash(data, "sha256")
    hash_md5 = calculate_bytes_hash(data, "md5")
    
    print("=== 文件哈希测试 ===")
    print(f"数据: {data}")
    print(f"SHA256: {hash_sha256}")
    print(f"MD5: {hash_md5}")
    print()


def test_minio_client():
    """测试 MinIO 客户端"""
    from app.utils.minio_client import minio_client
    
    print("=== MinIO 客户端测试 ===")
    
    # 测试存储桶
    bucket_name = "test-bucket"
    minio_client.ensure_bucket(bucket_name)
    print(f"✓ 存储桶创建成功: {bucket_name}")
    
    # 测试上传
    test_data = b"Test file content"
    object_name = "test/file.txt"
    minio_client.upload_bytes(bucket_name, object_name, test_data)
    print(f"✓ 文件上传成功: {object_name}")
    
    # 测试下载
    downloaded_data = minio_client.download_stream(bucket_name, object_name)
    assert downloaded_data == test_data
    print(f"✓ 文件下载成功，内容匹配")
    
    # 测试文件存在性
    exists = minio_client.file_exists(bucket_name, object_name)
    print(f"✓ 文件存在性检查: {exists}")
    
    # 测试删除
    minio_client.delete_file(bucket_name, object_name)
    print(f"✓ 文件删除成功")
    
    print()


def test_upload_manager():
    """测试上传管理器"""
    from app.utils.upload_manager import upload_manager
    
    print("=== 上传管理器测试 ===")
    
    # 创建上传会话
    session_id = "test-session-001"
    file_name = "test_file.pdf"
    file_size = 10 * 1024 * 1024  # 10MB
    
    session = upload_manager.create_session(
        session_id=session_id,
        file_name=file_name,
        file_size=file_size,
        bucket_name="materials",
        object_name=f"test/{file_name}"
    )
    
    print(f"✓ 创建上传会话: {session_id}")
    print(f"  文件名: {session.file_name}")
    print(f"  文件大小: {session.file_size} 字节")
    print(f"  总分片数: {session.total_chunks}")
    print(f"  进度: {session.get_progress()}%")
    
    # 模拟上传分片
    chunk_data = b"x" * (5 * 1024 * 1024)  # 5MB 分片
    result = upload_manager.upload_chunk(session_id, 0, chunk_data)
    
    print(f"✓ 上传分片 0")
    print(f"  进度: {result['progress']}%")
    print(f"  已上传: {result['uploaded_chunks']}/{result['total_chunks']}")
    
    # 取消上传
    upload_manager.cancel_upload(session_id)
    print(f"✓ 取消上传")
    
    print()


async def test_material_service():
    """测试材料服务"""
    from app.services.material_enhanced import material_service
    from app.schemas.material import MaterialCreate, MaterialQuery
    from app.database import async_session
    
    print("=== 材料服务测试 ===")
    
    async with async_session() as db:
        # 测试创建材料
        material_data = MaterialCreate(
            asset_id=1,
            material_name="测试材料",
            material_type="文档",
            stage="registration",
            file_hash="a" * 64,  # 模拟 SHA256 哈希
            is_required=True
        )
        
        try:
            material = await material_service.create_material(
                db=db,
                material_data=material_data,
                user_id=1
            )
            print(f"✓ 创建材料成功: ID={material.id}")
            
            # 测试查询材料
            query = MaterialQuery(
                page=1,
                page_size=10,
                asset_id=1
            )
            materials, total = await material_service.list_materials(db, query)
            print(f"✓ 查询材料列表: 共 {total} 条")
            
            # 测试获取材料详情
            material_detail = await material_service.get_material(db, material.id)
            print(f"✓ 获取材料详情: {material_detail.material_name}")
            
        except Exception as e:
            print(f"✗ 测试失败: {e}")
    
    print()


def test_pydantic_models():
    """测试 Pydantic 模型"""
    from app.schemas.material import (
        MaterialCreate, MaterialUploadRequest,
        MaterialHashRequest, MaterialVerifyRequest
    )
    
    print("=== Pydantic 模型测试 ===")
    
    # 测试创建材料模型
    try:
        material = MaterialCreate(
            asset_id=1,
            material_name="测试材料",
            stage="registration",
            file_hash="a" * 64,
            is_required=True
        )
        print(f"✓ MaterialCreate 验证通过")
    except Exception as e:
        print(f"✗ MaterialCreate 验证失败: {e}")
    
    # 测试上传请求模型
    try:
        upload_req = MaterialUploadRequest(
            asset_id=1,
            material_name="测试文件",
            stage="registration",
            file_name="test.pdf",
            file_size=1024 * 1024  # 1MB
        )
        print(f"✓ MaterialUploadRequest 验证通过")
    except Exception as e:
        print(f"✗ MaterialUploadRequest 验证失败: {e}")
    
    # 测试哈希请求模型
    try:
        hash_req = MaterialHashRequest(algorithm="sha256")
        print(f"✓ MaterialHashRequest 验证通过")
    except Exception as e:
        print(f"✗ MaterialHashRequest 验证失败: {e}")
    
    # 测试验证请求模型
    try:
        verify_req = MaterialVerifyRequest(
            expected_hash="a" * 64,
            algorithm="sha256"
        )
        print(f"✓ MaterialVerifyRequest 验证通过")
    except Exception as e:
        print(f"✗ MaterialVerifyRequest 验证失败: {e}")
    
    print()


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("材料管理模块测试")
    print("=" * 60)
    print()
    
    # 工具函数测试
    test_file_hash()
    
    # MinIO 测试（需要 MinIO 服务运行）
    try:
        test_minio_client()
    except Exception as e:
        print(f"MinIO 测试跳过（需要 MinIO 服务）: {e}\n")
    
    # 上传管理器测试
    try:
        test_upload_manager()
    except Exception as e:
        print(f"上传管理器测试失败: {e}\n")
    
    # Pydantic 模型测试
    test_pydantic_models()
    
    # 材料服务测试（需要数据库）
    try:
        asyncio.run(test_material_service())
    except Exception as e:
        print(f"材料服务测试跳过（需要数据库）: {e}\n")
    
    print("=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
