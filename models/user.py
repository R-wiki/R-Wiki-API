from enum import IntEnum

from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse

class Level(IntEnum):
    USER = 1
    APPROVER = 2
    DEVELOVER = 3
    ADMIN = 4

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenModel(BaseModel):
    token: str

class UserLoginResponse(BaseResponse):
    data: TokenModel

class UserInfoModel(BaseModel):
    id: str
    username: str
    level: Level

class UserInfoResponse(BaseResponse):
    data: UserInfoModel

class UpdatePasswordRequest(BaseModel):
    password: str

class CreateUserRequest(BaseModel):
    username: str
    level: Level

class NewUserModel(BaseModel):
    id: str
    password: str

class CreateUserResponse(BaseResponse):
    data: NewUserModel
