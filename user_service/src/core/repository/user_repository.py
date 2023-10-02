from sqlalchemy.orm import Session
from src.core.database.models import UserModel, TokenModel, RoleModel
from src.core.database.db import get_db
from fastapi import HTTPException
from starlette import status


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    async def is_user_exist(self, user: UserModel):
        """
        Check if a user with the same username or email already exists.

        :param user: User model instance to check.
        :type user: UserModel
        :return: True if a user with the same username or email exists, False otherwise.
        :rtype: bool
        """
        return self.db.query(UserModel).filter(
            (UserModel.username == user.username) | (UserModel.email == user.email)
        ).first() is not None

    async def get_user_by_username(self, username: str):
        """
        Get a user by username.

        :param username: Username of the user to retrieve.
        :type username: str
        :return: The user model if found, None otherwise.
        :rtype: UserModel
        """
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    async def get_user_by_id(self, id: int):
        """
        Get a user by username.

        :param username: Id of the user to retrieve.
        :type id: int
        :return: The user model if found, None otherwise.
        :rtype: UserModel
        """
        return self.db.query(UserModel).filter(UserModel.id == id).first()

    async def is_admin_token(self, token: str):
        """
        Check if the token corresponds to an admin user.

        :param token: Token to check.
        :type token: str
        :return: True if the token corresponds to an admin user, False otherwise.
        :rtype: bool
        """
        admin_user = self.db.query(UserModel).join(TokenModel).filter(
            TokenModel.token == token,
            UserModel.role_id == (self.db.query(RoleModel).filter(RoleModel.name == 'admin').first()).id
        ).first()

        return admin_user is not None

    async def create_user(self, user: UserModel):
        """
        Create a new user.

        :param user: User model instance to create.
        :type user: UserModel
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

    async def get_user_token(self, user_id: int):
        """
        Get the user's token by user ID.

        :param user_id: The ID of the user.
        :type user_id: int
        :return: The user's token if found, None otherwise.
        :rtype: TokenModel
        """
        return self.db.query(TokenModel).filter(TokenModel.user_id == user_id).first()

    async def delete_tokens_by_user_id(self, user_id: int):
        """
        Delete user tokens from the database for a given user ID.

        :param user_id: The ID of the user for whom to delete tokens.
        :type user_id: int
        """
        self.db.query(TokenModel).filter(TokenModel.user_id == user_id).delete()
        self.db.commit()

    async def create_user_token(self, user_id: int, token: str):
        """
        Create a new user token in the database.

        :param user_id: The ID of the user for whom to create a token.
        :type user_id: int
        :param token: The token to be created.
        :type token: str
        """
        db_token = TokenModel(user_id=user_id, token=token)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)

    async def verify_user_token(self, token: str):
        """
        Verify the validity of a user token.

        :param token: The token to be verified.
        :type token: str
        :return: The user associated with the token.
        :rtype: UserModel
        :raises HTTPException: If the token is invalid or not associated with any user.
        """
        user = self.db.query(UserModel).join(TokenModel).filter(TokenModel.token == token).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user token",
            )
        return user

    async def is_any_admin_exists(self):
        return self.db.query(UserModel).filter(UserModel.role_id == 1).first() is not None