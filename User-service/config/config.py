from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import routers.consul
from config.envs import DICT_ENVS
from core.consul_integration import register_consul
from routers import user

Base = declarative_base()

def create_app():
    app = FastAPI()

    include_routers(app)

    register_consul()

    db_url = f"postgresql://{DICT_ENVS['POSTGRES_USER']}:{DICT_ENVS['POSTGRES_PASSWORD']}@{DICT_ENVS['POSTGRES_HOST']}:{DICT_ENVS['POSTGRES_PORT']}/{DICT_ENVS['POSTGRES_DB']}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return app, engine, SessionLocal

def include_routers(app):
    app.include_router(routers.consul.router, tags=["consul"])
