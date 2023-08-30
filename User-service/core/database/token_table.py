from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.database.db import get_db
from core.database.models import TokenModel, UserModel


def create_token_db(db: Session, user_id: int, token: str):
    db_token = TokenModel(user_id=user_id, token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)


def verify_token(token: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).join(TokenModel).filter(TokenModel.token == token).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token",
        )
    return user
