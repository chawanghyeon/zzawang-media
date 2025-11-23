from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback


class FeedbackRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        script_id: int,
        audio_path: str,
        recognized_text: str,
        accuracy_score: float,
        missing_words: Optional[str] = None,
        feedback_text: Optional[str] = None,
    ) -> Feedback:
        feedback = Feedback(
            script_id=script_id,
            audio_path=audio_path,
            recognized_text=recognized_text,
            accuracy_score=accuracy_score,
            missing_words=missing_words,
            feedback_text=feedback_text,
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_by_id(self, feedback_id: int) -> Optional[Feedback]:
        result = await self.db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Feedback]:
        result = await self.db.execute(select(Feedback))
        return list(result.scalars().all())

    async def get_average_score(self) -> float:
        result = await self.db.execute(select(func.avg(Feedback.accuracy_score)))
        avg = result.scalar()
        return float(avg) if avg else 0.0

    async def get_total_submissions(self) -> int:
        result = await self.db.execute(select(func.count(Feedback.id)))
        return result.scalar() or 0
