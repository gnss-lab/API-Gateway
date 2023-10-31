import asyncio
import contextlib
import os

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


def test_create_service(override_get_db):
    with client:
        response = client.post("/service/services", params={
            "service_name": "testservice"
        })
        assert response.status_code == 200


def test_duplicate_service(override_get_db):
    with client:
        response = client.post("/service/services", params={
            "service_name": "testservice"
        })
        assert response.status_code == 200
        response = client.post("/service/services", params={
            "service_name": "testservice"
        })
        assert response.status_code == 400


def test_get_all_services_empty(override_get_db):
    with client:
        response = client.get("/service/services")
        assert response.status_code == 200
        assert response.json() == []


def test_get_all_services_with_data(override_get_db):
    with client:
        # Добавляем службу для теста
        response_create = client.post("/service/services", params={"service_name": "testservice"})
        assert response_create.status_code == 200

        # Запрашиваем все службы
        response_get = client.get("/service/services")
        assert response_get.status_code == 200

        # Проверяем, что полученные данные соответствуют ожиданиям
        assert len(response_get.json()) == 1
        assert response_get.json()[0]["name"] == "testservice"


def test_delete_service_success(override_get_db):
    with client:
        response_create = client.post("/service/services", params={"service_name": "testservice"})
        assert response_create.status_code == 200
        service_id = response_create.json()["id"]

        response_delete = client.delete(f"/service/services/{service_id}")
        assert response_delete.status_code == 200
        assert response_delete.json() == {"message": "Service deleted successfully"}


def test_delete_service_not_found(override_get_db):
    with client:
        response_delete = client.delete("/service/services/999")
        print(response_delete.json())
        assert response_delete.status_code == 404
        assert response_delete.json() == {"detail": "Service not found"}


def test_assign_service_to_user_success(override_get_db):
    with client:
        user_repository = UserRepository(override_get_db)
        user = asyncio.run(user_repository.create_user(
            UserModel(username="test_user", password="test_password", email="test@example.com", role_id=1)))
        service_repository = ServiceRepository(override_get_db)
        service = asyncio.run(service_repository.create_service("test_service"))

        response = client.post(f"service/user/{user.id}/services", params={"service_id": service.id})

        assert response.status_code == 200
        assert response.json() == {"message": "Service assigned successfully"}


def test_assign_service_to_user_user_not_found(override_get_db):
    with client:
        # Создаем службу, но не создаем пользователя
        service_repository = ServiceRepository(override_get_db)
        service = asyncio.run(service_repository.create_service("test_service"))

        # Вызываем endpoint для назначения службы несуществующему пользователю
        response = client.post("/service/user/999/services", params={"service_id": service.id})

        # Проверяем, что получаем ошибку 404
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}


def test_assign_service_to_user_service_not_found(override_get_db):
    with client:
        # Создаем пользователя, но не создаем службу
        user_repository = UserRepository(override_get_db)
        user = asyncio.run(user_repository.create_user(
            UserModel(username="test_user", password="test_password", email="test@example.com", role_id=1)))

        # Вызываем endpoint для назначения несуществующей службы пользователю
        response = client.post(f"/service/user/{user.id}/services", params={"service_id": 999})

        # Проверяем, что получаем ошибку 404
        assert response.status_code == 404
        assert response.json() == {"detail": "Service not found"}


def test_assign_service_to_user_already_has_access(override_get_db):
    with client:
        # Создаем пользователя и службу
        user_repository = UserRepository(override_get_db)
        user = asyncio.run(user_repository.create_user(
            UserModel(username="test_user", password="test_password", email="test@example.com", role_id=1)))
        service_repository = ServiceRepository(override_get_db)
        service = asyncio.run(service_repository.create_service("test_service"))

        # Назначаем службу пользователю
        user_service = UserServiceModel(user_id=user.id, service_id=service.id)
        asyncio.run(service_repository.assign_service_to_user(user_service))

        # Вызываем endpoint для назначения той же службы пользователю
        response = client.post(f"/service/user/{user.id}/services", params={"service_id": service.id})

        # Проверяем, что получаем сообщение об уже имеющемся доступе
        assert response.status_code == 200
        assert response.json() == {"message": "User already has access to this service"}
