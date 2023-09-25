from sqlalchemy.orm import Session
from src.core.database.models import RoleModel, UserModel


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create_role(self, name: str):
        role = RoleModel(name=name)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    async def delete_role(self, role_id: int):
        if role := self.db.query(RoleModel).filter(RoleModel.id == role_id).first():
            self.db.delete(role)
            self.db.commit()
            return True
        return False

    async def get_all_roles(self):
        return self.db.query(RoleModel).all()

    async def assign_role_to_user(self, user_id: int, role_id: int):
        if user := self.db.query(UserModel).filter(UserModel.id == user_id).first():
            user.role_id = role_id
            self.db.commit()
            return True
        return False

    async def get_role_by_id(self, role_id):
        return self.db.query(RoleModel).filter(RoleModel.id == role_id).first()
