from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from config.envs import DICT_ENVS

DATABASE_URL = f"postgresql://{DICT_ENVS['POSTGRES_USER']}:{DICT_ENVS['POSTGRES_PASSWORD']}@{DICT_ENVS['POSTGRES_HOST']}:{DICT_ENVS['POSTGRES_PORT']}/{DICT_ENVS['POSTGRES_DB']}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """
    Get a database session.

    :return: A database session.
    :rtype: Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
