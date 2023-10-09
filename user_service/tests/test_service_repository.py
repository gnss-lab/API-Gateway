import asyncio

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.repository.role_repository import RoleRepository
from src.core.repository.service_repository import ServiceRepository
from src.core.database.models import ServiceModel, UserModel, UserServiceModel, RoleModel


@pytest.fixture
def db():
    engine = create_engine('sqlite:///:memory:')
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    RoleModel.metadata.create_all(bind=engine)
    UserModel.metadata.create_all(bind=engine)

    yield db

    RoleModel.metadata.drop_all(bind=engine)
    UserModel.metadata.drop_all(bind=engine)
    db.close()


def test_create_service(db):
    service_repository = ServiceRepository(db)
    service_name = "test_service"

    # Проверим создание сервиса
    service = asyncio.run(service_repository.create_service(service_name))
    assert service.id is not None
    assert service.name == service_name


def test_delete_service(db):
    service_repository = ServiceRepository(db)
    service_name = "test_service"

    # Создадим сервис
    service = asyncio.run(service_repository.create_service(service_name))
    service_id = service.id

    # Проверим удаление сервиса
    result = asyncio.run(service_repository.delete_service(service_id))
    assert result is True

    # Проверим, что сервис действительно удален
    deleted_service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    assert deleted_service is None


def test_get_all_services(db):
    service_repository = ServiceRepository(db)

    # Создадим несколько сервисов
    asyncio.run(service_repository.create_service("service1"))
    asyncio.run(service_repository.create_service("service2"))
    asyncio.run(service_repository.create_service("service3"))

    # Получим все сервисы
    services = asyncio.run(service_repository.get_all_services())

    # Проверим, что количество сервисов соответствует ожидаемому
    assert len(services) == 3


def test_assign_service_to_user(db):
    service_repository = ServiceRepository(db)
    role_repository = RoleRepository(db)

    # Создадим роль
    role = asyncio.run(role_repository.create_role("test_role"))

    # Создадим сервис
    service = asyncio.run(service_repository.create_service("test_service"))

    # Создадим пользователя
    user = UserModel(username="test_user", password="test_password", email="test@example.com", role_id=role.id)
    db.add(user)
    db.commit()

    # Проверим присвоение сервиса пользователю
    result = asyncio.run(service_repository.assign_service_to_user(
        UserServiceModel(user_id=user.id, service_id=service.id)
    ))
    assert result is True

    # Проверим, что у пользователя есть присвоенный сервис
    user_services = db.query(UserServiceModel).filter_by(user_id=user.id, service_id=service.id).first()
    assert user_services is not None
