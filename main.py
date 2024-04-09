from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi import utils as openapi_utils
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.general import load_config
load_config("config.ini")

from config.db import init_user_check
init_user_check()

from routers.music import music_api_router
from routers.user import user_api_router
from routers.pic import pic_api_router
from routers.video import video_api_router
from routers.lyric import lyric_api_router

from models.base import BaseResponse

app = FastAPI()

openapi_utils.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "status": {"title": "Message", "type": "integer", "default": 40201},
        "error": {"title": "Message", "type": "string", "default": "Request param error: <error_detail>"}, 
    },
}

app.include_router(user_api_router)
app.include_router(music_api_router)
app.include_router(lyric_api_router)
app.include_router(pic_api_router)
app.include_router(video_api_router)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(BaseResponse(status=exc.status_code, msg=exc.detail).model_dump(), status_code=200)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(BaseResponse(status=40201, msg="Request param error: " + str(exc)).model_dump(), status_code=200)