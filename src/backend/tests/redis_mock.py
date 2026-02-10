"""
Redis Mock模块 - 用于在没有Redis的环境中进行测试
模拟Redis连接和基本操作
"""

import asyncio
from typing import Any, Optional, Dict, List, Union
import json
import time


class RedisMock:
    """Redis模拟类 - 提供同步和异步方法"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    # 同步方法（用于security.py等同步代码）
    def setex(self, key: str, ex: int, value: Any) -> bool:
        """模拟Redis SETEX操作（同步）"""
        self._data[key] = value
        if ex:
            self._expiry[key] = time.time() + ex
        return True

    def exists(self, key: str) -> int:
        """模拟Redis EXISTS操作（同步）"""
        self._clean_expired()
        return 1 if key in self._data else 0

    # 异步方法（用于异步代码）
    async def async_get(self, key: str) -> Optional[str]:
        """模拟Redis GET操作"""
        self._clean_expired()
        value = self._data.get(key)
        if value is None:
            return None
        return json.dumps(value) if isinstance(value, (dict, list)) else str(value)

    async def async_set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """模拟Redis SET操作"""
        self._data[key] = value
        if ex:
            self._expiry[key] = time.time() + ex
        return True

    async def delete(self, key: str) -> int:
        """模拟Redis DELETE操作"""
        if key in self._data:
            del self._data[key]
            if key in self._expiry:
                del self._expiry[key]
            return 1
        return 0

    async def expire(self, key: str, ex: int) -> bool:
        """模拟Redis EXPIRE操作"""
        if key in self._data:
            self._expiry[key] = time.time() + ex
            return True
        return False
    
    async def ttl(self, key: str) -> int:
        """模拟Redis TTL操作"""
        if key not in self._data:
            return -2
        if key not in self._expiry:
            return -1
        remaining = self._expiry[key] - time.time()
        return max(0, int(remaining))
    
    async def hset(self, key: str, field: str, value: Any) -> int:
        """模拟Redis HSET操作"""
        if key not in self._data:
            self._data[key] = {}
        self._data[key][field] = value
        return 1
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """模拟Redis HGET操作"""
        self._clean_expired()
        if key not in self._data:
            return None
        value = self._data[key].get(field)
        if value is None:
            return None
        return json.dumps(value) if isinstance(value, (dict, list)) else str(value)
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        """模拟Redis HGETALL操作"""
        self._clean_expired()
        if key not in self._data:
            return {}
        result = {}
        for k, v in self._data[key].items():
            result[k] = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
        return result
    
    async def hdel(self, key: str, field: str) -> int:
        """模拟Redis HDEL操作"""
        if key in self._data and field in self._data[key]:
            del self._data[key][field]
            if not self._data[key]:
                del self._data[key]
            return 1
        return 0
    
    async def sadd(self, key: str, *members: Any) -> int:
        """模拟Redis SADD操作"""
        if key not in self._data:
            self._data[key] = set()
        added = 0
        for member in members:
            if member not in self._data[key]:
                self._data[key].add(member)
                added += 1
        return added
    
    async def smembers(self, key: str) -> List[str]:
        """模拟Redis SMEMBERS操作"""
        self._clean_expired()
        if key not in self._data:
            return []
        return [json.dumps(m) if isinstance(m, (dict, list)) else str(m) 
                for m in self._data[key]]
    
    async def srem(self, key: str, *members: Any) -> int:
        """模拟Redis SREM操作"""
        if key not in self._data:
            return 0
        removed = 0
        for member in members:
            if member in self._data[key]:
                self._data[key].remove(member)
                removed += 1
        if not self._data[key]:
            del self._data[key]
        return removed
    
    async def incr(self, key: str) -> int:
        """模拟Redis INCR操作"""
        current = int(self._data.get(key, 0))
        new_value = current + 1
        self._data[key] = new_value
        return new_value
    
    async def decr(self, key: str) -> int:
        """模拟Redis DECR操作"""
        current = int(self._data.get(key, 0))
        new_value = current - 1
        self._data[key] = new_value
        return new_value
    
    def _clean_expired(self):
        """清理过期的键"""
        current_time = time.time()
        expired_keys = [k for k, exp in self._expiry.items() if exp <= current_time]
        for key in expired_keys:
            if key in self._data:
                del self._data[key]
            del self._expiry[key]
    
    async def close(self):
        """模拟关闭连接"""
        self._data.clear()
        self._expiry.clear()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 全局Redis mock实例
_redis_mock = None


def get_redis_mock() -> RedisMock:
    """获取Redis mock实例"""
    global _redis_mock
    if _redis_mock is None:
        _redis_mock = RedisMock()
    return _redis_mock


async def create_redis_mock_connection():
    """创建Redis mock连接"""
    return get_redis_mock()


# 模拟Redis连接字符串
REDIS_MOCK_URL = "redis://mock:6379/0"


class RedisMockPool:
    """Redis连接池模拟"""
    
    def __init__(self):
        self.redis = get_redis_mock()
    
    async def acquire(self):
        return self.redis
    
    async def release(self, conn):
        pass
    
    async def close(self):
        await self.redis.close()


def create_redis_pool_mock():
    """创建Redis连接池mock"""
    return RedisMockPool()