"""
测试配置文件
使用SQLite内存数据库和内存缓存进行测试
"""
import os
from typing import Dict, Any

# 测试环境配置
TEST_CONFIG: Dict[str, Any] = {
    # 数据库配置 - 使用SQLite内存数据库
    "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    "DATABASE_ECHO": False,
    
    # Redis配置 - 使用内存模拟
    "REDIS_URL": "memory://",
    "REDIS_ENABLED": False,
    
    # JWT配置
    "SECRET_KEY": "test-secret-key-for-testing-only-change-in-production",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 30,
    "REFRESH_TOKEN_EXPIRE_DAYS": 7,
    
    # 安全配置
    "PASSWORD_MIN_LENGTH": 8,
    "PASSWORD_REQUIRE_UPPERCASE": True,
    "PASSWORD_REQUIRE_LOWERCASE": True,
    "PASSWORD_REQUIRE_DIGITS": True,
    "PASSWORD_REQUIRE_SPECIAL": False,
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOCKOUT_MINUTES": 30,
    
    # 文件上传配置
    "MAX_UPLOAD_SIZE": 10 * 1024 * 1024,  # 10MB
    "ALLOWED_EXTENSIONS": [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"],
    "UPLOAD_DIR": "/tmp/test_uploads",
    
    # 测试模式
    "TESTING": True,
    "DEBUG": True,
    
    # CORS配置
    "CORS_ORIGINS": ["http://localhost:3000", "http://127.0.0.1:3000"],
    
    # 应用配置
    "APP_NAME": "数据资产平台测试环境",
    "APP_VERSION": "1.0.0-test",
    
    # 邮件配置（测试模式禁用）
    "SMTP_ENABLED": False,
    "SMTP_HOST": "localhost",
    "SMTP_PORT": 25,
    "SMTP_USER": "",
    "SMTP_PASSWORD": "",
    
    # MinIO配置（测试模式禁用）
    "MINIO_ENABLED": False,
    "MINIO_ENDPOINT": "localhost:9000",
    "MINIO_ACCESS_KEY": "minioadmin",
    "MINIO_SECRET_KEY": "minioadmin",
    "MINIO_SECURE": False,
    
    # OCR配置
    "OCR_ENABLED": False,
    "TESSERACT_CMD": "/usr/bin/tesseract",
    
    # 会话配置
    "SESSION_TIMEOUT_MINUTES": 30,
    
    # 日志配置
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "/tmp/data_asset_test.log",
}


def get_test_settings():
    """获取测试配置"""
    return TEST_CONFIG


class TestSettings:
    """测试配置类"""
    
    def __init__(self):
        for key, value in TEST_CONFIG.items():
            setattr(self, key, value)
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return getattr(self, key, default)


# 创建测试配置实例
test_settings = TestSettings()