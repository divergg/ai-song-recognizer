from pydantic_settings import SettingsConfigDict

from src.configs.base import BaseApplicationSettings


class RegogniseApiSettings(BaseApplicationSettings):
    lyrics_url: str = "https://api.lyrics.ovh/v1"
    model_config = SettingsConfigDict(env_prefix="RECOGNIZE_")
