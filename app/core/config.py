from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 데이터베이스
    database_url: str = "sqlite+aiosqlite:///./data/speechlab.db"

    # Whisper 설정
    whisper_model: str = "turbo"

    # 임베딩 설정
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 2048

    # 파일 업로드
    upload_dir: str = "./data/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # FAISS 설정
    faiss_index_path: str = "./data/faiss_index.bin"
    similar_scripts_count: int = 3

    # 캐시 설정
    whisper_cache_dir: str = "./data/cache/whisper"
    huggingface_cache_dir: str = "./data/cache/huggingface"


settings = Settings()
