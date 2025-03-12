from src.configs import settings
from src.adapter.ws_adapter import WsAdapter


if __name__ == "__main__":
    adapter = WsAdapter(
        port=settings.app.port,
        host=settings.app.host,
        queue_prefix=settings.rabbit.queue_prefix,
        rabbit_mq_url=settings.rabbit.url,
        allow_origins=["*"]
    )

    adapter.start_app_polling()
