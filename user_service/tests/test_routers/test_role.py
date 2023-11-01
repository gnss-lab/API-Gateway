import asyncio
import contextlib
import os
import time
from unittest.mock import patch

from src.config.config import create_app
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from src.config.config import create_app, get_db
from src.core.database.models import UserModel, UserServiceModel
from src.core.repository.role_repository import RoleRepository
from src.core.database.db import Base
from src.core.repository.service_repository import ServiceRepository
from src.core.repository.user_repository import UserRepository

app, _, _ = create_app()
client = TestClient(app)
count = 0


@pytest.fixture
def override_get_db():
    global count
    count += 1
    db_path = f'test_db{count}.sqlite'
    if os.path.exists(db_path):
        os.remove(db_path)
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

    # Creating an admin user with token "123"
    user_repository = UserRepository(db)
    admin_user = asyncio.run(user_repository.create_user(
        UserModel(username="admin", password="admin_password", email="admin@example.com", role_id=1)))
    admin_token = "123"
    asyncio.run(user_repository.create_user_token(admin_user.id, admin_token))

    # Creating an admin user with token "123" in psql
    user_repository = UserRepository(next(get_db()))
    admin_user = asyncio.run(user_repository.create_user(
        UserModel(username="admin", password="admin_password", email="admin@example.com", role_id=1)))
    admin_id = admin_user.id
    admin_token = "123"
    asyncio.run(user_repository.create_user_token(admin_id, admin_token))

    def override():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override

    yield db

    app.dependency_overrides.pop(get_db)

    asyncio.run(user_repository.delete_user_by_id(admin_id))

    engine.dispose()
    db.close()

    with contextlib.suppress(PermissionError):
        os.remove(db_path)


def test_get_all_roles(override_get_db):
    response = client.get("/role/roles")

    assert response.status_code == 200

    assert response.json() == [{'id': 1, 'name': 'admin'}, {'id': 2, 'name': 'user'}]


def test_delete_role(override_get_db):
    response = client.delete("/role/roles/1", params={"token": "123"})
    assert response.status_code == 200
    assert response.json() == {"deleted": True}

    response = client.get("/role/roles")
    assert response.json() == [{'id': 2, 'name': 'user'}]


def test_create_role(override_get_db):
    response = client.post("/role/roles", json={"name": "test_role"}, params={"token": "123"})

    assert response.status_code == 200

    role_repository = RoleRepository(override_get_db)
    created_role = asyncio.run(role_repository.get_role_by_name("test_role"))
    assert created_role is not None
    assert created_role.name == "test_role"


def test_get_user_role_success(override_get_db):
    user_repository = UserRepository(override_get_db)
    role_repository = RoleRepository(override_get_db)

    user = UserModel(username="test_user", password="test_password", email="test@example.com", role_id=1)

    override_get_db.add(user)
    override_get_db.commit()

    user = asyncio.run(user_repository.get_user_by_username("test_user"))

    role_id = asyncio.run(role_repository.get_user_role_by_id(user.id))

    response = client.get("/role/user/2/role/")
    assert response.status_code == 200
    assert response.json()["id"] == role_id


def test_get_user_roles_user_not_found(override_get_db):
    response = client.get("role/user/999/role")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_assign_role_to_user_success(override_get_db):
    with client:
        user_repository = UserRepository(override_get_db)
        user = asyncio.run(user_repository.create_user(
            UserModel(username="test_user", password="test_password", email="test@example.com", role_id=2)))

        role_repository = RoleRepository(override_get_db)
        role = asyncio.run(role_repository.create_role("test_role"))

        response = client.post(f"/role/user/{user.id}/role", json={"role_id": role.id}, params={"token": "123"})

        assert response.status_code == 200
        assert response.json() is True


def test_assign_role_to_user_user_not_found(override_get_db):
    with client:
        response = client.post("/role/user/999/role", json={"role_id": 1}, params={"token": "123"})

        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}


def test_assign_role_to_user_role_not_found(override_get_db):
    with client:
        user_repository = UserRepository(override_get_db)
        user = asyncio.run(user_repository.create_user(
            UserModel(username="test_user", password="test_password", email="test@example.com", role_id=2)))

        response = client.post(f"/role/user/{user.id}/role", json={"role_id": 999}, params={"token": "123"})

        assert response.status_code == 404
        assert response.json() == {"detail": "Role not found"}
