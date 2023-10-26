import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from src.config.config import create_app
from src.core.database.models import UserModel
from src.core.database.db import Base
from src.core.database.db import SessionLocal, engine
from src.core.repository.role_repository import RoleRepository

app, _, _ = create_app()
client = TestClient(app)


@pytest.fixture()
def db_session_consul():
    db_path = 'test_db.sqlite'
    engine = create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    print("Tables in the database:", inspector.get_table_names())

    role_repository = RoleRepository(db)
    if not role_repository.is_default_roles_exists():
        asyncio.run(role_repository.create_default_roles())

    yield db

    Base.metadata.drop_all(bind=engine)
    db.close()


def test_health_endpoint(db_session_consul):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"message": "Service is healthy"}
