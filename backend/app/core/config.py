from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "数据资产管理平台"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/data_asset"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    UPLOAD_DIR: str = "./uploads"

    class Config:
        env_file = ".env"


settings = Settings()
