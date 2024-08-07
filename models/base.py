from pydantic import BaseModel

class BaseResponse(BaseModel):
    status: int = 0
    msg:    str = "Success"
    data:   dict | list | None = None

class PagingDataModel(BaseModel):
    page: int | None = 1
    size: int | None = 20

class IdRequest(BaseModel):
    id: str = ""