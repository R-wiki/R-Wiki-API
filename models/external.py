from typing import List

from pydantic import BaseModel

from .base import BaseResponse

from datetime import datetime

class ChecklistItemModel(BaseModel):
    item_id     : str
    item_type   : str
    content     : str
    token       : str

class ChecklistResponse(BaseResponse):
    data: List[ChecklistItemModel]
    total: int