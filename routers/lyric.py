from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from .user import token_required

from models.base import BaseResponse, PagingDataModel
from models.user import UserInfoModel, Level
from models.lyric import LyricResponse

import api.lyric as LyricApi
from api.general import user_action_log

lyric_api_router = APIRouter(
    prefix="/lyric",
    tags=["lyric"]
)

@lyric_api_router.get("/search", response_model=LyricResponse)
def get_music_by_filter(
        q: str = "",
        ):
    data, count = LyricApi.search_lyric(q)
    return LyricResponse(data=data, total=count)