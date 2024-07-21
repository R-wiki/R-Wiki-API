from typing import Annotated, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from .user import token_required

import api.external as ExternalApi

from models.base import BaseResponse, PagingDataModel
from models.user import UserInfoModel, Level
from models.external import ChecklistResponse

from api.general import user_action_log

external_api_router = APIRouter(
    prefix="/external",
    tags=["external"]
)

@external_api_router.get("/checklist", response_model=ChecklistResponse)
def get_checklist(
        current_user: UserInfoModel = Depends(token_required)
    ):
    if current_user.level < Level.APPROVER:
        raise HTTPException(40105, "Permission denied, level < 2.")
    else:
        data, count = ExternalApi.get_checklist()
        return ChecklistResponse(data=data, total=count)
    
@external_api_router.get("/approve", response_model=BaseResponse)
def get_checklist(
        token: str = ""
    ):
    item_type, item_id = ExternalApi.verify_jwt(token)
    result = ExternalApi.approve(item_type, item_id)
    if result:
        user_action_log("External API", item_type, "approve", item_id)
        return BaseResponse()
    else:
        return BaseResponse(status=40303, msg="Failed")
    
@external_api_router.get("/decline", response_model=BaseResponse)
def get_checklist(
        token: str = ""
    ):
    item_type, item_id = ExternalApi.verify_jwt(token)
    result = ExternalApi.decline(item_type, item_id)
    if result:
        user_action_log("External API", item_type, "decline", item_id)
        return BaseResponse()
    else:
        return BaseResponse(status=40303, msg="Failed")