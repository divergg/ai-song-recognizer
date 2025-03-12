from pydantic_settings import SettingsConfigDict

from src.configs.base import BaseApplicationSettings


class AISettings(BaseApplicationSettings):
    model: str = "gpt-4o-2024-08-06"
    token: str
    proxy_url: str = ""
    model_config = SettingsConfigDict(env_prefix="AI_")
