import re
from fastapi import APIRouter, status, Request
from core.rest_api.modules.route_service import route_service

router = APIRouter()


@route_service(
    request_method=router.post,
    path="/ping",
    status_code=status.HTTP_200_OK,
)
async def ping_pong_mosgim(request: Request, text: str):

    params = {"text": text}

    return {"params": params}
