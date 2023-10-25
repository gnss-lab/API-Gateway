import asyncio
import contextlib
import os
import time

import pytest
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from starlette.testclient import TestClient

from src.config.envs import DICT_ENVS
from src.core.database.db import Base
from src.core.database.models import RoleModel, UserModel
from src.core.repository.role_repository import RoleRepository
from src.config.config import create_app, get_db
from src.core.repository.user_repository import UserRepository

app, _, _ = create_app()
client = TestClient(app)


@pytest.fixture
def override_get_db():
    db_path = 'test_db.sqlite'
    engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    connection = db.connection()

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    print("Tables in the database:", inspector.get_table_names())

    role_repository = RoleRepository(db)
    if not role_repository.is_default_roles_exists():
        asyncio.run(role_repository.create_default_roles())
    print("is_default_roles_exists", role_repository.is_default_roles_exists())

    def override():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override

    yield db

    app.dependency_overrides.pop(get_db)

    engine.dispose()
    db.close()

    with contextlib.suppress(PermissionError):
        os.remove(db_path)


def test_register_user(override_get_db):
    with client:
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        print(response.json())
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered"


def test_register_existing_user(override_get_db):
    # Регистрация существующего пользователя должна вызвать ошибку 400
    with client:
        # Регистрация первого пользователя
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        assert response.status_code == 200

        # Попытка зарегистрировать того же пользователя еще раз
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "User with the same username or email already exists"


def test_register_user_admin_role(override_get_db):
    # Проверка, что пользователь с ролью "admin" создается, если роли настроены
    with client:
        response = client.post("/user/register", json={
            "username": "testadmin",
            "password": "testpassword",
            "email": "admin@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered"

        # Проверка, что пользователь с ролью "admin" создан
        user_repository = UserRepository(override_get_db)
        admin_user = asyncio.run(user_repository.get_user_by_username("testadmin"))
        assert admin_user.role_id == 1


def test_login_user(override_get_db):
    # Создаем пользователя
    DICT_ENVS["ADMIN_CONFIGURED"] = True
    with client:
        register_response = client.post("/user/register", json={
            "username": "testloginuser",
            "password": "testloginpassword",
            "email": "testlogin@example.com"
        })
        assert register_response.status_code == 200

    # Пытаемся войти с правильными учетными данными
    with client:
        login_response = client.post("/user/login", json={
            "username": "testloginuser",
            "password": "testloginpassword"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        assert data["message"] == "User logged in"
        assert "token" in data


def test_login_user_invalid_credentials(override_get_db):
    # Создаем пользователя
    DICT_ENVS["ADMIN_CONFIGURED"] = True
    with client:
        register_response = client.post("/user/register", json={
            "username": "testloginuser1",
            "password": "testloginpassword1",
            "email": "testlogin1@example.com"
        })
        assert register_response.status_code == 200

    # Пытаемся войти с неверными учетными данными
    with client:
        login_response = client.post("/user/login", json={
            "username": "testloginuser",
            "password": "incorrectpassword"
        })
        assert login_response.status_code == 401
        data = login_response.json()
        assert data["detail"] == "Invalid credentials"


def test_login_user_nonexistent_user(override_get_db):
    # Пытаемся войти с учетными данными несуществующего пользователя
    DICT_ENVS["ADMIN_CONFIGURED"] = True

    with client:
        login_response = client.post("/user/login", json={
            "username": "nonexistentuser",
            "password": "somepassword"
        })
        assert login_response.status_code == 401
        data = login_response.json()
        assert data["detail"] == "Invalid credentials"


def test_refresh_token_success(override_get_db):
    # Создаем пользователя
    DICT_ENVS["ADMIN_CONFIGURED"] = True

    with client:
        register_response = client.post("/user/register", json={
            "username": "testrefreshuser",
            "password": "testrefreshpassword",
            "email": "testrefresh@example.com"
        })
        assert register_response.status_code == 200

    # Входим и получаем токен
    with client:
        login_response = client.post("/user/login", json={
            "username": "testrefreshuser",
            "password": "testrefreshpassword"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        assert data["message"] == "User logged in"
        assert "token" in data
        original_token = data["token"]

    # Обновляем токен
    with client:
        refresh_response = client.post("/user/refresh-token", json={
            "username": "testrefreshuser",
            "password": "testrefreshpassword"
        })
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert data["message"] == "Token refreshed"
        assert "token" in data
        new_token = data["token"]

        # Убеждаемся, что новый токен отличается от оригинального
        assert new_token != original_token


def test_refresh_token_invalid_credentials(override_get_db):
    # Создаем пользователя
    DICT_ENVS["ADMIN_CONFIGURED"] = True

    with client:
        register_response = client.post("/user/register", json={
            "username": "testrefreshuser",
            "password": "testrefreshpassword",
            "email": "testrefresh@example.com"
        })
        assert register_response.status_code == 200

    # Пытаемся обновить токен с неверными учетными данными
    with client:
        refresh_response = client.post("/user/refresh-token", json={
            "username": "testrefreshuser",
            "password": "incorrectpassword"
        })
        assert refresh_response.status_code == 401
        data = refresh_response.json()
        assert data["detail"] == "Invalid credentials"


def test_refresh_token_nonexistent_user(override_get_db):
    # Пытаемся обновить токен несуществующего пользователя
    DICT_ENVS["ADMIN_CONFIGURED"] = True

    with client:
        refresh_response = client.post("/user/refresh-token", json={
            "username": "nonexistentuser",
            "password": "somepassword"
        })
        assert refresh_response.status_code == 401
        data = refresh_response.json()
        assert data["detail"] == "Invalid credentials"


def test_verify_user_valid_token(override_get_db):
    # Создаем пользователя и получаем токен

    DICT_ENVS["ADMIN_CONFIGURED"] = True
    with client:
        register_response = client.post("/user/register", json={
            "username": "testverifyuser",
            "password": "testverifypassword",
            "email": "testverify@example.com"
        })
        assert register_response.status_code == 200

        login_response = client.post("/user/login", json={
            "username": "testverifyuser",
            "password": "testverifypassword"
        })
        assert login_response.status_code == 200
        data = login_response.json()
        assert data["message"] == "User logged in"
        assert "token" in data
        token = data["token"]

    # Проверяем токен
    with client:
        verify_response = client.get("/user/verify", params={"token": token})
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["message"] == "User token verified"
        assert data["is_valid"] is True


def test_verify_user_invalid_token(override_get_db):
    DICT_ENVS["ADMIN_CONFIGURED"] = True

    # Подменяем токен (например, добавляем символ в середину)
    modified_token = "invalidtoken"

    # Проверяем модифицированный токен
    with client:
        verify_response = client.get("/user/verify", params={"token": modified_token})
        assert verify_response.status_code == 401
        data = verify_response.json()
        assert data["detail"] == "Invalid user token"


def test_verify_user_missing_token(override_get_db):
    DICT_ENVS["ADMIN_CONFIGURED"] = True
    # Пытаемся проверить токен без передачи параметра
    with client:
        verify_response = client.get("/user/verify")
        assert verify_response.status_code == 422
        data = verify_response.json()
        assert data["detail"][0]["msg"] == "Field required"
