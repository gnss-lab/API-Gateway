import re
from fastapi import APIRouter, status, Request, Response
from core.rest_api.modules.route_service import route_service
from core.config.envs import DICT_ENVS
from fastapi_gateway import route

router = APIRouter()


# @route_service(
#     request_method=router.post,
#     path="/mosgim/ping",
#     status_code=status.HTTP_200_OK,
#     service_url=DICT_ENVS["MOSGIM_SERVICE_URL"]
# )
@route(
    request_method=router.post,
    service_url=DICT_ENVS["MOSGIM_SERVICE_URL"],
    gateway_path="/mosgim/ping",
    service_path="/mosgim/ping",
    status_code=status.HTTP_200_OK
)
async def ping_pong_mosgim(request: Request, response: Response):
    pass
