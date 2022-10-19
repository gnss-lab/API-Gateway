from fastapi import APIRouter, status, Request, File, HTTPException, Response
from loguru import logger
from core.rest_api.modules.route_service import route_service
from pprint import pformat
from core.config.envs import DICT_ENVS

router = APIRouter()


@route_service(
    request_method=router.post,
    path="/mosgim/generate-map",
    status_code=status.HTTP_200_OK,
    service_url=DICT_ENVS["MOSGIM_SERVICE_URL"]
)
async def generate_map(request: Request, mag_type: str, const: str, file: bytes = File()):

    if not "X-Context-Type" in request.headers:
        raise HTTPException(
            status_code=409, detail="Header X-Context-Type not found")

    ret = {
        "data": {
            "file": file
        },
        "params": {
            "mag_type": mag_type,
            "const": const
        },
        "headers": {
            "X-Context-Type": request.headers.get("X-Context-Type")
        }
    }

    return ret
