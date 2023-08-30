import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database.db import get_db
from core.database.models import UserModel
from core.database.token_table import create_token_db, verify_token
from core.utils import create_jwt_token
from dtos.user import UserCreateResponse, UserCreateRequest, UserLoginRequest, UserLoginResponse, \
    UserVerifyTokenResponse, UserVerifyTokenRequest

router = APIRouter()


@router.post("/register", response_model=UserCreateResponse)
async def register_user(user: UserCreateRequest, db: Session = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_str = hashed_password.decode('utf-8')
    db_user = UserModel(username=user.username, password=hashed_password_str, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserCreateResponse(message="User registered")


@router.post("/login", response_model=UserLoginResponse)
async def login_user(login_request: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == login_request.username).first()

    if not user or not bcrypt.checkpw(login_request.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt_token(user.id)
    create_token_db(db, user.id, token)

    return UserLoginResponse(message="User logged in", token=token)


@router.get("/verify", response_model=UserVerifyTokenResponse)
async def verify_user(user: UserVerifyTokenRequest = Depends(verify_token)):
    return UserVerifyTokenResponse(message = "User token verified!", is_valid = True)
