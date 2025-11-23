import difflib
import re
from typing import List, Tuple


class PronunciationEvaluator:
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        구두점과 특수문자를 제거하고 텍스트를 정리합니다.
        """
        # 구두점 제거
        text = re.sub(r"[^\w\s]", "", text)
        # 연속된 공백을 하나로
        text = re.sub(r"\s+", " ", text)
        return text.strip().lower()

    @staticmethod
    def calculate_accuracy(original: str, recognized: str) -> float:
        """
        Levenshtein 기반 유사도를 사용하여 발음 정확도를 계산합니다.
        0.0에서 100.0 사이의 점수를 반환합니다.
        """
        original_clean = PronunciationEvaluator._clean_text(original)
        recognized_clean = PronunciationEvaluator._clean_text(recognized)
        similarity = difflib.SequenceMatcher(None, original_clean, recognized_clean)
        return round(similarity.ratio() * 100, 2)

    @staticmethod
    def find_missing_words(original: str, recognized: str) -> List[str]:
        """
        원본 텍스트에는 있지만 인식된 텍스트에서 누락된 단어를 찾습니다.
        """
        original_clean = PronunciationEvaluator._clean_text(original)
        recognized_clean = PronunciationEvaluator._clean_text(recognized)

        original_words = set(original_clean.split())
        recognized_words = set(recognized_clean.split())
        missing = original_words - recognized_words
        return sorted(list(missing))

    @staticmethod
    def generate_feedback(
        accuracy_score: float, missing_words: List[str], original: str, recognized: str
    ) -> str:
        """
        정확도 점수와 누락된 단어를 기반으로 상세한 피드백을 생성합니다.
        """
        feedback_parts = []

        if accuracy_score >= 90:
            feedback_parts.append("훌륭합니다! 발음이 매우 정확합니다.")
        elif accuracy_score >= 70:
            feedback_parts.append("좋습니다! 조금만 더 연습하면 완벽해질 것 같아요.")
        elif accuracy_score >= 50:
            feedback_parts.append("괜찮습니다. 더 연습이 필요합니다.")
        else:
            feedback_parts.append("많은 연습이 필요합니다. 천천히 따라 읽어보세요.")

        if missing_words:
            feedback_parts.append(
                f"누락된 단어: {', '.join(missing_words)}. 이 단어들을 신경써서 발음해보세요."
            )

        # 추가 구체적인 피드백
        if len(recognized.split()) < len(original.split()):
            feedback_parts.append("문장을 끝까지 읽어주세요.")
        elif len(recognized.split()) > len(original.split()):
            feedback_parts.append("불필요한 단어가 추가되었습니다.")

        return " ".join(feedback_parts)

    @staticmethod
    def evaluate(original: str, recognized: str) -> Tuple[float, List[str], str]:
        """
        전체 평가를 수행합니다: (정확도 점수, 누락된 단어, 피드백 텍스트)를 반환합니다.
        """
        accuracy = PronunciationEvaluator.calculate_accuracy(original, recognized)
        missing = PronunciationEvaluator.find_missing_words(original, recognized)
        feedback = PronunciationEvaluator.generate_feedback(
            accuracy, missing, original, recognized
        )
        return accuracy, missing, feedback
