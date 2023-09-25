from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.routers import consul, user, role
from src.config.envs import DICT_ENVS
from src.core.utils.consul_integration import register_consul
from src.routers import user

Base = declarative_base()

def create_app():
    tags_metadata = [
        {
            "name": "default",
            "description": "Operations with users.",
            "x-auto-generate-in-api-gateway": True,
        }
    ]

    app = FastAPI(openapi_tags=tags_metadata)

    include_routers(app)

    if not DICT_ENVS["TEST"]:
        register_consul()

    db_url = f"postgresql://{DICT_ENVS['POSTGRES_USER']}:{DICT_ENVS['POSTGRES_PASSWORD']}@{DICT_ENVS['POSTGRES_HOST']}:{DICT_ENVS['POSTGRES_PORT']}/{DICT_ENVS['POSTGRES_DB']}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return app, engine, SessionLocal

def include_routers(app):
    app.include_router(user.router, prefix="/user", tags=["user"])
    app.include_router(role.router, prefix="/role", tags=["role"])
    app.include_router(consul.router, tags=["consul"])
