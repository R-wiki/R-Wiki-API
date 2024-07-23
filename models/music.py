from typing import List

from pydantic import BaseModel

from .base import BaseResponse

from datetime import datetime


class PlatformModel(BaseModel):
    netease: str | None = None
    qq_music: str | None = None
    bilibili: str | None = None

class StaffModel(BaseModel):
    type: str
    name: str

class MusicInfoModel(BaseModel):
    id: str | None = None
    name: str
    music_type: str
    language: str
    solo: str
    publish_time: datetime | None = None
    album: str
    pv_mv: str | None = None
    platform: PlatformModel = PlatformModel()
    staff: List[StaffModel] = []
    note: str | None = ""

class MusicIdRequest(BaseModel):
    music_id: str

class MusicInfoResponse(BaseResponse):
    data: List[MusicInfoModel]
    total: int

class MusicDetailModel(MusicInfoModel):
    cover_url : str | None = None
    play_url : str | None = None
    lyric : str | None = None

class MusicDetailResponse(BaseResponse):
    data : MusicDetailModel