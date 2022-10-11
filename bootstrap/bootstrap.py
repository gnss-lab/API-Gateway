from typing import NoReturn
import uvicorn
from uvicorn_loguru_integration import run_uvicorn_loguru
from core.logging.loguru_init import logger_configuration
from core.api.api import app

# @app.post("/files/")
# async def create_file(mag_type: str, const: str, file: bytes = File()):

#     return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     return {"filename": file.filename}


def start_server() -> NoReturn:
    run_uvicorn_loguru(
        uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level="trace",
            reload=True,
        )
    )


def bootstrap() -> NoReturn:
    logger_configuration()
    start_server()
