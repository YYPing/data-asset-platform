# 数据资产CRUD API - 快速开始指南

## 概述

本模块实现了数据资产管理平台的核心业务功能，包括：
- ✅ 完整的CRUD操作
- ✅ 版本控制（创建版本、查看历史、回滚）
- ✅ 状态流转（草稿→提交→审核→登记→注销）
- ✅ 中文分词全文搜索（基于PostgreSQL zhparser）
- ✅ 完整的审计日志

## 前置要求

### 1. PostgreSQL扩展配置

安装并配置zhparser中文分词扩展：

```sql
-- 1. 安装扩展（需要先安装zhparser插件）
CREATE EXTENSION IF NOT EXISTS zhparser;

-- 2. 创建中文分词配置
CREATE TEXT SEARCH CONFIGURATION chinese_zh (PARSER = zhparser);

-- 3. 添加词性映射
ALTER TEXT SEARCH CONFIGURATION chinese_zh 
ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 4. 创建GIN索引（加速搜索）
CREATE INDEX idx_data_assets_search ON data_assets USING gin(search_vector);
```

### 2. 数据库触发器（可选，推荐）

自动更新搜索向量：

```sql
CREATE OR REPLACE FUNCTION update_asset_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := 
    setweight(to_tsvector('chinese_zh', COALESCE(NEW.asset_code, '')), 'A') ||
    setweight(to_tsvector('chinese_zh', COALESCE(NEW.asset_name, '')), 'A') ||
    setweight(to_tsvector('chinese_zh', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('chinese_zh', COALESCE(NEW.data_source, '')), 'C') ||
    setweight(to_tsvector('chinese_zh', COALESCE(NEW.category, '')), 'D') ||
    setweight(to_tsvector('chinese_zh', COALESCE(NEW.asset_type, '')), 'D');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_asset_search_vector
BEFORE INSERT OR UPDATE ON data_assets
FOR EACH ROW
EXECUTE FUNCTION update_asset_search_vector();
```

## API使用示例

### 1. 基础CRUD操作

#### 创建资产
```bash
curl -X POST "http://localhost:8000/api/v1/assets" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_name": "用户行为数据集",
    "organization_id": 1,
    "category": "business",
    "data_classification": "internal",
    "sensitivity_level": "medium",
    "description": "包含用户浏览、点击、购买等行为数据",
    "data_source": "Web应用日志",
    "data_volume": "10TB",
    "data_format": "JSON",
    "update_frequency": "每日",
    "asset_type": "结构化数据",
    "estimated_value": 1000000.00
  }'
```

#### 获取资产列表
```bash
curl -X GET "http://localhost:8000/api/v1/assets?page=1&page_size=20&status=draft" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 更新资产
```bash
curl -X PUT "http://localhost:8000/api/v1/assets/123" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "更新后的描述",
    "data_volume": "15TB"
  }'
```

#### 删除资产（软删除）
```bash
curl -X DELETE "http://localhost:8000/api/v1/assets/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 状态流转操作

#### 提交审核
```bash
curl -X POST "http://localhost:8000/api/v1/assets/123/submit" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 审核通过
```bash
curl -X POST "http://localhost:8000/api/v1/assets/123/approve" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "资料齐全，符合登记要求"
  }'
```

#### 审核驳回
```bash
curl -X POST "http://localhost:8000/api/v1/assets/123/reject" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "数据来源说明不清晰，请补充"
  }'
```

#### 完成登记
```bash
curl -X POST "http://localhost:8000/api/v1/assets/123/register" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "登记完成",
    "certificate_no": "CERT-2026-001"
  }'
```

#### 注销资产
```bash
curl -X POST "http://localhost:8000/api/v1/assets/123/cancel" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "数据已过期，不再使用"
  }'
```

### 3. 版本控制操作

#### 创建新版本
```bash
curl -X POST "http://localhost:8000/api/v1/assets/123/versions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "更新数据量和更新频率信息"
  }'
```

#### 获取版本历史
```bash
curl -X GET "http://localhost:8000/api/v1/assets/123/versions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 回滚到指定版本
```bash
curl -X POST "http://localhost:8000/api/v1/assets/123/versions/456/rollback" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 搜索功能

#### 简单搜索
```bash
curl -X GET "http://localhost:8000/api/v1/assets/search?q=用户行为&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 高级搜索（中文分词）
```bash
curl -X POST "http://localhost:8000/api/v1/assets/search/advanced" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "用户行为数据",
    "status": ["approved", "registered"],
    "stage": ["operation"],
    "category": ["business"],
    "data_classification": ["internal", "confidential"],
    "sensitivity_level": ["medium", "high"],
    "date_from": "2026-01-01T00:00:00Z",
    "date_to": "2026-12-31T23:59:59Z",
    "page": 1,
    "page_size": 20,
    "use_fulltext": true
  }'
```

## 状态流转图

