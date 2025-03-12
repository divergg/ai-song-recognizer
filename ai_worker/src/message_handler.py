from datetime import datetime
import asyncio
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange, AbstractQueue
from common_utils.schemas import (
    Message,
    UserMessage,
    StatusMessage,
    ResponseMessage,
)
from common_utils.log_util import setup_file_logger
from src.engine.worker import Engine
from src.engine.enums import QueryStatus

logger = setup_file_logger(
    name="ai_message_logger", log_file="ai_message_logger.log")


def create_status_callback(
    chat_id: str,
    message_id: str,
    out_exchange: AbstractExchange,
    out_queue: AbstractQueue,
):
    async def status_callback(status: QueryStatus):
        status_msg = None
        if status == QueryStatus.WAITING_FOR_RESPONSE:
            text = "Waiting for response..."
            status_msg = StatusMessage(
                chat_id=chat_id,
                user_message_id=message_id,
                text=text,
            )
        if status_msg:
            await out_exchange.publish(status_msg.prepare(), routing_key=out_queue.name)

    return status_callback


def message_handler(out_exchange: AbstractExchange, out_queue: AbstractQueue):
    engine = Engine()

    async def on_message(message: AbstractIncomingMessage) -> None:
        msg = Message.from_rabbit_message(message)
        if isinstance(msg, UserMessage):
            logger.info(f"Received message: {msg.message_id} {msg.title} {msg.artist}")
            try:
                process_coro = engine.query(
                    artist=msg.artist,
                    title=msg.title,
                )
                task = asyncio.wait_for(process_coro, timeout=200)
                result: dict = await task
            except Exception as e:
                logger.error(f"Failed to process message. Error {e}")
                result = {"response": "Something went wrong. Try again later", "countries": []}

            logger.info(f"{msg.message_id} Response: {result}")
            response_msg = ResponseMessage(
                chat_id=msg.chat_id, user_message_id=msg.message_id, response=result.get("response"), countries=result.get("countries")
            )
            await out_exchange.publish(
                response_msg.prepare(), routing_key=out_queue.name
            )

    return on_message
