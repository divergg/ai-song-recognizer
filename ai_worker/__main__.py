import asyncio
from aio_pika import connect
from aio_pika.exceptions import AMQPConnectionError
from aio_pika.abc import AbstractChannel, AbstractExchange

from src.message_handler import message_handler
from src.configs import settings


from common_utils.log_util import setup_file_logger


logger = setup_file_logger(
    name="ai_setup_logger", log_file="ai_setup_logger.log")

async def setup_source(
    channel: AbstractChannel, exchange: AbstractExchange, source: str
):
    in_queue = await channel.declare_queue(f"incoming_{source}", durable=True)
    out_queue = await channel.declare_queue(f"outgoing_{source}")

    await in_queue.consume(
        message_handler(out_exchange=exchange, out_queue=out_queue), no_ack=True
    )

async def connect_with_retry(url, retries=5, delay=6):
    for attempt in range(1, retries + 1):
        try:
            return await connect(url)
        except (ConnectionRefusedError, AMQPConnectionError) as e:
            if attempt == retries:
                raise
            logger.info(f"Rabbit not ready, retry #{attempt} in {delay}s...")
            await asyncio.sleep(delay)



async def main():
    logger.info("Establishing a connection with RabbitMQ ....")
    connection = await connect_with_retry(settings.rabbit.url)
    logger.info(f"Connection is ready")

    async with connection:

        channel = await connection.channel()
        exchange = channel.default_exchange
        if settings.rabbit.queue_prefix is not None:
            prefix = settings.rabbit.queue_prefix
        else:
            prefix = ""
        await asyncio.gather(
            setup_source(channel, exchange, f"{prefix}"),
        )

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
