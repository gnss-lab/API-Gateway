from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from src.core.database.db import Base, engine

class RoleModel(Base):
    """
    Represents a role in the database.

    Attributes:
        id (int): The unique identifier of the role.
        name (str): The name of the role.
    """
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("UserModel", back_populates="role")

    def __str__(self):
        return self.name