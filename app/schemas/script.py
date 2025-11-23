from datetime import datetime

from pydantic import BaseModel


class ScriptCreate(BaseModel):
    text: str


class ScriptResponse(BaseModel):
    id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True
