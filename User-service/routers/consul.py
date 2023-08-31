from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def check_health():
    """
    Endpoint to check the health status of the service.
    """
    return {"message": "Service is healthy"}
