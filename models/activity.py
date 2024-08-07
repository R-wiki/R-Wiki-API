from typing import List
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse

class ActivityIdRequest(BaseModel):
    activity_id: str

class ActivityLinkModel(BaseModel):
    type: str
    id: str

class ActivityModel(BaseModel):
    id: str | None = None
    name: str
    note: str = ""
    time: datetime
    pic: List[str] = []
    url: str = ""
    link: List[ActivityLinkModel] = []

class ActivityListResponse(BaseResponse):
    data: List[ActivityModel] = []
    total: int