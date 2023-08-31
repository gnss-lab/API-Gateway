from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from core.database.db import get_db
from core.database.models import TokenModel, UserModel

def delete_token_db(db: Session, user_id: int):
    """
    Delete user tokens from the database for a given user ID.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user for whom to delete tokens.
    :type user_id: int
    """
    db.query(TokenModel).filter(TokenModel.user_id == user_id).delete()
    db.commit()

def create_token_db(db: Session, user_id: int, token: str):
    """
    Create a new user token in the database.

    :param db: The database session.
    :type db: Session
    :param user_id: The ID of the user for whom to create a token.
    :type user_id: int
    :param token: The token to be created.
    :type token: str
    """
    db_token = TokenModel(user_id=user_id, token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

def verify_token(token: str, db: Session = Depends(get_db)):
    """
    Verify the validity of a user token.

    :param token: The token to be verified.
    :type token: str
    :param db: The database session.
    :type db: Session
    :return: The user associated with the token.
    :rtype: UserModel
    :raises HTTPException: If the token is invalid or not associated with any user.
    """
    user = db.query(UserModel).join(TokenModel).filter(TokenModel.token == token).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token",
        )
    return user
