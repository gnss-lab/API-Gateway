import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.config.config import create_app
from src.core.database.db import Base


@pytest.fixture(scope='session')
def test_db():
    engine = create_engine('postgresql://localhost/test_myapp')  # Используйте свою строку подключения
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def test_client(test_db):
    app, _, _ = create_app()
    return TestClient(app)


@pytest.fixture
def db_session(test_db):
    return test_db
