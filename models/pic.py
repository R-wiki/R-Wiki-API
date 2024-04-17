from typing import List
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse

class PicItemModel(BaseModel):
    id: str | None = None
    name: str
    date: datetime
    type: str
    pics: List[str] = []
    cover: str = ""
    note: str = ""
    show: bool = False

class PicDetailModel(PicItemModel):
    urls: List[str] = []

class PicListResponse(BaseResponse):
    data: List[PicItemModel] = []
    total: int

class PicDetailResponse(BaseResponse):
    data: PicDetailModel

class PicIdRequest(BaseModel):
    pic_id: str

class SinglePicModel(BaseModel):
    id: str = ""
    set_id: str = ""
    path: str = ""
    url: str = ""
    
class SinglePicListResponse(BaseResponse):
    data: List[SinglePicModel] = []
    total: int