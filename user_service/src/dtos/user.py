from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    """
    Represents the request model for creating a user.

    :param username: The username of the user.
    :type username: str
    :param password: The password of the user.
    :type password: str
    :param email: The email of the user.
    :type email: str
    """
    username: str
    password: str
    email: str


class UserCreateResponse(BaseModel):
    """
    Represents the response model for user creation.

    :param message: A message indicating the status of the user creation.
    :type message: str
    """
    message: str


class UserLoginRequest(BaseModel):
    """
    Represents the request model for user login.

    :param username: The username of the user.
    :type username: str
    :param password: The password of the user.
    :type password: str
    """
    username: str
    password: str


class UserLoginResponse(BaseModel):
    """
    Represents the response model for user login.

    :param message: A message indicating the status of the user login.
    :type message: str
    :param token: The authentication token for the logged-in user.
    :type token: str
    """
    message: str
    token: str


class UserVerifyTokenRequest(BaseModel):
    """
    Represents the request model for verifying a user token.

    :param token: The authentication token of the user to be verified.
    :type token: str
    """
    token: str


class UserVerifyTokenResponse(BaseModel):
    """
    Represents the response model for verifying a user token.

    :param message: A message indicating the status of the token verification.
    :type message: str
    :param is_valid: Indicates whether the provided token is valid or not.
    :type is_valid: bool
    """
    message: str
    is_valid: bool


class UserAccessResponse(BaseModel):
    """
    Represents the response for user access to a service.

    Attributes:
        message (str): A message describing the access status.
        has_access (bool): Indicates whether the user has access to the service.
    """
    message: str
    has_access: bool
