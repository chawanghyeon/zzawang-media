from pathlib import Path
from typing import List

import aiofiles
from fastapi import UploadFile

from app.core.config import settings
from app.core.evaluator import PronunciationEvaluator
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.script_repository import ScriptRepository
from app.schemas.feedback import SimilarScript
from app.services.embedding_service import embedding_service
from app.services.stt_service import stt_service


class FeedbackService:
    def __init__(
        self,
        script_repo: ScriptRepository,
        feedback_repo: FeedbackRepository,
    ):
        self.script_repo = script_repo
        self.feedback_repo = feedback_repo
        self.evaluator = PronunciationEvaluator()

    async def save_audio_file(self, file: UploadFile) -> str:
        """
        업로드된 오디오 파일을 디스크에 저장합니다.

        Args:
            file: 업로드된 오디오 파일

        Returns:
            저장된 파일 경로
        """
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / f"{file.filename}"

        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        return str(file_path)

    async def process_submission(self, script_id: int, audio_file: UploadFile) -> dict:
        """
        오디오 제출을 처리합니다: STT, 평가, 유사 스크립트 찾기.

        Args:
            script_id: 대상 스크립트 ID
            audio_file: 업로드된 오디오 파일

        Returns:
            피드백 데이터와 유사 스크립트가 담긴 딕셔너리
        """
        # 원본 스크립트 가져오기
        script = await self.script_repo.get_by_id(script_id)
        if not script:
            raise ValueError(f"Script with id {script_id} not found")

        # 오디오 파일 저장
        audio_path = await self.save_audio_file(audio_file)

        # STT 수행
        recognized_text = await stt_service.transcribe(audio_path)

        # 발음 평가
        accuracy_score, missing_words, feedback_text = self.evaluator.evaluate(
            script.text, recognized_text
        )

        # 피드백 레코드 생성
        feedback = await self.feedback_repo.create(
            script_id=script_id,
            audio_path=audio_path,
            recognized_text=recognized_text,
            accuracy_score=accuracy_score,
            missing_words=", ".join(missing_words) if missing_words else None,
            feedback_text=feedback_text,
        )

        # 인식된 텍스트를 기반으로 유사 스크립트 찾기
        similar_scripts = await self.get_similar_scripts(
            recognized_text, exclude_id=script_id
        )

        return {
            "feedback_id": feedback.id,
            "recognized_text": recognized_text,
            "accuracy_score": accuracy_score,
            "missing_words": ", ".join(missing_words) if missing_words else None,
            "feedback_text": feedback_text,
            "similar_scripts": similar_scripts,
        }

    async def get_similar_scripts(
        self, text: str, exclude_id: int = None
    ) -> List[SimilarScript]:
        """
        임베딩 검색을 사용하여 유사한 스크립트를 찾습니다.

        Args:
            text: 쿼리 텍스트
            exclude_id: 결과에서 제외할 스크립트 ID

        Returns:
            유사 스크립트 리스트
        """
        similar = await embedding_service.find_similar(text)

        results = []
        for script_id, similarity_score in similar:
            if exclude_id and script_id == exclude_id:
                continue

            script = await self.script_repo.get_by_id(script_id)
            if script:
                results.append(
                    SimilarScript(
                        id=script.id,
                        text=script.text,
                        similarity_score=similarity_score,
                    )
                )

        return results[: settings.similar_scripts_count]
