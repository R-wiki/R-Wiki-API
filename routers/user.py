from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Header, Body

from pydantic import Field

from models.base import BaseResponse
from models.user import UserLoginRequest, UpdatePasswordRequest, CreateUserRequest
from models.user import UserInfoModel, TokenModel, Level
from models.user import UserLoginResponse, UserInfoResponse, CreateUserResponse, UserListResponse

import api.user as UserApi
from api.general import user_action_log

user_api_router = APIRouter(
    prefix="/user",
    tags=["user"]
)

def token_required(x_token:Annotated[str, Header()]):
    user_info = UserApi.get_user_data_by_toekn(x_token)
    return user_info           

@user_api_router.post("/login", response_model=UserLoginResponse)
def user_login(user_login_data: UserLoginRequest):
    jwt_payload = UserApi.get_jwt_by_user(user_login_data)
    user_action_log(user_login_data.username, "user", "login")
    return UserLoginResponse(data=TokenModel(token=jwt_payload))

@user_api_router.get("/me", response_model=UserInfoResponse)
def get_user_info(current_user: UserInfoModel = Depends(token_required)):
    return UserInfoResponse(data=current_user)

@user_api_router.get("/list", response_model=UserListResponse)
def get_user_list(current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.DEVELOVER:
        raise HTTPException(40105, "Permission denied, level < 3.")
    user_list = UserApi.get_user_list()
    return UserListResponse(data=user_list)

@user_api_router.post("/update_password", response_model=BaseResponse)
def update_password(password: Annotated[UpdatePasswordRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    UserApi.update_password(current_user, password.password)
    user_action_log(current_user.username, "user", "update_password")
    return BaseResponse(status=0, msg="Success")

@user_api_router.post("/create_user", response_model=CreateUserResponse)
def create_user(new_user_info: Annotated[CreateUserRequest, Body()], current_user: UserInfoModel = Depends(token_required)):
    if current_user.level < Level.ADMIN:
        raise HTTPException(40105, "Permission denied, level < 4.")
    new_user = UserApi.create_user(new_user_info)
    user_action_log(current_user.username, "user", "create_user", new_user.id, new_user_info.username)
    return CreateUserResponse(data=new_user)