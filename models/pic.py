from typing import List
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse

class PicItemModel(BaseModel):
    id: str | None = ""
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

class PicDetailResponse(BaseResponse):
    data: PicDetailModel = []