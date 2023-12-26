from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from src.core.database.db import Base, engine


class ServiceModel(Base):
    """
    Represents a service in the database.

    Attributes:
        id (int): The unique identifier of the service.
        name (str): The name of the service.
        user_services (relationship): The relationship to the users associated with the service.
    """
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    user_services = relationship("UserServiceModel", back_populates="service", cascade="all, delete-orphan")

