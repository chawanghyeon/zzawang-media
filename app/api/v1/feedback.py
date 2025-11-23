from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    특정 제출에 대한 상세 피드백을 가져옵니다.
    """
    repo = FeedbackRepository(db)
    feedback = await repo.get_by_id(feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return feedback
