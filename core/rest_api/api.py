from fastapi import FastAPI
from loguru import logger
from uvicorn_loguru_integration import run_uvicorn_loguru
import uvicorn

import fastapi_gateway_auto_generate
from core.config.envs import DICT_ENVS


class API:
    def __init__(self):
        self.__app: FastAPI = FastAPI(debug=True)
        self.__init_routes()

        config: fastapi_gateway_auto_generate.Config = fastapi_gateway_auto_generate.Config(
            fast_api_app=self.__app,
            db_path=DICT_ENVS["DATABASE_PATH"] # "./database/database.db"
        )

        fastapi_gateway_auto_generate.Generator(config=config)

    def __init_routes(self):
        logger.success("Routers initialized")

    def run_uvicorn_server(self):
        run_uvicorn_loguru(
            uvicorn.Config(
                app=self.__app,
                host=DICT_ENVS["FASTAPI_IP"],
                port=DICT_ENVS["FASTAPI_PORT"],
                log_level="info",
                # reload=True,
            )
        )
