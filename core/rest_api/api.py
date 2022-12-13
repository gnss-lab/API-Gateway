from fastapi import FastAPI
from .routers import FileUpload
from .routers.mosgim_service import generate_map as mosgim_service__generate_map
from .routers.mosgim_service import ping_pong as mosgim_service__ping_pong
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
            db_path="./database/database.db"
        )

        fastapi_gateway_auto_generate.Generator(config=config)

    def __init_routes(self):
        self.__app.include_router(FileUpload.router)
        self.__app.include_router(mosgim_service__ping_pong.router)
        self.__app.include_router(mosgim_service__generate_map.router)
        logger.success("Routers initialized")

    def run_uvicorn_server(self):
        run_uvicorn_loguru(
            uvicorn.Config(
                app=self.__app,
                host=DICT_ENVS["IP_SERVER"],
                port=DICT_ENVS["PORT_SERVER"],
                log_level="info",
                # reload=True,
            )
        )
