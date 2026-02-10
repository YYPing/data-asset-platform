# 材料管理模块使用指南

## 快速开始

### 1. 文件位置

新创建的增强版文件：
```
src/backend/app/
├── utils/
│   ├── file_hash.py           # 文件哈希计算工具
│   ├── minio_client.py        # MinIO 客户端封装
│   └── upload_manager.py      # 上传管理器
├── schemas/
│   └── material.py            # Pydantic 模型（已更新）
├── services/
│   └── material_enhanced.py   # 材料服务增强版
└── api/v1/
    └── materials_enhanced.py  # API 路由增强版
```

### 2. 集成到现有项目

#### 方式一：替换现有文件（推荐）

如果要完全使用新功能，可以替换现有文件：

```bash
# 备份现有文件
cd src/backend/app
cp services/material.py services/material.py.bak
cp api/v1/materials.py api/v1/materials.py.bak

# 使用新文件
mv services/material_enhanced.py services/material.py
mv api/v1/materials_enhanced.py api/v1/materials.py
```

#### 方式二：并存使用

保留现有文件，新旧功能并存：

```python
# 在 app/api/v1/__init__.py 中同时注册两个路由
from app.api.v1 import materials, materials_enhanced

# 旧版路由：/api/v1/materials
app.include_router(materials.router)

# 新版路由：/api/v1/materials-v2
materials_enhanced.router.prefix = "/api/v1/materials-v2"
app.include_router(materials_enhanced.router)
```

### 3. 配置环境变量

确保 `.env` 文件包含以下配置：

```env
# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=materials

# 数据库配置
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/data_asset

# JWT 配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### 4. 安装依赖

```bash
pip install minio
```

### 5. 启动 MinIO（如果还没有）

```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```

访问 MinIO 控制台：http://localhost:9001

### 6. 测试 API

启动应用后，访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 主要功能

### 1. 分片上传大文件

```python
# 前端示例（JavaScript）
async function uploadLargeFile(file, assetId, materialName, stage) {
  // 1. 初始化上传
  const initResponse = await fetch('/api/v1/materials/upload', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      asset_id: assetId,
      material_name: materialName,
      stage: stage,
      file_name: file.name,
      file_size: file.size,
      is_required: true
    })
  });
  
  const { session_id, total_chunks, chunk_size } = await initResponse.json();
  
  // 2. 分片上传
  for (let i = 0; i < total_chunks; i++) {
    const start = i * chunk_size;
    const end = Math.min(start + chunk_size, file.size);
    const chunk = file.slice(start, end);
    
    const formData = new FormData();
    formData.append('chunk_index', i);
    formData.append('chunk_data', chunk);
    
    const chunkResponse = await fetch(`/api/v1/materials/${session_id}/upload-chunk`, {
      method: 'POST',
      body: formData
    });
    
    const { progress } = await chunkResponse.json();
    console.log(`上传进度: ${progress}%`);
  }
  
  // 3. 完成上传
  const completeFormData = new FormData();
  completeFormData.append('material_name', materialName);
  completeFormData.append('stage', stage);
  completeFormData.append('is_required', 'true');
  
  const completeResponse = await fetch(`/api/v1/materials/${session_id}/complete-upload`, {
    method: 'POST',
    body: completeFormData
  });
  
  const { material_id, file_hash } = await completeResponse.json();
  console.log(`上传完成！材料ID: ${material_id}, 哈希: ${file_hash}`);
}
```

### 2. 哈希验证

```bash
# 获取材料哈希
curl -X GET "http://localhost:8000/api/v1/materials/123/hash?algorithm=sha256" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 验证材料完整性
curl -X POST "http://localhost:8000/api/v1/materials/123/verify" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "expected_hash": "abc123...",
    "algorithm": "sha256"
  }'
```

### 3. 版本管理

```bash
# 创建新版本
curl -X POST "http://localhost:8000/api/v1/materials/123/versions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_hash": "def456...",
    "file_path": "path/to/new/version",
    "change_description": "更新数据范围"
  }'

# 获取版本历史
curl -X GET "http://localhost:8000/api/v1/materials/123/versions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 审核流程

```bash
# 提交审核
curl -X POST "http://localhost:8000/api/v1/materials/123/submit" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment": "请审核"}'

# 审核通过
curl -X POST "http://localhost:8000/api/v1/materials/123/approve" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment": "审核通过"}'

# 审核驳回
curl -X POST "http://localhost:8000/api/v1/materials/123/reject" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment": "缺少必要信息"}'
```

## 工具函数使用

### 文件哈希计算

