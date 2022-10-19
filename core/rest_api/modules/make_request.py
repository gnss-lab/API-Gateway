import aiohttp
import async_timeout
from typing import Union
from core.config.envs import DICT_ENVS


async def make_request(
    url: str,
    method: str,
    data: Union[dict, None] = None,
    headers: Union[dict, None] = None,
    params: Union[dict, None] = None
):
    """
    Args:
    ----------
    url : str
        is the url for one of the in-network services
    method : str
        is the lower version of one of the HTTP methods: GET, POST, PUT, DELETE # noqa
    data : Union[dict, None]
        is the payload
    headers : Union[dict, None]
        is the header to put additional headers into request
    Returns:
        service result coming / non-blocking http request (coroutine)
        e.g:   {
                    "id": 1,
                    "username": "xitowzys",
                    "email": "xitowzys@xitowzys.com",
                    "hashed_password": "***",
                    "created_by": 1
                }
    """
    if not data:
        data = {}

    with async_timeout.timeout(DICT_ENVS["GATEWAY_TIMEOUT"]):
        async with aiohttp.ClientSession() as session:
            request = getattr(session, method)
            async with request(url, data=data, headers=headers, params=params) as response:
                data = await response.json()
                return data, response.status
