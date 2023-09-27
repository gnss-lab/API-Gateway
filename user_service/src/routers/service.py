from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.database.db import get_db
from src.core.database.models import ServiceModel, UserServiceModel
from src.core.repository.service_repository import ServiceRepository
from src.core.repository.user_repository import UserRepository

router = APIRouter()


@router.get("/services", summary="Get all services")
async def get_all_services(db: Session = Depends(get_db)):
    """
    Get a list of all services.

    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Services retrieved successfully.
    :statuscode 500: Internal server error.
    """
    try:
        service_repository = ServiceRepository(db)
        return await service_repository.get_all_services()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/services", summary="Create a new service")
async def create_service(service_name: str, db: Session = Depends(get_db)):
    """
    Create a new service.

    :param str service_name: The name of the new service.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Service created successfully.
    :statuscode 500: Internal server error.
    """
    try:
        service_repository = ServiceRepository(db)
        return await service_repository.create_service(service_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") # TODO : checking if there is a service with the same name


@router.delete("/services/{service_id}", summary="Delete a service by ID")
async def delete_service(service_id: int, db: Session = Depends(get_db)):
    """
    Delete a service by ID.

    :param int service_id: The ID of the service to delete.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Service deleted successfully.
    :statuscode 404: Service not found.
    :statuscode 500: Internal server error.
    """
    try:
        service_repository = ServiceRepository(db)
        deleted = await service_repository.delete_service(service_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Service deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/user/{user_id}/services", summary="Assign a service to a user")
async def assign_service_to_user(user_id: int, service_id: int, db: Session = Depends(get_db)):
    """
    Assign a service to a user.

    :param int user_id: The ID of the user.
    :param int service_id: The ID of the service to assign.
    :param Session db: Database session. A dependency created using `get_db`.

    :statuscode 200: Service assigned successfully.
    :statuscode 404: User or service not found.
    :statuscode 500: Internal server error.
    """
    try:
        user_repository = UserRepository(db)
        service_repository = ServiceRepository(db)

        user = await user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        service = await service_repository.get_service_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        user_service = UserServiceModel(user_id=user_id, service_id=service_id)
        assigned_service = await service_repository.assign_service_to_user(user_service)

        if assigned_service is not None:
            return {"message": "Service assigned successfully"}
        else:
            return {"message": "User already has access to this service"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
