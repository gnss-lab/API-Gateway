from fastapi import APIRouter, HTTPException, status, Request, UploadFile, File
import aiohttp
from core.rest_api.modules.make_request import make_request
from core.config.envs import DICT_ENVS
from loguru import logger
import io
import os
import zipfile
from pathlib import Path


router = APIRouter()


@router.post("/file")
async def file_upload(request: Request, file: UploadFile = File(...)):

    if (file.content_type == "application/zip"):

        zipfile_ob = zipfile.ZipFile(io.BytesIO(file.file.read()))

        logger.debug(file.content_type)
        # logger.debug(zipfile_ob.getinfo())

        logger.debug(zipfile_ob.namelist())

        # for f in zipfile_ob.infolist():
        #     logger.debug(f)

        # for f in zipfile_ob.namelist():
        #     path = Path(f)

        #     if f.endswith("/") or f.endswith(".DS_Store"):
        #         continue

        #     logger.debug(path)

        #     with zipfile_ob.open(f, mode='r') as thefile:
        #         print(thefile.read().decode("utf-8"))
    else:
        raise HTTPException(status_code=409, detail="Incorrect file extension")
