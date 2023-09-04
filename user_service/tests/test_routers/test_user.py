import pytest
from fastapi.testclient import TestClient
from src.config.config import create_app
from src.core.database.models import UserModel, TokenModel
from src.core.database.db import SessionLocal, engine

app, _, _ = create_app()
client = TestClient(app)

# Фикстура для создания и удаления таблиц в базе данных
@pytest.fixture(scope="function", autouse=True)
def create_and_delete_tables():
    UserModel.metadata.create_all(bind=engine)
    yield
    UserModel.metadata.drop_all(bind=engine)

# Фикстура для сессии базы данных
@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()

def test_register_user(db_session):
    with client:
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered"

def test_login_user(db_session):
    with client:
        # Создаем тестового пользователя
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        assert response.status_code == 200

        # Пытаемся войти с созданным пользователем для получения токена
        response = client.post("/user/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data

def test_refresh_token(db_session):
    with client:
        # Создаем тестового пользователя
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        assert response.status_code == 200

        # Входим с созданным пользователем, чтобы получить токен
        response = client.post("/user/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        # Обновляем токен
        response = client.post("/user/refresh-token", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data


def test_verify_user(db_session):
    with client:
        # Создаем тестового пользователя
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        assert response.status_code == 200

        # Входим с созданным пользователем, чтобы получить токен
        response = client.post("/user/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        # Проверяем токен
        response = client.get(f"/user/verify?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
