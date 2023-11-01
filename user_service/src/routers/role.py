from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.envs import DICT_ENVS
from src.core.database.db import get_db
from src.core.repository.role_repository import RoleRepository
from src.core.repository.user_repository import UserRepository
from src.dtos.role import UserRoleAssignRequest, RoleDeleteResponse, RoleCreateResponse, RoleCreateRequest, RoleList

router = APIRouter()


async def check_admin_token(token):
    user_repository = UserRepository(next(get_db()))
    print(await user_repository.is_admin_token(token))
    try:
        user_repository = UserRepository(next(get_db()))
        print(await user_repository.is_admin_token(token))
        if not await user_repository.is_admin_token(token):
            raise HTTPException(status_code=401, detail="Not an administrator token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/roles", response_model=List[RoleList], summary="Get all roles")
async def get_all_roles(db: Session = Depends(get_db)):
    """
    Get a list of all roles.

    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Roles retrieved successfully.
    :statuscode 500: Internal server error.
    """
    try:
        role_repository = RoleRepository(db)
        return await role_repository.get_all_roles()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/roles", response_model=RoleCreateResponse, summary="Create a new role",
             dependencies=[Depends(check_admin_token)])
async def create_role(role_request: RoleCreateRequest, db: Session = Depends(get_db)):
    """
    Create a new role.

    :param RoleCreateRequest role_request: Request to create a new role.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Role created successfully.
    :statuscode 500: Internal server error.
    """
    try:
        role_repository = RoleRepository(db)
        if await role_repository.is_role_exist(role_request.name):
            raise HTTPException(status_code=400,
                                detail="Role with the same name already exists")  # TODO : always returns 500 error
        else:
            # Возвращать данные или что-то еще, если роль была успешно создана
            return await role_repository.create_role(role_request.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/roles/{role_id}", response_model=RoleDeleteResponse, summary="Delete a role by ID",
               dependencies=[Depends(check_admin_token)])
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    """
    Delete a role by ID.

    :param int role_id: The ID of the role to delete.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Role deleted successfully.
    :statuscode 404: Role not found.
    :statuscode 500: Internal server error.
    """
    try:
        role_repository = RoleRepository(db)
        deleted = await role_repository.delete_role(role_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Role not found")
        return RoleDeleteResponse(deleted=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}/role", summary="Get user roles by ID")
async def get_user_roles(user_id: int, db: Session = Depends(get_db)):
    """
    Get role of a user by user ID.

    :param int user_id: The ID of the user.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Roles retrieved successfully.
    :statuscode 404: User not found.
    :statuscode 500: Internal server error.
    """
    try:
        role_repository = RoleRepository(db)
        role_id = await role_repository.get_user_role_by_id(user_id)
        role = await role_repository.get_role_by_id(role_id)
        if role is not None:
            return role
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/user/{user_id}/role", response_model=bool, dependencies=[Depends(check_admin_token)])
async def assign_role_to_user(user_id: int, role_request: UserRoleAssignRequest, db: Session = Depends(get_db)):
    """
    Assign a role to a user.

    :param int user_id: The ID of the user.
    :param UserRoleAssignRequest role_request: Request to assign a role to a user.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Role assigned successfully.
    :statuscode 404: User or role not found.
    :statuscode 500: Internal server error.
    """
    try:
        role_repository = RoleRepository(db)
        user_repository = UserRepository(db)

        user = await user_repository.get_user_by_id(user_id)
        if user:
            role = await role_repository.get_role_by_id(role_request.role_id)
            if role:
                await role_repository.assign_role_to_user(user_id, role_request.role_id)
                return True
            else:
                raise HTTPException(status_code=404, detail="Role not found")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
