
from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from .user import token_required

from models.base import BaseResponse, PagingDataModel
from models.user import UserInfoModel, Level
from models.music import MusicIdRequest
from models.music import MusicInfoModel
from models.music import MusicInfoResponse, MusicDetailResponse

import api.music as MusicApi

muisc_api_router = APIRouter(
    prefix="/music",
    tags=["music"]
)

def get_paging_data(page:int=1, size:int=20):
    return PagingDataModel(page=page, size=size)

@muisc_api_router.post("/create", response_model=BaseResponse)
def create_music_item(music_data: Annotated[MusicInfoModel, Body()], current_user: UserInfoModel = Depends(token_required)):
    result = MusicApi.create_music_item(music_data)
    if not result:
        raise HTTPException(40302, "Create/Update music failed.")
    return BaseResponse()

@muisc_api_router.post("/approve", response_model=BaseResponse)
def approve_music_item(music_id_data: Annotated[MusicIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = MusicApi.approve_music(music_id_data.music_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline music failed.")
    return BaseResponse()

@muisc_api_router.post("/decline", response_model=BaseResponse)
def decline_music_item(music_id_data: Annotated[MusicIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = MusicApi.decline_music(music_id_data.music_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline music failed.")
    return BaseResponse()

@muisc_api_router.get("/pending", response_model=MusicInfoResponse)
def get_pending_music(current_user: UserInfoModel = Depends(token_required), paging_data: PagingDataModel = Depends(get_paging_data)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    data, count = MusicApi.get_pending_music_list(paging_data.page, paging_data.size)
    return MusicInfoResponse(data=data, total=count)

@muisc_api_router.get("/latest", response_model=MusicInfoResponse)
def get_latest_music(paging_data: PagingDataModel = Depends(get_paging_data)):
    data, count = MusicApi.get_latest_music_list(paging_data.page, paging_data.size)
    return MusicInfoResponse(data=data, total=count)

@muisc_api_router.get("/filter", response_model=MusicInfoResponse)
def get_music_by_filter(
        q: str = "",
        album:    List[str] = Query(default=[]),
        solo:     List[str] = Query(default=[]),
        platform: List[str] = Query(default=[]),
        language: List[str] = Query(default=[]),
        paging_data: PagingDataModel = Depends(get_paging_data)
        ):
    data, count = MusicApi.get_music_list_by_filter(q, album, solo, platform, language, paging_data.page, paging_data.size)
    return MusicInfoResponse(data=data, total=count)

@muisc_api_router.get("/detail", response_model=MusicDetailResponse)
def get_music_detail(music_id : str):
    data = MusicApi.get_music_detail(music_id)
    return MusicDetailResponse(data=data)