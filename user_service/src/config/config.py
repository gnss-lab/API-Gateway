import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from src.core.database.db import get_db
from src.core.repository.role_repository import RoleRepository
from src.core.repository.user_repository import UserRepository
from src.routers import consul, user, role, service
from src.config.envs import DICT_ENVS
from src.core.utils.consul_integration import register_consul
from src.routers import user
from fastapi.responses import JSONResponse

from fastapi import FastAPI, Depends, HTTPException, status

from loguru import logger

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

    role_repository = RoleRepository(next(get_db()))
    if not role_repository.is_default_roles_exists():
        asyncio.run(role_repository.create_default_roles())

    include_routers(app)

    if not DICT_ENVS["TEST"]:
        register_consul()

    is_admin_configured()
    logger.info(f"Is admin configured: {DICT_ENVS['ADMIN_CONFIGURED']}")

    db_url = f"postgresql://{DICT_ENVS['POSTGRES_USER']}:{DICT_ENVS['POSTGRES_PASSWORD']}@{DICT_ENVS['POSTGRES_HOST']}:{DICT_ENVS['POSTGRES_PORT']}/{DICT_ENVS['POSTGRES_DB']}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @app.middleware("http")
    async def check_admin_config(request, call_next):
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return await call_next(request)

        elif request.url.path.startswith("/user/register"):
            return await call_next(request)

        if not await is_admin_configured():
            error_response = JSONResponse(
                content={
                    "detail": "The administrator is not configured yet. Please set up an administrator account."},
                status_code=status.HTTP_403_FORBIDDEN,
            )
            return error_response
        return await call_next(request)

    return app, engine, SessionLocal


def include_routers(app):
    app.include_router(user.router, prefix="/user", tags=["user"])
    app.include_router(role.router, prefix="/role", tags=["role"])
    app.include_router(service.router, prefix="/service", tags=["service"])
    app.include_router(consul.router, tags=["consul"])


async def is_admin_configured():
    if not DICT_ENVS["ADMIN_CONFIGURED"]:
        user_repository = UserRepository(next(get_db()))
        if await user_repository.is_any_admin_exists():
            DICT_ENVS["ADMIN_CONFIGURED"] = True
        else:
            return False
    return True
