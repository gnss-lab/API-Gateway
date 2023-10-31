import asyncio
import contextlib
import os

from src.config.config import create_app
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from src.config.config import create_app, get_db
from src.core.repository.role_repository import RoleRepository
from src.core.database.db import Base

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
