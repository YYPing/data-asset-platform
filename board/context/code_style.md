# 代码规范

## 后端 (Python/FastAPI)
- 异步函数: `async def`
- 类型注解: 所有函数参数和返回值
- 命名: snake_case（变量/函数），PascalCase（类）
- 依赖注入: `Depends(get_db)`, `Depends(get_current_user)`
- 错误处理: `raise HTTPException(status_code=400, detail={"code": 40001, "message": "..."})`
- 日志: `import logging; logger = logging.getLogger(__name__)`
- 分页响应: `{"code": 200, "data": {"items": [...], "total": N, "page": 1, "page_size": 20}}`

## 前端 (Vue 3/TypeScript)
- Composition API: `<script setup lang="ts">`
- 命名: PascalCase（组件），camelCase（变量/函数）
- 状态管理: Pinia `defineStore`
- API调用: 统一封装在 `src/api/` 目录
- 组件库: Element Plus，不手写基础CSS
- 类型: 所有API响应定义interface
