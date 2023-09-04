import pytest
from src.core.database.models import UserModel, TokenModel
from src.core.database.db import SessionLocal, engine
@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module", autouse=True)
def create_tables():
    UserModel.metadata.create_all(bind=engine)
    yield
    UserModel.metadata.drop_all(bind=engine)

def test_create_and_get_user(db_session):
    # Создаем пользователя
    user = UserModel(username="testuser1", password="testpassword", email="test1@example.com")
    db_session.add(user)
    db_session.commit()

    # Получаем пользователя из базы данных
    retrieved_user = db_session.query(UserModel).filter_by(username="testuser1").first()

    # Проверяем, что пользователь был успешно создан и получен
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser1"
    assert retrieved_user.email == "test1@example.com"

# Тест для создания и получения токена
def test_create_and_get_token(db_session):
    # Создаем пользователя
    user = UserModel(username="testuser2", password="testpassword", email="test2@example.com")
    db_session.add(user)
    db_session.commit()

    # Создаем токен для пользователя
    token = TokenModel(user_id=user.id, token="testtoken")
    db_session.add(token)
    db_session.commit()

    # Получаем токен из базы данных
    retrieved_token = db_session.query(TokenModel).filter_by(user_id=user.id).first()

    # Проверяем, что токен был успешно создан и получен
    assert retrieved_token is not None
    assert retrieved_token.token == "testtoken"
    assert retrieved_token.user_id == user.id


# Тест для удаления пользователя
def test_delete_user(db_session):
    # Создаем пользователя
    user = UserModel(username="testuser3", password="testpassword", email="unique_email@example.com")
    db_session.add(user)
    db_session.commit()

    # Удаляем пользователя
    db_session.delete(user)
    db_session.commit()

    # Проверяем, что пользователя больше нет в базе данных
    deleted_user = db_session.query(UserModel).filter_by(username="testuser3").first()
    assert deleted_user is None

