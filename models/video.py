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

class VideoListResponse (BaseResponse):
    data: List[VideoItemModel] = []
    total: int

class VideoDetailModel(VideoItemModel):
    url: str = ""

class VideoDetailResponse(BaseResponse):
    data: VideoDetailModel
    
class VideoFastCreateRequest(BaseModel):
    bvid: str
    type: str = ""
