from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from src.core.database.db import Base, engine, get_db
from src.core.database.models import UserModel, ServiceModel


class UserServiceModel(Base):
    """
    Represents the relationship between users and services in the database.

    Attributes:
        id (int): The unique identifier of the relationship.
        user_id (int): The ID of the associated user.
        service_id (int): The ID of the associated service.
        user (relationship): The relationship to the user associated with the relationship.
        service (relationship): The relationship to the service associated with the relationship.
    """
    __tablename__ = 'user_services'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.id', ondelete='CASCADE'), nullable=False)

    user = relationship("UserModel", back_populates="user_services")
    service = relationship("ServiceModel", back_populates="user_services")

    @property
    def user_name(self) -> str:
        with next(get_db()) as db:
            user = db.query(UserModel).filter(UserModel.id == self.user_id).first()
        return user.username if user else None

    @property
    def service_name(self) -> str:
        with next(get_db()) as db:
            service = db.query(ServiceModel).filter(ServiceModel.id == self.service_id).first()
        return service.name if service else None