```python
from app.utils.file_hash import calculate_file_hash, verify_file_hash

# 计算文件哈希
hash_value = calculate_file_hash("path/to/file.pdf", algorithm="sha256")
print(f"SHA256: {hash_value}")

# 验证文件哈希
is_valid = verify_file_hash("path/to/file.pdf", expected_hash, algorithm="sha256")
print(f"验证结果: {'通过' if is_valid else '失败'}")
```

### MinIO 操作

```python
from app.utils.minio_client import minio_client

# 上传文件
minio_client.upload_file(
    bucket_name="materials",
    object_name="asset_1/registration/file.pdf",
    file_path="local/path/file.pdf"
)

# 下载文件
minio_client.download_file(
    bucket_name="materials",
    object_name="asset_1/registration/file.pdf",
    file_path="local/path/downloaded.pdf"
)

# 生成预签名URL
url = minio_client.get_presigned_url(
    bucket_name="materials",
    object_name="asset_1/registration/file.pdf",
    expires=timedelta(hours=1)
)
print(f"下载链接: {url}")
```

### 上传管理器

```python
from app.utils.upload_manager import upload_manager

# 创建上传会话
session = upload_manager.create_session(
    session_id="uuid-xxx",
    file_name="large_file.pdf",
    file_size=52428800,  # 50MB
    bucket_name="materials",
    object_name="asset_1/registration/large_file.pdf"
)

# 上传分片
result = upload_manager.upload_chunk(
    session_id="uuid-xxx",
    chunk_index=0,
    chunk_data=chunk_bytes
)
print(f"进度: {result['progress']}%")

# 完成上传
result = await upload_manager.complete_upload(
    session_id="uuid-xxx",
    verify_hash="expected_hash"
)
print(f"文件哈希: {result['file_hash']}")
```

## 常见问题

### Q1: 如何修改分片大小？

```python
from app.utils.upload_manager import upload_manager

# 修改默认分片大小为 10MB
upload_manager.chunk_size = 10 * 1024 * 1024
```

### Q2: 如何修改最大文件大小？

```python
from app.utils.upload_manager import upload_manager

# 修改最大文件大小为 2GB
upload_manager.MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024
```

### Q3: 如何清理过期的上传会话？

```python
from app.utils.upload_manager import upload_manager

# 手动清理过期会话
cleaned_count = upload_manager.cleanup_expired_sessions()
print(f"清理了 {cleaned_count} 个过期会话")
```

建议设置定时任务（cron）定期清理：

```python
# 在 app/services/scheduler.py 中添加
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2)  # 每天凌晨2点执行
def cleanup_expired_uploads():
    from app.utils.upload_manager import upload_manager
    count = upload_manager.cleanup_expired_sessions()
    logger.info(f"清理过期上传会话: {count} 个")

scheduler.start()
```

### Q4: 如何支持更多哈希算法？

在 `app/utils/file_hash.py` 中添加新算法：

```python
import hashlib

def calculate_file_hash(file_path, algorithm="sha256"):
    if algorithm == "sha512":
        hasher = hashlib.sha512()
    # ... 其他算法
```

### Q5: 如何集成区块链存证？

在 `app/services/material_enhanced.py` 中扩展：

```python
async def store_hash_to_blockchain(self, file_hash: str) -> str:
    """将哈希存储到区块链"""
    # 调用区块链 API
    blockchain_tx = await blockchain_client.store_hash(file_hash)
    return blockchain_tx.transaction_id
```

## 性能优化建议

### 1. 启用 Redis 缓存

```python
# 缓存上传会话信息
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 在 upload_manager 中使用 Redis
def create_session(self, ...):
    session = UploadSession(...)
    # 存储到 Redis
    redis_client.setex(
        f"upload_session:{session_id}",
        86400,  # 24小时过期
        json.dumps(session.to_dict())
    )
```

### 2. 数据库索引优化

```sql
-- 为常用查询添加索引
CREATE INDEX idx_materials_asset_stage ON materials(asset_id, stage);
CREATE INDEX idx_materials_status ON materials(status);
CREATE INDEX idx_materials_uploaded_at ON materials(uploaded_at DESC);
```

### 3. 并发上传优化

```python
import asyncio

async def upload_chunks_concurrently(session_id, chunks):
    """并发上传多个分片"""
    tasks = [
        upload_manager.upload_chunk(session_id, i, chunk)
        for i, chunk in enumerate(chunks)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## 更多信息

详细的开发文档请参考：
- [COMPLETION_REPORT.md](./COMPLETION_REPORT.md) - 完整的开发报告
- [API 文档](http://localhost:8000/docs) - 在线 API 文档

如有问题，请联系开发团队。
