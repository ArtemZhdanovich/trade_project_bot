from dishka import make_async_container
from dishka.integrations.faststream import setup_dishka
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from account_events.src.config import Config
from account_events.src.controllers.amqp import controller
from account_events.src.infrastructure.broker import new_broker
from account_events.src.ioc import AppProvider


def get_faststream_app() -> FastStream:
    config = Config()
    broker = new_broker(config.rabbit)
    container = make_async_container(
        AppProvider(),
        context={
            Config: config, 
            RabbitBroker: broker
        }
    )
    faststream_app = FastStream(broker)
    setup_dishka(
        container=container, 
        app=faststream_app, 
        auto_inject=True
    )
    broker.include_router(controller)
    return faststream_app


if __name__ == "__main__":
    import uvicorn
    app = get_faststream_app()
    uvicorn.run(
        app="main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )