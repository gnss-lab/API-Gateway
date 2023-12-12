from loguru import logger
from sqlalchemy.orm import Session
from src.core.database.models import UserModel
from src.core.database.models.RoleModel import RoleModel


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

    async def is_role_exist(self, role):
        return self.db.query(RoleModel).filter(RoleModel.name == role).first() is not None

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

    async def get_role_by_name(self, role_name):
        if role := self.db.query(RoleModel).filter(RoleModel.name == role_name).first():
            return role
        return None

    async def get_user_role_by_id(self, user_id):
        if user := (
                self.db.query(UserModel)
                        .filter(UserModel.id == user_id)
                        .first()
        ):
            return user.role_id
        return None

    def is_default_roles_exists(self):
        try:
            db_role_admin = self.db.query(RoleModel).filter(RoleModel.name == "admin").first()
            db_role_user = self.db.query(RoleModel).filter_by(name="user").first()

            return db_role_admin is not None and db_role_user is not None
        finally:
            self.db.close()

    async def create_default_roles(self):
        default_roles = ["admin", "user"]

        for role_name in default_roles:
            role = await self.create_role(role_name)
