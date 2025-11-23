import pickle
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

from app.core.config import settings


class EmbeddingService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.index = None
        self.script_ids = []

    async def load_model(self):
        """임베딩 모델을 지연 로딩합니다."""
        if self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.embedding_model, cache_dir=settings.huggingface_cache_dir
            )
            self.model = AutoModel.from_pretrained(
                settings.embedding_model, cache_dir=settings.huggingface_cache_dir
            )
            self.model.eval()

    async def generate_embedding(self, text: str) -> np.ndarray:
        """
        주어진 텍스트에 대한 임베딩 벡터를 생성합니다.

        Args:
            text: 입력 텍스트

        Returns:
            numpy 배열로 된 임베딩 벡터
        """
        await self.load_model()

        inputs = self.tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            # 평균 풀링 사용
            embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings.squeeze().numpy()

    def build_index(self, embeddings: List[np.ndarray], script_ids: List[int]):
        """
        임베딩으로부터 FAISS 인덱스를 구축합니다.

        Args:
            embeddings: 임베딩 벡터 리스트
            script_ids: 대응하는 스크립트 ID들
        """
        if not embeddings:
            return

        dimension = embeddings[0].shape[0]
        self.index = faiss.IndexFlatL2(dimension)

        embeddings_matrix = np.array(embeddings).astype("float32")
        self.index.add(embeddings_matrix)
        self.script_ids = script_ids

    def save_index(self):
        """FAISS 인덱스를 디스크에 저장합니다."""
        if self.index is None:
            return

        index_path = Path(settings.faiss_index_path)
        faiss.write_index(self.index, str(index_path))

        # 스크립트 ID 매핑 저장
        ids_path = index_path.with_suffix(".pkl")
        with open(ids_path, "wb") as f:
            pickle.dump(self.script_ids, f)

    def load_index(self):
        """디스크로부터 FAISS 인덱스를 로드합니다."""
        index_path = Path(settings.faiss_index_path)
        if not index_path.exists():
            return False

        self.index = faiss.read_index(str(index_path))

        # 스크립트 ID 매핑 로드
        ids_path = index_path.with_suffix(".pkl")
        if ids_path.exists():
            with open(ids_path, "rb") as f:
                self.script_ids = pickle.load(f)

        return True

    async def find_similar(
        self, text: str, top_k: int = None
    ) -> List[Tuple[int, float]]:
        """
        FAISS를 사용하여 유사한 스크립트를 찾습니다.

        Args:
            text: 쿼리 텍스트
            top_k: 반환할 유사 항목 개수

        Returns:
            (script_id, similarity_score) 튜플 리스트
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        if top_k is None:
            top_k = settings.similar_scripts_count

        query_embedding = await self.generate_embedding(text)
        query_embedding = query_embedding.reshape(1, -1).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k + 1)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.script_ids):
                script_id = self.script_ids[idx]
                # L2 거리를 유사도 점수로 변환 (0-100)
                similarity = max(0, 100 - float(distance))
                results.append((script_id, round(similarity, 2)))

        return results


embedding_service = EmbeddingService()
