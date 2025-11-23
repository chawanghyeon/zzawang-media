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
| 음성 제출       | 특정 문장에 대한 사용자 음성을 업로드 |
| STT 처리        | Whisper(OpenAI) 또는 Vosk 엔진으로 음성 인식 |
| 발음 평가       | Levenshtein 거리 기반 점수 및 누락 단어 추출 |
| 피드백 조회     | 사용자가 제출한 결과에 대한 상세 피드백 제공 |

### 관리자 기능

| 기능            | 설명 |
|-----------------|------|
| 통계 조회       | 전체 평균 점수, 자주 틀리는 단어, 사용자별 평균 등 시각화용 데이터 제공 |

## 3. 기술 스택

- Python 3.12
- FastAPI (비동기 API 서버)
- SQLite (RDBMS)
- SQLAlchemy (ORM)
- Whisper v3
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

```bash
# 1. 레포지토리 클론
git clone https://github.com/chawanghyeon/zzawang-media.git
cd zzawang-media

# 2. Docker 실행
docker-compose up --build

# 3. 접속 확인
http://localhost:8000/docs
````

## 8. 향후 개선 방향

* 발음 평가에 억양, 말 속도 분석 추가
* 사용자 인증 및 이력 분석 기능 강화
* 관리자용 대시보드 UI 연동
* 비동기 STT 처리 및 대기열 분리
