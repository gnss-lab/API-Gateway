import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from src.config.envs import DICT_ENVS
from src.core.database.db import get_db
from src.core.database.models import UserModel, TokenModel, ServiceModel, UserServiceModel
from src.core.repository.role_repository import RoleRepository
from src.core.repository.user_repository import UserRepository
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

    This endpoint allows you to register a new user in the system.

    :param UserCreateRequest user: Data for user registration.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Successful registration.
    :statuscode 400: User with the same username or email already exists.
    :statuscode 500: Internal server error.
    """
    try:
        user_repository = UserRepository(db)

        if await user_repository.is_user_exist(user):
            raise HTTPException(status_code=400, detail="User with the same username or email already exists")

        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')

        db_user = UserModel(username=user.username, password=hashed_password_str, email=user.email)
        await user_repository.create_user(db_user)

        if not DICT_ENVS["ADMIN_CONFIGURED"]:
            role_repository = RoleRepository(db)
            await role_repository.assign_role_to_user(1, 1)
            DICT_ENVS["ADMIN_CONFIGURED"] = True

        return UserCreateResponse(message="User registered")
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login", response_model=UserLoginResponse)
async def login_user(login_request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Log in a user.

    This endpoint allows you to log in an existing user.

    :param UserLoginRequest login_request: Data for user login.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Successful login.
    :statuscode 401: Invalid credentials.
    """
    try:
        user_repository = UserRepository(db)

        user = await user_repository.get_user_by_username(login_request.username)

        if not user or not bcrypt.checkpw(login_request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        existing_token = await user_repository.get_user_token(user.id)

        if existing_token:
            return UserLoginResponse(message="User logged in", token=existing_token.token)

        token = create_jwt_token(user.id)
        await user_repository.create_user_token(user.id, token)

        return UserLoginResponse(message="User logged in", token=token)
    except Exception as e:
        logger.error(f"Error during user login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh-token", response_model=UserLoginResponse)
async def refresh_token(login_request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Refresh a user's authentication token.

    This endpoint allows you to refresh a user's authentication token.

    :param UserLoginRequest login_request: Data for token refresh.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Token refreshed successfully.
    :statuscode 401: Invalid credentials.
    :statuscode 500: Internal server error.
    """
    try:
        user_repository = UserRepository(db)

        user = await user_repository.get_user_by_username(login_request.username)

        if not user or not bcrypt.checkpw(login_request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        new_token = create_jwt_token(user.id)
        await user_repository.delete_tokens_by_user_id(user.id)
        await user_repository.create_user_token(user.id, new_token)

        return UserLoginResponse(message="Token refreshed", token=new_token)
    except Exception as e:
        logger.error(f"Error during token refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/verify", response_model=UserVerifyTokenResponse)
async def verify_user(user: UserVerifyTokenRequest, db: Session = Depends(get_db)):
    """
    Verify a user's authentication token.

    :param UserVerifyTokenRequest user: User token verification request data.
    :return: User token verification response.
    :rtype: UserVerifyTokenResponse

    :statuscode 200: Token verified successfully.
    :statuscode 401: Token is invalid.
    """
    user_repository = UserRepository(db)
    is_valid_token = await user_repository.verify_user_token(user.token)

    if is_valid_token:
        return UserVerifyTokenResponse(message="User token verified", is_valid=True)
    else:
        raise HTTPException(status_code=401, detail="Token is invalid")


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
