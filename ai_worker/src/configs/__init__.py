from typing import ClassVar

from src.configs.base import BaseApplicationSettings
from src.configs.ai import AISettings
from src.configs.rabbit import RabbitSettings
from src.configs.texts_api import RegogniseApiSettings


class ApplicationSettings(BaseApplicationSettings):
    ai: ClassVar[AISettings] = AISettings()
    rabbit: ClassVar[RabbitSettings] = RabbitSettings()
    recognize: ClassVar[RegogniseApiSettings] = RegogniseApiSettings()


settings = ApplicationSettings()
