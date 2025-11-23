from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.script_repository import ScriptRepository
from app.schemas.feedback import SubmitResponse
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/submit", tags=["submit"])


@router.post("", response_model=SubmitResponse)
async def submit_audio(
    script_id: int = Form(...),
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    특정 스크립트에 대한 오디오를 제출하고 평가 피드백을 받습니다.

    - **script_id**: 평가할 스크립트 ID
    - **audio**: 오디오 파일 (WAV, MP3 등)

    반환:
    - STT로부터 인식된 텍스트
    - 정확도 점수
    - 누락된 단어
    - 상세한 피드백
    - 유사 스크립트 추천
    """
    script_repo = ScriptRepository(db)
    feedback_repo = FeedbackRepository(db)
    feedback_service = FeedbackService(script_repo, feedback_repo)

    try:
        result = await feedback_service.process_submission(script_id, audio)
        return SubmitResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")
