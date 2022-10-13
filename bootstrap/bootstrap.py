from core.rest_api.api import API
from typing import NoReturn
from core.logging.loguru_init import logger_configuration


def bootstrap() -> NoReturn:
    logger_configuration()

    api = API()
    api.run_uvicorn_server()
