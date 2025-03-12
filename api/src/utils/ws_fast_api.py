from collections import defaultdict
from starlette.websockets import WebSocket
from typing import Dict
from fastapi import FastAPI
import asyncio



class BotFastAPI(FastAPI):
    """
    FastAPI app with opened web socket storage
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opened_ws: dict[str, list[WebSocket]] = defaultdict(list)
        self.tasks: Dict[str, dict] = defaultdict(dict)
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
