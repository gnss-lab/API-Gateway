import sys
import logstash
from loguru import logger
from core.config.envs import DICT_ENVS
from uvicorn_loguru_integration import run_uvicorn_loguru
from logstash.handler_tcp import TCPLogstashHandler


def logger_configuration() -> None:
    logger.remove()

    # logger.add("./logs/logs.log", format="({time}) {level} {message}",
    #            level="DEBUG", rotation="10 KB", compression="zip", serialize=True)

    logger.add(TCPLogstashHandler(DICT_ENVS["LOGSTASH_HOST"], DICT_ENVS["LOGSTASH_PORT"], version=1, tags="PASS"), serialize=True, level="INFO")

    logger.add(
        sys.stdout, colorize=True, level="DEBUG",
        format="(<level>{level}</level>)({module}) [<cyan>{file}</cyan>:<cyan>{line}</cyan>] [<green>{time:HH:mm:ss}</green>] ➤ <level>{message}</level>")
