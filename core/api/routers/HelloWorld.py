from fastapi import APIRouter, HTTPException, status, Request
import aiohttp
from core.api.modules.make_request import make_request
from core.config.envs import DICT_ENVS
from loguru import logger

router = APIRouter()


@router.post("/test")
async def ping_pong_mosgim(request: Request):

    try:
        resp_data, status_code_from_service = await make_request(
            url=f'{DICT_ENVS["MOSGIM_SERVICE_URL"]}/test',
            method=request.scope['method'].lower(),
            data={"ping_pong_api_gateway": "ping"}
        )

        logger.debug(f"{resp_data}")
    except aiohttp.client_exceptions.ClientConnectorError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Service is unavailable.',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except aiohttp.client_exceptions.ContentTypeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Service error.',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except Exception as e:
        print(e)

    # logger.debug(f"({status_code_from_service}) -> {resp_data}")

    return "ok"
