from pydantic import BaseModel


class RoleCreateRequest(BaseModel):
    name: str


class RoleCreateResponse(BaseModel):
    id: int
    name: str


class RoleDeleteResponse(BaseModel):
    deleted: bool


class UserRoleAssignRequest(BaseModel):
    role_id: int

class RoleList(BaseModel):
    id: int
    name: str