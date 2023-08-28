from core.rest_api.api import API
from typing import NoReturn
from core.logging.loguru_init import logger_configuration
from core.consul.consul_init import register_consul


def bootstrap() -> NoReturn:
    logger_configuration()
    register_consul()

    api = API()
    api.run_uvicorn_server()
