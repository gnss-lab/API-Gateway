from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from src.core.database.db import Base, engine
class UserModel(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        password (str): The hashed password of the user.
        email (str): The email of the user.
        tokens (relationship): The relationship to the tokens associated with the user.
        role_id (int): The ID of the associated role.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    tokens = relationship("TokenModel", back_populates="user")
