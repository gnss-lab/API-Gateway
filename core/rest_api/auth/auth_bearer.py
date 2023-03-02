import json
from typing import Optional

import aiohttp
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPBasicCredentials, HTTPAuthorizationCredentials


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not await self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    async def verify_jwt(self, jwt_token: str) -> bool:
        async with aiohttp.ClientSession() as session:
            pokemon_url = 'http://127.0.0.1:8000/api/v1/verify-jwt'
            async with session.post(pokemon_url, json={"jwt": jwt_token}) as resp:
                pokemon = await resp.json()
                print(pokemon)

                if isinstance(pokemon, bool):
                    return pokemon
