import time
from fastapi import FastAPI, Request
from loguru import logger
from uvicorn_loguru_integration import run_uvicorn_loguru
import uvicorn

import fastapi_gateway_auto_generate

from core.config.calery_config import settings
from core.config.calery_utils import create_celery
from core.config.envs import DICT_ENVS
from core.rest_api.routers import upload_file_test


celery = create_celery()

class API:
    def __init__(self):
        self.__app: FastAPI = FastAPI(debug=True)


        @self.__app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response

        self.__init_routes()

        config: fastapi_gateway_auto_generate.Config = fastapi_gateway_auto_generate.Config(
            fast_api_app=self.__app,
            db_path="./database/database.db"
        )

        fastapi_gateway_auto_generate.Generator(config=config)




    def __init_routes(self):
        self.__app.include_router(upload_file_test.router)
        logger.success("Routers initialized")


    def run_uvicorn_server(self):
        run_uvicorn_loguru(
            uvicorn.Config(
                app=self.__app,
                host=DICT_ENVS["FASTAPI_IP"],
                port=DICT_ENVS["FASTAPI_PORT"],
                log_level="info",
                reload=True,
            )
        )
