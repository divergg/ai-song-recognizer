from pydantic_settings import SettingsConfigDict

from src.configs.base import BaseApplicationSettings


class MongoSettings(BaseApplicationSettings):
    host: str
    port: int
    db_name: str
    db_url: str
    collection_name: str
    model_config = SettingsConfigDict(env_prefix="MONGO_")
