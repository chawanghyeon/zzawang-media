from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.script import Script


class ScriptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, text: str, embedding: Optional[bytes] = None) -> Script:
        script = Script(text=text, embedding=embedding)
        self.db.add(script)
        await self.db.commit()
        await self.db.refresh(script)
        return script

    async def update_embedding(
        self, script_id: int, embedding: bytes
    ) -> Optional[Script]:
        script = await self.get_by_id(script_id)
        if script:
            script.embedding = embedding
            await self.db.commit()
            await self.db.refresh(script)
        return script

    async def get_all(self) -> List[Script]:
        result = await self.db.execute(select(Script))
        return list(result.scalars().all())

    async def get_by_id(self, script_id: int) -> Optional[Script]:
        result = await self.db.execute(select(Script).where(Script.id == script_id))
        return result.scalar_one_or_none()

    async def get_all_with_embeddings(self) -> List[Script]:
        result = await self.db.execute(
            select(Script).where(Script.embedding.isnot(None))
        )
        return list(result.scalars().all())
