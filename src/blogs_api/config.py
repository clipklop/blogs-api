from pydantic import BaseSettings, Field
from pydantic_settings import SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    sql_echo: bool = False
    database_connect_timeout: int = Field(default=5, ge=1)
    database_pool_timeout: int = Field(default=5, ge=1)
    algorithm: str = Field(default="HS256")
    secret_key: str = Field(default="1e161ee6687d59903b9c7776c7c23e6d2a9f47a93b25ef447b733e456230a66e")  # Replace with your actual secret key, like with openssl rand -hex 32
    access_token_expire_minutes: int = Field(default=30, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # env_prefix="BLOGS_",
        extra="ignore",
    )

settings = Settings()
