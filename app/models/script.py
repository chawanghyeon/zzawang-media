from sqlalchemy import Column, DateTime, Integer, LargeBinary, String
from sqlalchemy.sql import func

from app.models.base import Base


class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    embedding = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
