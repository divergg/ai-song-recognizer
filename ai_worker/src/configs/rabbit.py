from pydantic_settings import SettingsConfigDict

from src.configs.base import BaseApplicationSettings


class RabbitSettings(BaseApplicationSettings):
    url: str
    queue_prefix: str = "song"
    model_config = SettingsConfigDict(env_prefix="RABBIT_")
