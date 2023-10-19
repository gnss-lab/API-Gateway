import asyncio
import os

import pytest
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from starlette.testclient import TestClient

from src.core.database.db import Base
from src.core.database.models import RoleModel, UserModel
from src.core.repository.role_repository import RoleRepository
from src.config.config import create_app, get_db

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
    os.remove(db_path)


def test_register_user(override_get_db):
    with client:
        response = client.post("/user/register", json={
            "username": "testuser",
            "password": "testpassword",
            "email": "test@example.com"
        })
        print(response.json())
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User registered"
