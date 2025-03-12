from pydantic_settings import SettingsConfigDict

from src.configs.base import BaseApplicationSettings


class AppSettings(BaseApplicationSettings):
    host: str = "0.0.0.0"
    port: int
    token: str
    model_config = SettingsConfigDict(env_prefix="APP_")
