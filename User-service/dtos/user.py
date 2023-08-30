from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    username: str
    password: str
    email: str


class UserCreateResponse(BaseModel):
    message: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    message: str
    token: str


class UserVerifyTokenRequest(BaseModel):
    token: str


class UserVerifyTokenResponse(BaseModel):
    message: str
    is_valid: bool
