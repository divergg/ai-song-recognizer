import json
import asyncio
import uvicorn
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.exceptions import AMQPConnectionError
from typing import Optional, Iterable
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.utils.ws_fast_api import BotFastAPI
from src.utils.token import verify_token
from src.exceptions.exceptions import MethodNotAllowedError, InternalError, JsonDecodeError, MissingDataError
from src.repository.mongo_repo import MongodbRepository
from src.configs import settings
from src.adapter.models import WsOutEvent, WsNewMessageEvent, MessageData
from common_utils.log_util import setup_file_logger
from common_utils.schemas import UserMessage, StatusMessage, WsAuthRequest, Message, WsAuthResponse

logger = setup_file_logger(
    name="ws_adapter_logger", log_file="ws_adapter_looger.log")


class WsAdapter:

    client = MongodbRepository(database_url=settings.database.db_url,
                               database_name=settings.database.db_name)


    def __init__(
        self,
        rabbit_mq_url: str,
        host: str = "0.0.0.0",
        port: int = 7777,
        queue_prefix="",
        allow_origins: Optional[Iterable] = (),
    ):
        self.allow_origins = allow_origins
        self.host = host
        self.port = port
        self.app = BotFastAPI()
        self.methods = {
            "recognizeSong": self._recognize_song
        }
        self.rabbit_mq_url = rabbit_mq_url
        self.rabbit_outgoing_connection = None
        self.rabbit_incoming_connection = None
        self.rabbit_outgoing_channel = None
        self.exchange = None
        self.outgoing_queue = None
        self.queue_prefix = queue_prefix
        self.chat_data: dict[int, WsAuthRequest] = {}


    async def _handle_messages(
        self, websocket: WebSocket, chat_id: int, client_data: dict
    ):
        logger.info(f"method in request is: {client_data.get("method")}")
        method = self.methods.get(client_data.get("method"))
        if method is not None:
            try:
                await method(chat_id, client_data, websocket)
                logger.info(f"{chat_id}\t{method} successful")
                await websocket.send_json(
                    {
                        "type": "response",
                        "id": client_data["id"],
                        "data": {"success": True},
                    }
                )
            except ValidationError as error:
                logger.error(f"validate error: {error}")
                await websocket.send_json(json.loads(error.json()))
            except Exception as exc:
                logger.error(
                    f"{chat_id}\t{method} failed becaues of {exc}", exc_info=True
                )
                await websocket.send_json(
                    InternalError().to_json()
                )
        else:
            await websocket.send_json(
               MethodNotAllowedError().to_json()
            )

    async def _recognize_song(self, chat_id: str, client_data: dict, websocket):
        artist = client_data["artist"]
        title = client_data["title"]
        message_id = client_data["id"]
        logger.info(f"received title: {title}. received artist: {artist}")
        cache, countries = await self._find_result_in_cache(artist=artist, title=title)
        if cache:
            data = WsNewMessageEvent(
                data=MessageData(
                    user_message_id=message_id,
                    text=cache,
                    countries=countries,
                    title=title,
                    artist=artist,
                )
            )
            await websocket.send_text(data.model_dump_json())
        else:
            data = UserMessage(
                chat_id=chat_id,
                message_id=message_id,
                artist=artist,
                title=title
            )
            await self._recognize_song_request(data)

    async def _recognize_song_request(self, data: UserMessage):
        await self.send_to_rabbitmq(data)


    async def _find_result_in_cache(self, artist: str, title: str):
        result: dict = await self.client.find_one(collection_name=settings.database.collection_name,
                                    query={"artist": artist, "title": title})
        if result:
            return result.get('result', None), result.get('countries', [])
        return None, None

    async def _save_result_to_cache(self, artist: str, title: str, countries: list, result: str):
        result: dict = await self.client.insert_one(collection_name=settings.database.collection_name,
                                    query={"artist": artist, "title": title, "result": result, "countries": countries})


    async def send_to_rabbitmq(self, message: UserMessage):
        if not self.rabbit_outgoing_connection:
            self.rabbit_outgoing_connection = await self.connect_with_retry(self.rabbit_mq_url)
        if not self.rabbit_outgoing_channel:
            self.rabbit_outgoing_channel = (
                await self.rabbit_outgoing_connection.channel()
            )

        if not self.exchange:
            self.exchange = self.rabbit_outgoing_channel.default_exchange
        if not self.outgoing_queue:
            self.outgoing_queue = await self.rabbit_outgoing_channel.declare_queue(
                f"incoming_{self.queue_prefix}", durable=True
            )

        await self.exchange.publish(
            message.prepare(),
            routing_key=self.outgoing_queue.name,
        )

    async def connect_with_retry(self, url, retries=5, delay=3):
        for attempt in range(1, retries + 1):
            try:
                return await connect(url)
            except (ConnectionRefusedError, AMQPConnectionError) as e:
                if attempt == retries:
                    raise
                logger.info(f"Rabbit not ready, retry #{attempt} in {delay}s...")
                await asyncio.sleep(delay)

    async def listen_for_rabbitmq_responses(self):
        if not self.rabbit_incoming_connection:
            logger.info("Establishing a connection with RabbitMQ ....")
            self.rabbit_incoming_connection = await self.connect_with_retry(self.rabbit_mq_url)
            logger.info(f"Connection is ready")
        channel = await self.rabbit_incoming_connection.channel()
        queue = await channel.declare_queue(f"outgoing_{self.queue_prefix}")
        await queue.consume(self.handle_rabbit_message, no_ack=True)
        await asyncio.Future()

    async def handle_rabbit_message(self, message: AbstractIncomingMessage):
        msg = Message.from_rabbit_message(message)
        logger.info(f'Message for worker - {msg}')
        out_event = WsOutEvent.from_message(msg)
        for websocket in self.app.opened_ws.get(msg.chat_id, []):
            data: WsNewMessageEvent = out_event
            if data.event == 'newMessage' and "Something went wrong. Try again later" not in data.data.text:
                await self._save_result_to_cache(artist=data.data.artist,
                                                 title=data.data.title,
                                                 countries=data.data.countries,
                                                 result=data.data.text)
            await websocket.send_text(out_event.model_dump_json())

    def build_app(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.allow_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/status")
        async def status():
            """
            Check for status
            """
            return {"status": "ok"}

        @self.app.post(
            "/ws_auth", response_model=WsAuthResponse, response_model_exclude_unset=True
        )
        async def ws_auth(ws_auth_data: WsAuthRequest, verified=Depends(verify_token)):
            """
            Authentication in the app
            :return: The dictionary response containing the generated websocket URL.
            :rtype: dict
            """
            response = {"ws_url": f"/ws/{ws_auth_data.chat_id}"}
            self.chat_data[ws_auth_data.chat_id] = ws_auth_data
            return response

        @self.app.websocket("/ws/{chat_id}")
        async def websocket_endpoint(chat_id: str, websocket: WebSocket):
            """
            WebSocket endpoint for handling incoming websocket messages from the frontend.
            :param chat_id:
            :param websocket:
            :return: None
            """

            # Read an Authorization header
            authorization = websocket.headers.get("Authorization")
            verify_token(header_token=authorization)

            await websocket.accept()
            self.app.opened_ws[chat_id].append(websocket)
            try:
                while True:
                    message = await websocket.receive()
                    if message.get("type") == "websocket.disconnect":
                        raise WebSocketDisconnect
                    try:
                        client_data = json.loads(message.get("text"))
                        task = asyncio.create_task(
                            self._handle_messages(websocket, chat_id, client_data)
                        )
                        self.app.tasks[chat_id][id(task)] = task

                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        data = message.get("bytes")
                        if data is None:
                            logger.error('Json decode error')
                            await websocket.send_json(JsonDecodeError().to_json())
                    except Exception as e:
                        logger.error(e)
            except WebSocketDisconnect:
                if websocket in self.app.opened_ws[chat_id]:
                    self.app.opened_ws[chat_id].remove(websocket)
                logger.info(
                    f"{chat_id}\tWebSocket {chat_id} closed by client. "
                    f'{len(self.app.opened_ws["user_id"])} left'
                )
            except asyncio.CancelledError:
                logger.info(f"{chat_id}\tTask cancelled")
            finally:
                for task in self.app.tasks[chat_id].values():
                    task.cancel()
                del self.app.tasks[chat_id]

        @self.app.on_event("startup")
        def start_rabbitmq_listener():
            loop = asyncio.get_event_loop()
            loop.create_task(self.listen_for_rabbitmq_responses())

    def start_app_polling(self):
        self.build_app()
        logger.info("Running app")
        uvicorn.run(self.app, host=self.host, port=self.port)
