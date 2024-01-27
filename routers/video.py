from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from .user import token_required

from models.base import BaseResponse, PagingDataModel
from models.user import UserInfoModel, Level
from models.video import VideoItemModel, VideoDetailResponse, VideoListResponse, VideoIdRequest, VideoFastCreateRequest

import api.video as VideoApi

video_api_router = APIRouter(
    prefix="/video",
    tags=["video"]
)

def get_paging_data(page:int=1, size:int=20):
    return PagingDataModel(page=page, size=size)

@video_api_router.post("/create",response_model=BaseResponse)
def create_video_item(video_data: Annotated[VideoItemModel, Body()], current_user: UserInfoModel = Depends(token_required)):
    result = VideoApi.create_video_item(video_data)
    if not result:
        raise HTTPException(40302, "Create/Update video failed.")
    return BaseResponse()

@video_api_router.post("/fast_create", response_model=BaseResponse)
def create_video_by_bvid(bvid_data: Annotated[VideoFastCreateRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    result = VideoApi.create_video_by_bvid(bvid_data.bvid, bvid_data.type)
    if not result:
        raise HTTPException(40302, "Create/Update video failed.")
    return BaseResponse()

@video_api_router.post("/approve", response_model=BaseResponse)
def approve_video_item(video_id_data: Annotated[VideoIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = VideoApi.approve_video(video_id_data.video_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline video failed.")
    return BaseResponse()

@video_api_router.post("/decline", response_model=BaseResponse)
def decline_video_item(video_id_data: Annotated[VideoIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = VideoApi.decline_music(video_id_data.music_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline video failed.")
    return BaseResponse()

@video_api_router.get("/pending", response_model=VideoListResponse)
def get_pending_video(current_user: UserInfoModel = Depends(token_required), paging_data: PagingDataModel = Depends(get_paging_data)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    data, count = VideoApi.get_pending_video_list(paging_data.page, paging_data.size)
    return VideoListResponse(data=data, total=count)

@video_api_router.get("/latest", response_model=VideoListResponse)
def get_latest_video(paging_data: PagingDataModel = Depends(get_paging_data)):
    data, count = VideoApi.get_latest_video_list(paging_data.page, paging_data.size)
    return VideoListResponse(data=data, total=count)

@video_api_router.get("/filter", response_model=VideoListResponse)
def get_video_by_filter(
        q: str = "",
        duration   : List[str] = Query(default=[]),
        video_type  : List[str] = Query(default=[]),
        year        : List[int] = Query(default=[]),
        month       : List[int] = Query(default=[]),
        paging_data: PagingDataModel = Depends(get_paging_data)
        ):
    data, count = VideoApi.get_video_list_by_filter(q, duration, video_type, year, month, paging_data.page, paging_data.size)
    return VideoListResponse(data=data, total=count)

@video_api_router.get("/detail", response_model=VideoDetailResponse)
def get_video_detail(video_id : str):
    data = VideoApi.get_video_detail(video_id)
    return VideoDetailResponse(data=data)
