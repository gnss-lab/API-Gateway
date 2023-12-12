from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean, func
from sqlalchemy.orm import relationship
from src.core.database.db import Base, engine, get_db
from src.core.database.models import UserModel


class TokenModel(Base):
    """
    Represents an authentication token in the database.

    Attributes:
        id (int): The unique identifier of the token.
        user_id (int): The ID of the associated user.
        token (str): The authentication token.
        created_at (timestamp): The timestamp of token creation.
        user (relationship): The relationship to the user associated with the token.
    """
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    user = relationship("UserModel", back_populates="tokens", cascade="all, delete-orphan", single_parent=True)

    @property
    def user_name(self) -> str:
        with next(get_db()) as db:
            user = db.query(UserModel).filter(UserModel.id == self.user_id).first()
        return user.username if user else None
