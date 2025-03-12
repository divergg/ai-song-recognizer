import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseApplicationSettings(BaseSettings):
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")