```
┌─────────┐
│  draft  │ 草稿
└────┬────┘
     │ submit
     ▼
┌───────────┐
│ submitted │ 已提交
└─────┬─────┘
      │
      ├─── approve ───┐
      │               ▼
      │         ┌──────────┐
      │         │ approved │ 已审核
      │         └────┬─────┘
      │              │ register
      │              ▼
      │         ┌────────────┐
      │         │ registered │ 已登记
      │         └─────┬──────┘
      │               │ cancel
      │               ▼
      │         ┌───────────┐
      │         │ cancelled │ 已注销
      │         └───────────┘
      │
      └─── reject ───┐
                     ▼
               ┌──────────┐
               │ rejected │ 已驳回
               └────┬─────┘
                    │ 修改后重新提交
                    └──────────────┐
                                   ▼
                              ┌─────────┐
                              │  draft  │
                              └─────────┘
```

## 权限说明

### 角色权限矩阵

| 操作 | holder_user | holder_admin | reviewer | admin |
|------|-------------|--------------|----------|-------|
| 创建资产 | ✅ | ✅ | ✅ | ✅ |
| 查看资产 | ✅（本组织） | ✅（本组织） | ✅（所有） | ✅（所有） |
| 编辑资产 | ✅（本组织） | ✅（本组织） | ❌ | ✅（所有） |
| 删除资产 | ✅（本组织） | ✅（本组织） | ❌ | ✅（所有） |
| 提交审核 | ✅（本组织） | ✅（本组织） | ❌ | ✅（所有） |
| 审核通过 | ❌ | ❌ | ✅ | ✅ |
| 审核驳回 | ❌ | ❌ | ✅ | ✅ |
| 完成登记 | ❌ | ❌ | ❌ | ✅ |
| 注销资产 | ❌ | ❌ | ❌ | ✅ |
| 创建版本 | ✅（本组织） | ✅（本组织） | ❌ | ✅（所有） |
| 回滚版本 | ✅（本组织） | ✅（本组织） | ❌ | ✅（所有） |

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 123,
    "asset_code": "DA-20260210-0001",
    "asset_name": "用户行为数据集",
    "status": "draft",
    "current_stage": "registration",
    "version": 1,
    "created_at": "2026-02-10T10:00:00Z",
    "updated_at": "2026-02-10T10:00:00Z"
  }
}
```

### 错误响应
```json
{
  "detail": "Asset not found"
}
```

## 审计日志

所有关键操作都会自动记录到`operation_logs`表，包括：
- 操作类型（create/update/delete/submit/approve/reject/register/cancel等）
- 操作用户
- 目标资产
- 操作描述
- 客户端IP和User-Agent
- 操作时间
- 操作结果

查询审计日志示例：
```sql
SELECT 
  ol.id,
  ol.operation_type,
  ol.description,
  ol.created_at,
  u.username,
  ol.ip_address
FROM operation_logs ol
LEFT JOIN users u ON ol.user_id = u.id
WHERE ol.target_type = 'asset'
  AND ol.target_id = 123
ORDER BY ol.created_at DESC;
```

## 性能优化建议

### 1. 数据库索引
确保以下索引已创建：
```sql
-- 搜索向量索引
CREATE INDEX idx_data_assets_search ON data_assets USING gin(search_vector);

-- 常用查询索引
CREATE INDEX idx_data_assets_org_status ON data_assets(organization_id, status);
CREATE INDEX idx_data_assets_stage_status ON data_assets(current_stage, status);
CREATE INDEX idx_data_assets_created_at ON data_assets(created_at DESC);
```

### 2. 缓存策略
- 使用Redis缓存热门搜索结果
- 缓存资产详情（TTL: 5分钟）
- 缓存版本历史（TTL: 10分钟）

### 3. 异步处理
- 审计日志记录可以异步化
- 搜索向量更新可以异步化
- 通知发送可以异步化

## 故障排查

### 1. 搜索功能不工作
检查zhparser扩展是否正确安装：
```sql
SELECT * FROM pg_extension WHERE extname = 'zhparser';
SELECT * FROM pg_ts_config WHERE cfgname = 'chinese_zh';
```

### 2. 搜索结果不准确
手动更新搜索向量：
```python
from app.utils.search import SearchService

# 更新单个资产
await SearchService.update_search_vector(db, asset_id=123)

# 批量更新所有资产
UPDATE data_assets
SET search_vector = 
  setweight(to_tsvector('chinese_zh', COALESCE(asset_code, '')), 'A') ||
  setweight(to_tsvector('chinese_zh', COALESCE(asset_name, '')), 'A') ||
  setweight(to_tsvector('chinese_zh', COALESCE(description, '')), 'B') ||
  setweight(to_tsvector('chinese_zh', COALESCE(data_source, '')), 'C') ||
  setweight(to_tsvector('chinese_zh', COALESCE(category, '')), 'D') ||
  setweight(to_tsvector('chinese_zh', COALESCE(asset_type, '')), 'D')
WHERE deleted_at IS NULL;
```

### 3. 权限错误
检查用户角色和组织ID：
```sql
SELECT id, username, role, organization_id FROM users WHERE id = YOUR_USER_ID;
```

## 开发团队

- **后端开发**: Backend Development Expert
- **开发日期**: 2026-02-10
- **版本**: 1.0.0

## 相关文档

- [完成报告](./COMPLETION_REPORT.md) - 详细的开发完成报告
- [API文档](./docs/api.md) - 完整的API文档（待生成）
- [数据库设计](./docs/database.md) - 数据库表结构设计（待生成）

## 联系方式

如有问题或建议，请联系开发团队。
