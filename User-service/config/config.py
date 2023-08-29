from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.envs import DICT_ENVS

Base = declarative_base()

def create_app():
    app = FastAPI()

    db_url = f"postgresql://{DICT_ENVS['POSTGRES_USER']}:{DICT_ENVS['POSTGRES_PASSWORD']}@{DICT_ENVS['POSTGRES_HOST']}:{DICT_ENVS['POSTGRES_PORT']}/{DICT_ENVS['POSTGRES_DB']}"
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return app, engine, SessionLocal