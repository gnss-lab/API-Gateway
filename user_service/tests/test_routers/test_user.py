import bcrypt
from sqlalchemy.orm import Session
from src.core.database.models import UserModel


# Это функция для создания пользователя для использования в тестах
def create_test_user(db: Session):
    hashed_password = bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt())
    hashed_password_str = hashed_password.decode('utf-8')
    db_user = UserModel(username="testuser", password=hashed_password_str, email="test@example.com")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def test_register_user(test_client, db_session):
    with test_client as client:
        response = client.post("/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered"


def test_login_user(test_client, db_session):
    with test_client as client:
        create_test_user(db_session)
        response = client.post("/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data


def test_refresh_token(test_client, db_session):
    with test_client as client:
        create_test_user(db_session)
        response = client.post("/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        response = client.post("/refresh-token", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["token"] != token


def test_verify_user(test_client, db_session):
    with test_client as client:
        create_test_user(db_session)
        response = client.post("/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/verify", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] == True
