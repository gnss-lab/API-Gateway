from datetime import datetime, timedelta

import jwt
from sqlalchemy.orm import Session

from config.envs import DICT_ENVS


def create_jwt_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, DICT_ENVS["SECRET_KEY"], algorithm="HS256")

