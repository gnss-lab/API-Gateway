from fastapi import FastAPI
from .routers import FileUpload
from .routers.mosgim_service import generate_map as mosgim_service__generate_map
from .routers.mosgim_service import ping_pong as mosgim_service__ping_pong
from loguru import logger
from uvicorn_loguru_integration import run_uvicorn_loguru
import uvicorn


class API:
    def __init__(self):
        self.__app = FastAPI(debug=True)
        self.__init_routes()

    def __init_routes(self):
        self.__app.include_router(FileUpload.router)
        self.__app.include_router(mosgim_service__ping_pong.router)
        self.__app.include_router(mosgim_service__generate_map.router)
        logger.success("Routers initialized")

    def run_uvicorn_server(self):
        run_uvicorn_loguru(
            uvicorn.Config(
                app=self.__app,
                host="127.0.0.1",
                port=8000,
                log_level="info",
                reload=True,
            )
        )
