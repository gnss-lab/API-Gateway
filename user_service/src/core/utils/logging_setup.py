import sys
from loguru import logger
from src.config.config import DICT_ENVS
from logstash.handler_tcp import TCPLogstashHandler

def logger_configuration() -> None:
    logger.remove()

    logger.add(TCPLogstashHandler(DICT_ENVS["LOGSTASH_HOST"], DICT_ENVS["LOGSTASH_PORT"], version=1, tags="PASS"), serialize=True, level="INFO")

    logger.add(
        sys.stdout, colorize=True, level="DEBUG",
        format="(<level>{level}</level>)({module}) [<cyan>{file}</cyan>:<cyan>{line}</cyan>] [<green>{time:HH:mm:ss}</green>] ➤ <level>{message}</level>")
