from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict  # 新增


class Settings(BaseSettings):
    PROJECT_NAME: str = "Dify HTTP Service"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "A service for handling HTTP requests in Dify"

    API_V1_STR: str = "/api/v1"

    # 服务配置
    DEBUG: bool = Field(True, env="DEBUG")
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(8000, env="APP_PORT")

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = Field(
        [],
        env="BACKEND_CORS_ORIGINS"
    )

    # 日志配置
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_PATH: str = Field("logs/app.log", env="LOG_PATH")
    LOG_CONSOLE: bool = Field(True, env="LOG_CONSOLE")

    # 新增配置，指定环境变量文件位置
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def get_settings():
    return Settings()
