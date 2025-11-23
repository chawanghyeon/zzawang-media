# zzawang-media

사용자의 음성 발화를 받아 실시간으로 음성 인식(STT) 및 발음 평가를 수행하고, 이에 대한 피드백을 제공하는 Python 기반의 음성 학습 평가 서버입니다.  

## 1. 프로젝트 개요

- 사용자가 연습할 문장을 등록하고, 해당 문장을 따라 말한 음성 파일을 제출하면,
- 서버는 음성을 텍스트로 변환(STT)하고,
- 원본 문장과 비교하여 발음 정확도, 누락 단어, 종합 피드백을 계산해 반환합니다.
- 관리자는 전체 사용자들의 평균 점수 및 학습 통계를 확인할 수 있습니다.


## 2. 주요 기능

### 사용자 기능

| 기능            | 설명 |
|-----------------|------|
| 문장 등록       | 학습용 문장을 서버에 등록 |
| 문장 벡터 저장  | 등록된 문장에 대한 임베딩 벡터 생성 및 저장 |
| 음성 제출       | 특정 문장에 대한 사용자 음성을 업로드 |
| STT 처리        | Whisper 엔진으로 음성 인식 |
| 발음 평가       | Levenshtein 거리 기반 점수 및 누락 단어 추출 |
| 피드백 조회     | 사용자가 제출한 결과에 대한 상세 피드백 제공 |
| 비슷한 문장 추천 | 발음이 유사한 다른 문장 추천 |

### 관리자 기능

| 기능            | 설명 |
|-----------------|------|
| 통계 조회       | 전체 평균 점수, 자주 틀리는 단어, 사용자별 평균 등 시각화용 데이터 제공 |

## 3. 기술 스택

- Python 3.12
- FastAPI (비동기 API 서버)
- SQLite (RDBMS)
- Faiss (벡터 검색)
- SQLAlchemy (ORM)
- Whisper v3
- sentence-transformers/all-MiniLM-L6-v2
- Docker / Docker Compose
- Pydantic / Uvicorn
- difflib (Levenshtein 유사도)
- aiofiles (비동기 파일 처리)

## 4. 아키텍처 구성

```

사용자 → FastAPI 서버 → STT 엔진(Whisper)
↓
발음 평가 모듈
↓
DB 저장 및 피드백 반환

```

- 음성 업로드 시 서버는 파일을 저장하고 STT 처리 후 인식 결과를 DB에 저장
- 발음 평가 점수와 누락 단어를 산출하여 응답으로 반환
- 관리자 통계는 DB 집계를 통해 제공

## 5. 디렉토리 구조

```

speechlab/
├── app/
│   ├── api/                 # 엔드포인트 정의
│   ├── core/                # 설정 및 평가 알고리즘
│   ├── repositories/        # DB 접근 모듈
│   ├── models/              # SQLAlchemy 모델 정의
│   ├── schemas/             # Pydantic 스키마 정의
│   ├── services/            # STT 및 피드백 로직
│   └── main.py              # FastAPI 앱 실행부
├── Dockerfile               # API 서버 Docker 빌드 정의
├── docker-compose.yml       # API + DB 통합 실행 환경
├── requirements.txt         # 패키지 의존성 정의
└── README.md                # 프로젝트 설명

````

## 6. 주요 API 명세

| 메서드 | 경로               | 설명                          |
|--------|--------------------|-------------------------------|
| POST   | `/script`          | 문장 등록                    |
| GET    | `/script`          | 문장 리스트 조회             |
| POST   | `/submit`          | 음성 제출 및 평가 처리       |
| GET    | `/feedback/{id}`   | 피드백 결과 조회             |
| GET    | `/admin/dashboard` | 전체 통계 조회               |

## 7. 실행 방법

### Docker를 사용한 실행 (권장)

```bash
# 1. 레포지토리 클론
git clone https://github.com/chawanghyeon/zzawang-media.git
cd zzawang-media

# 2. 환경 변수 설정 (선택사항)
cp .env.example .env
# .env 파일을 수정하여 설정 변경 가능

# 3. Docker Compose로 실행
docker-compose up -d --build

# 4. 로그 확인
docker-compose logs -f

# 5. 서비스 중지
docker-compose down

# 6. 접속 확인
http://localhost:8000          # 데모 페이지
http://localhost:8000/docs     # API 문서
```

### 🎤 데모 페이지 사용하기

서버 실행 후 브라우저에서 `http://localhost:8000` 접속

1. **문장 등록**: 연습하고 싶은 문장을 입력하고 등록
2. **문장 선택**: 등록된 문장 중 하나를 클릭하여 선택
3. **음성 녹음**: "녹음 시작" 버튼을 눌러 문장을 읽고, "녹음 중지"로 종료
4. **평가 받기**: 녹음이 완료되면 "평가 받기" 버튼으로 결과 확인
5. **통계 확인**: "통계 불러오기"로 전체 통계 조회

```

### 로컬 개발 환경 실행

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env

# 4. 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. 접속 확인
http://localhost:8000/docs
```

### API 사용 예시

```bash
# 문장 등록
curl -X POST "http://localhost:8000/api/v1/script" \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕하세요, 반갑습니다."}'

# 음성 제출
curl -X POST "http://localhost:8000/api/v1/submit" \
  -F "script_id=1" \
  -F "audio=@audio.wav"

# 피드백 조회
curl "http://localhost:8000/api/v1/feedback/1"

# 관리자 대시보드
curl "http://localhost:8000/api/v1/admin/dashboard"
```

````

## 8. 향후 개선 방향

* 발음 평가에 억양, 말 속도 분석 추가
* 사용자 인증 및 이력 분석 기능 강화
* 관리자용 대시보드 UI 연동
* 비동기 STT 처리 및 대기열 분리
