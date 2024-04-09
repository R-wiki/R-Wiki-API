from typing import List

from pydantic import BaseModel

from .base import BaseResponse

from datetime import datetime

class LyricLineModel(BaseModel):
    time_mark   : str
    text        : str

class MusicLyricModel(BaseModel):
    music_id    : str
    name        : str
    lyrics      : List[LyricLineModel]

class LyricResponse(BaseResponse):
    data: List[MusicLyricModel]
    total: int