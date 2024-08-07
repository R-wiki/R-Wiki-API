from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from .user import token_required

import api.activity as ActivityApi

from models.base import BaseResponse, PagingDataModel
from models.user import UserInfoModel, Level
from models.activity import ActivityModel, ActivityListResponse, ActivityIdRequest

from api.general import user_action_log

def get_paging_data(page:int=1, size:int=20):
    return PagingDataModel(page=page, size=size)

activity_api_router = APIRouter(
    prefix="/activity",
    tags=["activity"]
)

@activity_api_router.post("/create", response_model=BaseResponse)
def create_activity_item(activity_data: Annotated[ActivityModel, Body()], current_user: UserInfoModel = Depends(token_required)):
    result = ActivityApi.create_activity_item(activity_data)
    if not result:
        raise HTTPException(40302, "Create/Update activity failed.")
    user_action_log(current_user.username, "activity", "create", None, activity_data.name)
    return BaseResponse()

@activity_api_router.post("/approve", response_model=BaseResponse)
def approve_activity_item(activity_id_data: Annotated[ActivityIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = ActivityApi.approve_activity(activity_id_data.activity_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline activity failed.")
    user_action_log(current_user.username, "activity", "approve", activity_id_data.activity_id)
    return BaseResponse()

@activity_api_router.post("/decline", response_model=BaseResponse)
def decline_activity_item(activity_id_data: Annotated[ActivityIdRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    result = ActivityApi.approve_activity(activity_id_data.activity_id)
    if not result:
        raise HTTPException(40303, "Approve/Decline activity failed.")
    user_action_log(current_user.username, "activity", "decline", activity_id_data.activity_id)
    return BaseResponse()

@activity_api_router.get("/latest", response_model=ActivityListResponse)
def get_latest_activity(paging_data: PagingDataModel = Depends(get_paging_data)):
    data, count = ActivityApi.get_latest_activity_list(paging_data.page, paging_data.size)
    return ActivityListResponse(data=data, total=count)

@activity_api_router.get("/pending", response_model=ActivityListResponse)
def get_pending_activity(current_user: UserInfoModel = Depends(token_required), paging_data: PagingDataModel = Depends(get_paging_data)):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    data, count = ActivityApi.get_pending_activity_list(paging_data.page, paging_data.size)
    return ActivityListResponse(data=data, total=count)