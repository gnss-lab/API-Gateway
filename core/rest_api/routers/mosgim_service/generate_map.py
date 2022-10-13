from fastapi import APIRouter, HTTPException, status, Request, UploadFile, File
import aiohttp
from core.rest_api.modules.make_request import make_request
from core.config.envs import DICT_ENVS
from loguru import logger
import io
from core.rest_api.modules.route_service import route_service

router = APIRouter()


@route_service(
    request_method=router.post,
    path="/mosgim/generate-map",
    status_code=status.HTTP_200_OK,
)
async def generate_map(request: Request, mag_type: str, const: str, file: bytes = File()):
    data = {"file": file}
    params = {"mag_type": mag_type, "const": const}

    return {"data": data, "params": params}
