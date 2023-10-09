from sqlalchemy.orm import Session
from src.core.database.models import ServiceModel, UserServiceModel


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create_service(self, name: str):
        service = ServiceModel(name=name)
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    async def delete_service(self, service_id: int):
        if service := self.db.query(ServiceModel).filter(ServiceModel.id == service_id).first():
            self.db.delete(service)
            self.db.commit()
            return True
        return False

    async def get_all_services(self):
        return self.db.query(ServiceModel).all()

    async def assign_service_to_user(self, user_service: UserServiceModel):
        existing_user_service = self.db.query(UserServiceModel).filter(
            UserServiceModel.user_id == user_service.user_id,
            UserServiceModel.service_id == user_service.service_id
        ).first()

        if existing_user_service:
            return False

        self.db.add(user_service)
        self.db.commit()
        return True

    async def get_service_by_id(self, service_id: int):
        return self.db.query(ServiceModel).filter(ServiceModel.id == service_id).first()

    async def get_service_by_name(self, service_name: str):
        return self.db.query(ServiceModel).filter(ServiceModel.name == service_name).first()
