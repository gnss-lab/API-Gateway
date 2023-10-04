import asyncio

import pytest
from httpx import AsyncClient
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.db import Base
from src.core.database.models import UserModel, TokenModel, RoleModel
from src.core.repository.user_repository import UserRepository
from fastapi.testclient import TestClient

DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db():
    engine = create_engine(DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    return db


@pytest.fixture
def user_repository(db):
    return UserRepository(db)


def test_is_user_exist(user_repository, db):
    user = UserModel(username="test_user", password="test_password", email="test@example.com", role_id=1)
    db.add(user)
    db.commit()

    existing_user = UserModel(username="test_user", password="test_password", email="test@example.com", role_id=1)
    non_existing_user = UserModel(username="non_existing_user", password="test_password", email="test_non@example.com",
                                  role_id=1)

    assert asyncio.run(user_repository.is_user_exist(existing_user))
    assert not asyncio.run(user_repository.is_user_exist(non_existing_user))


def test_get_user_by_username(user_repository, db):
    user = UserModel(username="test_user", password="test_password", email="test@example.com", role_id=1)
    db.add(user)
    db.commit()

    retrieved_user = asyncio.run(user_repository.get_user_by_username("test_user"))

    assert retrieved_user is not None
    assert retrieved_user.username == "test_user"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.role_id == 1


def test_get_user_by_id(user_repository, db):
    user = UserModel(id=1000, username="test_user", password="test_password", email="test@example.com", role_id=1)
    db.add(user)
    db.commit()

    retrieved_user = asyncio.run(user_repository.get_user_by_id(1000))

    assert retrieved_user is not None
    assert retrieved_user.id == 1000
    assert retrieved_user.username == "test_user"
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.role_id == 1


def test_create_user(user_repository, db):
    user = UserModel(username="new_user", password="new_password", email="new@example.com", role_id=1)

    asyncio.run(user_repository.create_user(user))

    retrieved_user = db.query(UserModel).filter_by(username="new_user").first()

    assert retrieved_user is not None
    assert retrieved_user.username == "new_user"
    assert retrieved_user.email == "new@example.com"
    assert retrieved_user.role_id == 1


def test_get_user_token(user_repository, db):
    user = UserModel(id=10, username="token_user", password="token_password", email="token@example.com", role_id=1)
    token = TokenModel(user_id=user.id, token="user_token")

    db.add(user)
    db.add(token)
    db.commit()

    retrieved_token = asyncio.run(user_repository.get_user_token(user.id))

    assert retrieved_token is not None
    assert retrieved_token.token == "user_token"
    assert retrieved_token.user_id == user.id


def test_delete_tokens_by_user_id(user_repository, db):
    user = UserModel(id=15, username="delete_user", password="delete_password", email="delete@example.com", role_id=1)
    token1 = TokenModel(user_id=user.id, token="token1")
    token2 = TokenModel(user_id=user.id, token="token2")

    db.add(user)
    db.add(token1)
    db.add(token2)
    db.commit()

    asyncio.run(user_repository.delete_tokens_by_user_id(user.id))

    # Check that tokens were deleted
    remaining_tokens = db.query(TokenModel).filter_by(user_id=user.id).all()
    assert len(remaining_tokens) == 0


def test_create_user_token(user_repository, db):
    user = UserModel(id=10, username="create_token_user", password="create_token_password", email="create_token@example.com",
                     role_id=1)

    db.add(user)
    db.commit()

    token = "new_user_token"
    asyncio.run(user_repository.create_user_token(user.id, token))

    retrieved_token = db.query(TokenModel).filter_by(user_id=user.id).first()

    assert retrieved_token is not None
    assert retrieved_token.token == "new_user_token"
    assert retrieved_token.user_id == user.id


def test_verify_user_token(user_repository, db):
    user = UserModel(id=10, username="verify_user", password="verify_password", email="verify@example.com", role_id=1)
    token = TokenModel(user_id=user.id, token="verified_token")

    db.add(user)
    db.add(token)
    db.commit()

    verified_user = asyncio.run(user_repository.verify_user_token("verified_token"))

    assert verified_user is not None
    assert verified_user.id == user.id
    assert verified_user.username == "verify_user"
    assert verified_user.email == "verify@example.com"
    assert verified_user.role_id == 1


def test_is_any_admin_exists(user_repository, db):
    admin_user = UserModel(username="admin", password="admin_password", email="admin@example.com", role_id=1)

    db.add(admin_user)
    db.commit()

    assert asyncio.run(user_repository.is_any_admin_exists())
