from fastapi import APIRouter, UploadFile, File, Request, Response
from fastapi_gateway import route
from starlette import status

router = APIRouter()

# @route(
#     request_method=router.post,
#     service_url="http://46.149.73.242:8000",
#     gateway_path='/uploadfile',
#     form_params=['file'],
# )
@router.post("/uploadfile")
async def upload_file_test(request: Request, response: Response, file: UploadFile = File()):
    pass