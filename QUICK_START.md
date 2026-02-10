# 快速开始指南

## 🚀 5分钟快速上手

### 前置条件

- Python 3.9+
- PostgreSQL 12+
- MinIO（或兼容的 S3 存储）
- Redis（可选，用于缓存）

### 1. 安装依赖

```bash
cd /Users/yyp/.openclaw/workspace/data-asset-platform
pip install -r requirements.txt
```

如果 `requirements.txt` 中没有 MinIO，手动安装：

```bash
pip install minio
```

### 2. 启动 MinIO

使用 Docker 快速启动：

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
用户名：`minioadmin`  
密码：`minioadmin`

### 3. 配置环境变量

编辑 `.env` 文件：

```env
# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=materials

# 数据库配置
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/data_asset

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

### 4. 集成新模块

#### 方式一：替换现有文件（推荐）

```bash
cd src/backend/app

# 备份现有文件
cp services/material.py services/material.py.bak
cp api/v1/materials.py api/v1/materials.py.bak

# 使用新文件
mv services/material_enhanced.py services/material.py
mv api/v1/materials_enhanced.py api/v1/materials.py
```

#### 方式二：并存使用

在 `app/main.py` 或路由注册文件中：

```python
from app.api.v1 import materials_enhanced

# 注册新版路由
materials_enhanced.router.prefix = "/api/v1/materials-v2"
app.include_router(materials_enhanced.router)
```

### 5. 启动应用

```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 6. 验证安装

访问 API 文档：http://localhost:8000/docs

测试健康检查：

```bash
curl http://localhost:8000/health
```

### 7. 测试上传功能

使用 Postman 导入集合：

```bash
# 导入 Material_API.postman_collection.json
```

或使用 curl 测试：

```bash
# 1. 初始化上传
curl -X POST "http://localhost:8000/api/v1/materials/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_id": 1,
    "material_name": "测试文件",
    "stage": "registration",
    "file_name": "test.pdf",
    "file_size": 1048576
  }'

# 2. 上传分片（使用返回的 session_id）
curl -X POST "http://localhost:8000/api/v1/materials/{session_id}/upload-chunk" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "chunk_index=0" \
  -F "chunk_data=@/path/to/chunk/file"

# 3. 完成上传
curl -X POST "http://localhost:8000/api/v1/materials/{session_id}/complete-upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "material_name=测试文件" \
  -F "stage=registration" \
  -F "is_required=true"
```

---

## 📚 完整文档

- [完成报告](./COMPLETION_REPORT.md) - 详细的开发文档
- [使用指南](./MATERIAL_MODULE_GUIDE.md) - 功能使用说明
- [API 文档](http://localhost:8000/docs) - 在线 API 文档

---

## 🧪 运行测试

```bash
# 运行测试脚本
python test_material_module.py
```

---

## 🌐 前端演示

打开 `demo.html` 文件：

```bash
# 使用 Python 启动简单的 HTTP 服务器
python -m http.server 8080

# 访问 http://localhost:8080/demo.html
```

**注意**：需要先配置正确的 JWT 令牌。

---

## 🔧 常见问题

### Q1: MinIO 连接失败

**错误**: `Connection refused` 或 `MinIO bucket error`

**解决**:
1. 确保 MinIO 服务已启动：`docker ps | grep minio`
2. 检查端口是否被占用：`lsof -i :9000`
3. 验证配置：`.env` 中的 `MINIO_ENDPOINT` 是否正确

### Q2: 数据库连接失败

**错误**: `Connection to database failed`

**解决**:
1. 确保 PostgreSQL 服务已启动
2. 检查数据库是否存在：`psql -U admin -d data_asset`
3. 运行数据库迁移：`alembic upgrade head`

### Q3: 认证失败

**错误**: `401 Unauthorized`

**解决**:
1. 确保请求头包含有效的 JWT 令牌
2. 检查令牌是否过期
3. 验证 `SECRET_KEY` 配置是否正确

### Q4: 文件上传失败

**错误**: `Upload failed` 或 `Chunk upload error`

**解决**:
1. 检查文件大小是否超过限制（1GB）
2. 确保 MinIO 存储桶存在
3. 检查网络连接和超时设置
4. 查看服务器日志获取详细错误信息

### Q5: 分片上传中断后如何恢复？

**解决**:
1. 使用相同的 `session_id` 继续上传
2. 调用 API 获取已上传的分片列表
3. 只上传缺失的分片
4. 完成上传

---

## 📊 性能优化建议

### 1. 启用 Redis 缓存

```python
# 安装 Redis
pip install redis

# 配置 Redis
REDIS_URL=redis://localhost:6379/0
```

### 2. 数据库索引优化

```sql
-- 为常用查询添加索引
CREATE INDEX idx_materials_asset_stage ON materials(asset_id, stage);
CREATE INDEX idx_materials_status ON materials(status);
CREATE INDEX idx_materials_uploaded_at ON materials(uploaded_at DESC);
```

### 3. 并发上传优化

前端使用 Web Workers 并发上传多个分片：

```javascript
// 创建 Worker 池
const workers = [];
for (let i = 0; i < 4; i++) {
  workers.push(new Worker('upload-worker.js'));
}

// 分配任务到 Worker
chunks.forEach((chunk, index) => {
  const worker = workers[index % workers.length];
  worker.postMessage({ chunk, index });
});
```

### 4. CDN 加速

配置 MinIO 前置 CDN：

```nginx
# Nginx 配置
upstream minio {
  server localhost:9000;
}

server {
  listen 80;
  server_name cdn.example.com;

  location / {
    proxy_pass http://minio;
    proxy_cache my_cache;
    proxy_cache_valid 200 1h;
  }
}
```

---

## 🔐 安全建议

### 1. 生产环境配置

```env
# 使用强密码
SECRET_KEY=$(openssl rand -hex 32)
MINIO_ACCESS_KEY=$(openssl rand -hex 16)
MINIO_SECRET_KEY=$(openssl rand -hex 32)

# 启用 HTTPS
MINIO_ENDPOINT=minio.example.com:443
```

### 2. 文件类型验证

```python
# 在服务层添加文件类型白名单
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.png', '.docx', '.xlsx'}

def validate_file_extension(filename):
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {ext}")
```

### 3. 病毒扫描

集成 ClamAV 进行病毒扫描：

```python
import pyclamd

def scan_file(file_path):
    cd = pyclamd.ClamdUnixSocket()
    result = cd.scan_file(file_path)
    if result:
        raise ValueError("文件包含病毒")
```

---

## 📞 获取帮助

- 查看 [完成报告](./COMPLETION_REPORT.md) 了解详细功能
- 查看 [使用指南](./MATERIAL_MODULE_GUIDE.md) 了解使用方法
- 查看 [API 文档](http://localhost:8000/docs) 了解接口详情

如有问题，请联系开发团队。

---

**祝使用愉快！** 🎉
