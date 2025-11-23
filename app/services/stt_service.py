import whisper

from app.core.config import settings


class STTService:
    def __init__(self):
        self.model = None

    async def load_model(self):
        """Whisper 모델을 지연 로딩합니다."""
        if self.model is None:
            self.model = whisper.load_model(
                settings.whisper_model, download_root=settings.whisper_cache_dir
            )

    async def transcribe(self, audio_path: str) -> str:
        """
        Whisper를 사용하여 오디오 파일을 텍스트로 변환합니다.

        Args:
            audio_path: 오디오 파일 경로

        Returns:
            변환된 텍스트
        """
        await self.load_model()

        result = self.model.transcribe(audio_path, language="en")
        return result["text"].strip()


stt_service = STTService()
