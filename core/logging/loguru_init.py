import sys
from loguru import logger
from uvicorn_loguru_integration import run_uvicorn_loguru


def logger_configuration() -> None:
    # TODO: Добавить создание папки logs если её нету

    # logger.add("./logs/logs.log", format="({time}) {level} {message}",
    #            level="DEBUG", rotation="10 KB", compression="zip", serialize=True)

    logger.remove()

    logger.add(
        sys.stdout, colorize=True,
        format="(<level>{level}</level>) [<green>{time:HH:mm:ss}</green>] ➤ <level>{message}</level>")