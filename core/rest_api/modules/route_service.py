import aiohttp
from core.config.envs import DICT_ENVS
from functools import wraps
from fastapi import HTTPException, status
from core.rest_api.modules.make_request import make_request
from loguru import logger


def route_service(
    request_method,
    path: str,
    status_code: int,
):
    router_any = request_method(
        path=path,
        status_code=status_code
    )

    def decorator(f):
        @router_any
        @wraps(f)
        async def wrapper(**kwargs):
            build_request: dict = await f(**kwargs)

            request = kwargs.get("request")

            try:
                resp_data, status_code_from_service = await make_request(
                    url=f'{DICT_ENVS["MOSGIM_SERVICE_URL"]}{path}',
                    method=request.scope['method'].lower(),
                    params=build_request["params"] if "params" in build_request else None,
                    data=build_request["data"] if "data" in build_request else None
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

            return resp_data

    return decorator
