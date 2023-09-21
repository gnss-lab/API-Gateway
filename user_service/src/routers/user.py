import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database.db import get_db
from src.core.database.models import UserModel, TokenModel, ServiceModel, UserServiceModel
from src.core.database.token_table import create_token_db, delete_token_db, verify_token
from src.core.utils.utils import create_jwt_token

from src.dtos.user import (
    UserCreateResponse, UserCreateRequest, UserLoginRequest, UserLoginResponse,
    UserVerifyTokenResponse, UserVerifyTokenRequest, UserAccessResponse
)

router = APIRouter()


@router.post("/register", response_model=UserCreateResponse)
async def register_user(user: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Register a new user.

    :param user: User registration request data.
    :type user: UserCreateRequest
    :param db: Database session.
    :type db: Session
    :return: User registration response.
    :rtype: UserCreateResponse
    """
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User with the same username or email already exists")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_str = hashed_password.decode('utf-8')
    db_user = UserModel(username=user.username, password=hashed_password_str, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserCreateResponse(message="User registered")


@router.post("/login", response_model=UserLoginResponse)
async def login_user(login_request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Log in a user.

    :param login_request: User login request data.
    :type login_request: UserLoginRequest
    :param db: Database session.
    :type db: Session
    :return: User login response.
    :rtype: UserLoginResponse
    """
    user = db.query(UserModel).filter(UserModel.username == login_request.username).first()

    if not user or not bcrypt.checkpw(login_request.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    existing_token = db.query(TokenModel).filter(TokenModel.user_id == user.id).first()

    if existing_token:
        return UserLoginResponse(message="User logged in", token=existing_token.token)

    token = create_jwt_token(user.id)
    create_token_db(db, user.id, token)

    return UserLoginResponse(message="User logged in", token=token)


@router.post("/refresh-token", response_model=UserLoginResponse)
async def refresh_token(login_request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Refresh a user's authentication token.

    :param login_request: User login request data.
    :type login_request: UserLoginRequest
    :param db: Database session.
    :type db: Session
    :return: User login response with refreshed token.
    :rtype: UserLoginResponse
    """
    user = db.query(UserModel).filter(UserModel.username == login_request.username).first()

    if not user or not bcrypt.checkpw(login_request.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    new_token = create_jwt_token(user.id)
    delete_token_db(db, user.id)
    create_token_db(db, user.id, new_token)
    return UserLoginResponse(message="Token refreshed", token=new_token)


@router.get("/verify", response_model=UserVerifyTokenResponse)
async def verify_user(user: UserVerifyTokenRequest = Depends(verify_token)):
    """
    Verify a user's authentication token.

    :param user: User token verification request data.
    :type user: UserVerifyTokenRequest
    :return: User token verification response.
    :rtype: UserVerifyTokenResponse
    """
    return UserVerifyTokenResponse(message="User token verified", is_valid=True)


@router.post("/check-access", response_model=UserAccessResponse)
async def check_access_to_service(service_name: str, token: str, db: Session = Depends(get_db)):
    """
    Check if the user with the given token has access to the specified service.

    :param service_name: The name of the service to check access for.
    :type service_name: str
    :param token: The user's authentication token.
    :type token: str
    :param db: Database session.
    :type db: Session
    :return: User access response.
    :rtype: UserAccessResponse
    """
    token_entry = db.query(TokenModel).filter(TokenModel.token == token).first()
    if not token_entry:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(UserModel).filter(UserModel.id == token_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if (
            service := db.query(ServiceModel)
                    .filter(ServiceModel.name == service_name)
                    .first()
    ):
        return (
            UserAccessResponse(message="Access granted", has_access=True)
            if (
                user_service_entry := db.query(UserServiceModel)
                .filter(
                    UserServiceModel.user_id == user.id,
                    UserServiceModel.service_id == service.id,
                )
                .first()
            )
            else UserAccessResponse(message="Access denied", has_access=False)
        )
    else:
        raise HTTPException(status_code=404, detail="Service not found")
