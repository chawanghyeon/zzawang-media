from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    script_id: int
    audio_path: str
    recognized_text: str
    accuracy_score: float
    missing_words: Optional[str] = None
    feedback_text: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    script_id: int
    audio_path: str
    recognized_text: str
    accuracy_score: float
    missing_words: Optional[str]
    feedback_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SubmitRequest(BaseModel):
    script_id: int


class SimilarScript(BaseModel):
    id: int
    text: str
    similarity_score: float


class SubmitResponse(BaseModel):
    feedback_id: int
    recognized_text: str
    accuracy_score: float
    missing_words: Optional[str]
    feedback_text: Optional[str]
    similar_scripts: List[SimilarScript] = []
