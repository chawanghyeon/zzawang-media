from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.database import init_db
from app.services.embedding_service import embedding_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    시작 및 종료 이벤트를 위한 생명주기 이벤트 핸들러입니다.
    """
    # 시작
    await init_db()

    # FAISS 인덱스가 있으면 로드
    embedding_service.load_index()

    yield

    # 종료 (필요시)
    pass


app = FastAPI(
    title="Zzawang Media API",
    description="음성 학습 평가 서버",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 라우터 포함
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """데모 페이지로 리다이렉트"""
    return FileResponse(str(static_path / "index.html"))


@app.get("/demo")
async def demo():
    """데모 페이지"""
    return FileResponse(str(static_path / "index.html"))


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
