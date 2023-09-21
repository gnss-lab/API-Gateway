from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

from src.core.database.db import Base, engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserModel(Base):
    """
    Represents a user in the database.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        password (str): The hashed password of the user.
        email (str): The email of the user.
        tokens (relationship): The relationship to the tokens associated with the user.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    tokens = relationship("TokenModel", back_populates="user")


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
    user = relationship("UserModel", back_populates="tokens")


class ServiceModel(Base):
    """
    Represents a service in the database.

    Attributes:
        id (int): The unique identifier of the service.
        name (str): The name of the service.
        user_services (relationship): The relationship to the users associated with the service.
    """
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    user_services = relationship("UserServiceModel", back_populates="service")


class UserServiceModel(Base):
    """
    Represents the relationship between users and services in the database.

    Attributes:
        id (int): The unique identifier of the relationship.
        user_id (int): The ID of the associated user.
        service_id (int): The ID of the associated service.
        user (relationship): The relationship to the user associated with the relationship.
        service (relationship): The relationship to the service associated with the relationship.
    """
    __tablename__ = 'user_services'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id', ondelete='CASCADE'), nullable=False)
    user = relationship("UserModel", back_populates="user_services")
    service = relationship("ServiceModel", back_populates="user_services")
