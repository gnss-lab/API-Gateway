from typing import NoReturn
import aiohttp
from functools import wraps
from fastapi import HTTPException, status, APIRouter
from core.rest_api.modules.make_request import make_request
from loguru import logger


def route_service(
    request_method: APIRouter,
    path: str,
    status_code: int,
    service_url: str
) -> NoReturn:
    router_any = request_method(
        path=path,
        status_code=status_code
    )

    def decorator(f):
        @router_any
        @wraps(f)
        async def wrapper(**kwargs):
            build_request: dict = await f(**kwargs) or {}

            request = kwargs.get("request")

            try:
                resp_data, status_code_from_service = await make_request(
                    url=f'{service_url}{path}',
                    method=request.scope['method'].lower(),
                    params=build_request.get("params"),
                    data=build_request.get("data"),
                    headers=build_request.get("headers")
                )

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

            if not status_code_from_service == status_code:
                raise HTTPException(
                    status_code=status_code_from_service, detail=resp_data)

            return resp_data
    return decorator
