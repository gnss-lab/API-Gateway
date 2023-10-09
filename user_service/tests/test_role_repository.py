import asyncio

import pytest
from src.core.repository.role_repository import RoleRepository
from src.core.database.models import RoleModel, UserModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


def test_create_role(db):
    role_repository = RoleRepository(db)
    role_name = "test_role"

    role = asyncio.run(role_repository.create_role(role_name))
    assert role.id is not None
    assert role.name == role_name


def test_delete_role(db):
    role_repository = RoleRepository(db)
    role_name = "test_role"

    role = asyncio.run(role_repository.create_role(role_name))
    role_id = role.id

    result = asyncio.run(role_repository.delete_role(role_id))
    assert result is True

    # Проверяем, что роль действительно удалена
    deleted_role = db.query(RoleModel).filter(RoleModel.id == role_id).first()
    assert deleted_role is None


def test_is_role_exist(db):
    role_repository = RoleRepository(db)
    role_name = "test_role"

    # Проверяем, что роль не существует
    assert asyncio.run(role_repository.is_role_exist(role_name)) is False

    # Создаем роль
    asyncio.run(role_repository.create_role(role_name))

    # Проверяем, что роль теперь существует
    assert asyncio.run(role_repository.is_role_exist(role_name)) is True


def test_get_all_roles(db):
    role_repository = RoleRepository(db)

    # Создаем несколько ролей
    asyncio.run(role_repository.create_role("role1"))
    asyncio.run(role_repository.create_role("role2"))
    asyncio.run(role_repository.create_role("role3"))

    # Получаем все роли
    roles = asyncio.run(role_repository.get_all_roles())

    # Проверяем, что количество ролей соответствует ожидаемому
    assert len(roles) == 3


def test_assign_role_to_user(db):
    role_repository = RoleRepository(db)

    # Создаем роль
    role = asyncio.run(role_repository.create_role("test_role"))

    # Создаем пользователя с валидным role_id
    user = UserModel(username="test_user", password="test_password", email="test@example.com", role_id=role.id)
    db.add(user)
    db.commit()

    # Присваиваем другую роль пользователю
    result = asyncio.run(role_repository.assign_role_to_user(user.id, role.id))
    assert result is True

    # Проверяем, что у пользователя по-прежнему установлен оригинальный role_id
    updated_user = db.query(UserModel).filter(UserModel.id == user.id).first()
    assert updated_user.role_id == role.id


def test_get_role_by_id(db):
    role_repository = RoleRepository(db)
    role_name = "test_role"

    # Создаем роль
    created_role = asyncio.run(role_repository.create_role(role_name))

    # Получаем роль по id
    retrieved_role = asyncio.run(role_repository.get_role_by_id(created_role.id))

    # Проверяем, что полученная роль совпадает с созданной
    assert retrieved_role.id == created_role.id
    assert retrieved_role.name == created_role.name


def test_get_role_by_name(db):
    role_repository = RoleRepository(db)
    role_name = "test_role"

    # Создаем роль
    created_role = asyncio.run(role_repository.create_role(role_name))

    # Получаем роль по имени
    retrieved_role = asyncio.run(role_repository.get_role_by_name(role_name))

    # Проверяем, что полученная роль совпадает с созданной
    assert retrieved_role.id == created_role.id
    assert retrieved_role.name == created_role.name


def test_get_user_role_by_id(db):
    role_repository = RoleRepository(db)

    role1 = asyncio.run(role_repository.create_role("role1"))

    # Создаем пользователя
    user = UserModel(username="test_user", password="test_password", email="test@example.com", role_id=role1.id)
    db.add(user)
    db.commit()

    # Создаем роль для переопределения
    role2 = asyncio.run(role_repository.create_role("role2"))

    # Присваиваем роль пользователю
    asyncio.run(role_repository.assign_role_to_user(user.id, role2.id))

    # Получаем роль пользователя
    user_role = asyncio.run(role_repository.get_user_role_by_id(user.id))

    # Проверяем, что роль пользователя совпадает с ожидаемой
    assert user_role == role2.id


def test_is_default_roles_exists(db):
    role_repository = RoleRepository(db)

    # Создаем стандартные роли
    asyncio.run(role_repository.create_default_roles())

    # Проверяем, что стандартные роли существуют
    assert role_repository.is_default_roles_exists() is True


def test_create_default_roles(db):
    role_repository = RoleRepository(db)

    # Создаем стандартные роли
    asyncio.run(role_repository.create_default_roles())

    # Проверяем, что стандартные роли действительно созданы
    assert db.query(RoleModel).filter_by(name="admin").first() is not None
    assert db.query(RoleModel).filter_by(name="user").first() is not None
