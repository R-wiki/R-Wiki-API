from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, Field

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from .user import token_required

from models.base import BaseResponse, PagingDataModel
from models.user import UserInfoModel, Level
from models.pic import PicItemModel, PicIdRequest, PicListResponse, PicDetailModel, PicDetailResponse
from api.general import user_action_log

import api.pic as PicApi

pic_api_router = APIRouter(
    prefix="/pic",
    tags=["pic"]
)

def get_paging_data(page:int=1, size:int=20):
    return PagingDataModel(page=page, size=size)

@pic_api_router.post("/create",response_model=BaseResponse)
def create_pic_item(pic_data: Annotated[PicItemModel, Body()], current_user: UserInfoModel = Depends(token_required)):
    result = PicApi.create_pic_item(pic_data)
    if not result:
        raise HTTPException(40302, "Create/Update pic failed.")
    user_action_log(current_user.username, "pic", "create", None, pic_data.name)
    return BaseResponse()

@pic_api_router.post("/approve", response_model=BaseResponse)
def approve_pic_item(pic_id_data: Annotated[PicIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = PicApi.approve_pic(pic_id_data.pic_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline pic failed.")
    user_action_log(current_user.username, "pic", "approve", pic_id_data.pic_id, "")
    return BaseResponse()

@pic_api_router.post("/decline", response_model=BaseResponse)
def decline_pic_item(pic_id_data: Annotated[PicIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = PicApi.decline_pic(pic_id_data.pic_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline pic failed.")
    user_action_log(current_user.username, "pic", "decline", pic_id_data.pic_id, "")
    return BaseResponse()

@pic_api_router.get("/pending", response_model=PicListResponse)
def get_pending_pic(current_user: UserInfoModel = Depends(token_required), paging_data: PagingDataModel = Depends(get_paging_data)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    data, count = PicApi.get_pending_pic_list(paging_data.page, paging_data.size)
    return PicListResponse(data=data, total=count)

@pic_api_router.get("/latest", response_model=PicListResponse)
def get_latest_pic(paging_data: PagingDataModel = Depends(get_paging_data)):
    data, count = PicApi.get_latest_pic_list(paging_data.page, paging_data.size)
    return PicListResponse(data=data, total=count)

@pic_api_router.get("/filter", response_model=PicListResponse)
def get_pic_by_filter(
        q: str = "",
        pic_type:   List[str] = Query(default=[]),
        year:       List[int] = Query(default=[]),
        month:      List[int] = Query(default=[]),
        paging_data: PagingDataModel = Depends(get_paging_data)
        ):
    data, count = PicApi.get_pic_list_by_filter(q, pic_type, year, month, paging_data.page, paging_data.size)
    return PicListResponse(data=data, total=count)

@pic_api_router.get("/detail", response_model=PicDetailResponse)
def get_pic_detail(pic_id : str):
    data = PicApi.get_pic_detail(pic_id)
    return PicDetailResponse(data=data)