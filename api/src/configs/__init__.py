from typing import ClassVar

from src.configs.base import BaseApplicationSettings
from src.configs.database import MongoSettings
from src.configs.application import AppSettings
from src.configs.rabbit import RabbitSettings


class ApplicationSettings(BaseApplicationSettings):
    app: ClassVar[AppSettings] = AppSettings()
    database: ClassVar[MongoSettings] = MongoSettings()
    rabbit: ClassVar[RabbitSettings] = RabbitSettings()


settings = ApplicationSettings()
