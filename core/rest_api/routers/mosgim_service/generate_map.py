from fastapi import APIRouter, status, Request, File, HTTPException, Response, UploadFile
from loguru import logger
from core.rest_api.modules.route_service import route_service
from pprint import pformat
from core.config.envs import DICT_ENVS
from fastapi_gateway import route

router = APIRouter()


# @route_service(
#     request_method=router.post,
#     path="/mosgim/generate-map",
#     status_code=status.HTTP_200_OK,
#     service_url=DICT_ENVS["MOSGIM_SERVICE_URL"]
# )

@route(
    request_method=router.post,
    service_url=DICT_ENVS["MOSGIM_SERVICE_URL"],
    gateway_path="/mosgim/generate-map",
    service_path="/mosgim/generate-map",
    status_code=status.HTTP_200_OK,
    query_params=["mag_type", "const"],
    form_params=["file"]
)
async def generate_map(request: Request, response: Response, mag_type: str, const: str, file: UploadFile = File()):
    pass


    # if not "X-Context-Type" in request.headers:
    #     raise HTTPException(
    #         status_code=409, detail="Header X-Context-Type not found")

    # ret = {
    #     "data": {
    #         "file": file
    #     },
    #     "params": {
    #         "mag_type": mag_type,
    #         "const": const
    #     },
    #     "headers": {
    #         "X-Context-Type": request.headers.get("X-Context-Type")
    #     }
    # }

    # return ret


# async def generate_map(request: Request, mag_type: str, const: str, file: bytes = File()):

#     if not "X-Context-Type" in request.headers:
#         raise HTTPException(
#             status_code=409, detail="Header X-Context-Type not found")

#     ret = {
#         "data": {
#             "file": file
#         },
#         "params": {
#             "mag_type": mag_type,
#             "const": const
#         },
#         "headers": {
#             "X-Context-Type": request.headers.get("X-Context-Type")
#         }
#     }

#     return ret
