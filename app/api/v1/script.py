from typing import List

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.script_repository import ScriptRepository
from app.schemas.script import ScriptCreate, ScriptResponse
from app.services.embedding_service import embedding_service

router = APIRouter(prefix="/script", tags=["script"])


@router.post("", response_model=ScriptResponse, status_code=201)
async def create_script(
    script_data: ScriptCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    연습용 새 문장을 등록합니다.
    """
    repo = ScriptRepository(db)

    # 스크립트에 대한 임베딩 생성
    embedding_vector = await embedding_service.generate_embedding(script_data.text)
    embedding_bytes = embedding_vector.tobytes()

    # 임베딩과 함께 스크립트 생성
    script = await repo.create(text=script_data.text, embedding=embedding_bytes)

    # 새 스크립트로 FAISS 인덱스 재구축
    await rebuild_faiss_index(db)

    return script


@router.get("", response_model=List[ScriptResponse])
async def get_scripts(
    db: AsyncSession = Depends(get_db),
):
    """
    등록된 모든 스크립트를 가져옵니다.
    """
    repo = ScriptRepository(db)
    scripts = await repo.get_all()
    return scripts


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    ID로 특정 스크립트를 가져옵니다.
    """
    repo = ScriptRepository(db)
    script = await repo.get_by_id(script_id)

    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    return script


async def rebuild_faiss_index(db: AsyncSession):
    """
    임베딩이 있는 모든 스크립트로부터 FAISS 인덱스를 재구축합니다.
    """
    repo = ScriptRepository(db)
    scripts = await repo.get_all_with_embeddings()

    if not scripts:
        return

    embeddings = []
    script_ids = []

    for script in scripts:
        if script.embedding:
            embedding_array = np.frombuffer(script.embedding, dtype=np.float32)
            embeddings.append(embedding_array)
            script_ids.append(script.id)

    if embeddings:
        embedding_service.build_index(embeddings, script_ids)
        embedding_service.save_index()
