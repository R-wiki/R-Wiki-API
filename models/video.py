from typing import List
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse

class VideoItemModel(BaseModel):
    id: str | None = None
    name: str
    publish_time: datetime
    type: str
    duration: int
    bvid: str
    cid: str = ""
    show: bool = False

class VideoListResponse (BaseResponse):
    data: List[VideoItemModel] = []
    total: int

class VideoDetailResponse(BaseResponse):
    data: VideoItemModel

class VideoIdRequest(BaseModel):
    video_id: str
