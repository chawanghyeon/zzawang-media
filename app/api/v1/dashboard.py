from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """
    관리자 대시보드용 전체 통계를 가져옵니다.

    반환:
    - 총 제출 수
    - 평균 정확도 점수
    - 자주 틀리는 단어 상위 목록
    """
    repo = FeedbackRepository(db)

    # 기본 통계 가져오기
    total_submissions = await repo.get_total_submissions()
    average_score = await repo.get_average_score()

    # 누락된 단어 분석을 위해 모든 피드백 가져오기
    all_feedbacks = await repo.get_all()

    # 누락된 단어 카운트
    all_missing_words = []
    for feedback in all_feedbacks:
        if feedback.missing_words:
            words = [word.strip() for word in feedback.missing_words.split(",")]
            all_missing_words.extend(words)

    # 가장 많이 누락된 단어 상위 10개 가져오기
    word_counter = Counter(all_missing_words)
    top_mistakes = [word for word, count in word_counter.most_common(10)]

    return DashboardStats(
        total_submissions=total_submissions,
        average_score=average_score,
        top_mistakes=top_mistakes,
    )
