from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse

class PicModel(BaseModel):
    pic_id: int = Field(..., title="图片ID")
    pic_url: str = Field(..., title="图片URL")

class PicResponse(BaseResponse):
    data: PicModel = Field(..., title="图片信息")