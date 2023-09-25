from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database.db import get_db
from src.core.database.models import RoleModel
from src.core.repository.role_repository import RoleRepository
from src.core.repository.user_repository import UserRepository
from src.dtos.role import UserRoleAssignRequest, RoleDeleteResponse, RoleCreateResponse, RoleCreateRequest, RoleList

router = APIRouter()


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


@router.post("/roles", response_model=RoleCreateResponse, summary="Create a new role")
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
        return await role_repository.create_role(role_request.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/roles/{role_id}", response_model=RoleDeleteResponse, summary="Delete a role by ID")
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


@router.post("/user/{user_id}/roles", response_model=bool)
async def assign_role_to_user(role_request: UserRoleAssignRequest, db: Session = Depends(get_db)):
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

        user = await user_repository.get_user_by_id(role_request.user_id)
        if user:
            role = await role_repository.get_role_by_id(role_request.role_id)
            if role:
                await role_repository.assign_role_to_user(role_request.user_id, role_request.role_id)
                return True
            else:
                raise HTTPException(status_code=404, detail="Role not found")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
