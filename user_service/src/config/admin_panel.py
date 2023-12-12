import asyncio

from sqladmin import Admin, ModelView
from sqladmin.fields import SelectField, QuerySelectField
from sqlalchemy.orm import Session

from src.core.database.db import get_db, engine
from src.core.database.models import UserModel, RoleModel, UserServiceModel, ServiceModel, TokenModel
from src.core.repository.role_repository import RoleRepository

role_repository = RoleRepository(next(get_db()))
if not role_repository.is_default_roles_exists():
    asyncio.run(role_repository.create_default_roles())


def config_admin_panel(app):
    admin = Admin(app, engine)

    admin.add_view(Users)
    admin.add_view(Roles)
    admin.add_view(UserServices)
    admin.add_view(Services)
    admin.add_view(Tokens)


class Users(ModelView, model=UserModel):
    column_list = [UserModel.id, UserModel.username, UserModel.email, "role_name", UserModel.tokens]


class Roles(ModelView, model=RoleModel):
    column_list = [RoleModel.id, RoleModel.name]


class UserServices(ModelView, model=UserServiceModel):
    column_list = [UserServiceModel.id, UserServiceModel.user_id, UserServiceModel.service_id]


class Services(ModelView, model=ServiceModel):
    column_list = [ServiceModel.id, ServiceModel.name]


class Tokens(ModelView, model=TokenModel):
    column_list = [TokenModel.id, TokenModel.token, TokenModel.user_id]
