from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    audio_path = Column(String, nullable=False)
    recognized_text = Column(Text, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    missing_words = Column(Text)
    feedback_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    script = relationship("Script")
