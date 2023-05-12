from fastapi import FastAPI, Request
from loguru import logger
from starlette.responses import JSONResponse
from uvicorn_loguru_integration import run_uvicorn_loguru
import uvicorn

import fastapi_gateway_auto_generate
from core.config.envs import DICT_ENVS
from fastapi.middleware.cors import CORSMiddleware


async def custom_cors_middleware(request: Request, call_next):
    response = None
    allowed_port = 9000
    origin = request.headers.get("origin")

    if origin and origin.endswith(f":{allowed_port}"):
        response = await call_next(request)

        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Set-Cookie"

    if request.method == "OPTIONS" and response:
        response = JSONResponse(content={})
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Set-Cookie"

    if not response:
        response = await call_next(request)

    return response


class API:
    def __init__(self):
        self.__app: FastAPI = FastAPI(debug=True)
        self.__init_routes()
        self.__cors_settings()

        config: fastapi_gateway_auto_generate.Config = fastapi_gateway_auto_generate.Config(
            fast_api_app=self.__app,
            db_path=DICT_ENVS["DATABASE_PATH"]  # "./database/database.db"
        )

        fastapi_gateway_auto_generate.Generator(config=config)

    def __init_routes(self):
        logger.success("Routers initialized")

    def __cors_settings(self):
        # def custom_origin_check(origin: str) -> bool:
        #     # Check if the request comes from port 9000
        #     return origin.endswith(':9000')

        # origins = ["*"]
        #
        # self.__app.add_middleware(
        #     CORSMiddleware,
        #     allow_origin_callback=origins,
        #     allow_credentials=True,
        #     allow_methods=["*"],
        #     allow_headers=["*"],
        #     expose_headers=["*"],
        #
        # )

        self.__app.middleware("http")(custom_cors_middleware)

        logger.success("Cors settings are installed")

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
