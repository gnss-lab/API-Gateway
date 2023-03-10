from fastapi import APIRouter, UploadFile, File, Request, Response
from fastapi_gateway import route
from starlette import status
from core.calery.tasks import get_upload_file

router = APIRouter()

@route(
    request_method=router.post,
    service_url="http://46.149.73.242:8000",
    gateway_path='/uploadfile',
    form_params=['file'],
)
# @router.post("/uploadfile")
async def upload_file_test(request: Request, response: Response, file: UploadFile = File()):
    pass

@router.post("/uploadfile-async")
async def upload_file_test(request: Request, response: Response, file: UploadFile = File()):
    contents: bytes = await file.read()
    task = get_upload_file.apply_async(args=[contents])
    return {"task_id": task.id}
