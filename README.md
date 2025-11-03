# 🍜 yamyam-ops - 음식 추천 API 서버

## 프로젝트 개요

yamyam-ops는 Firebase Authentication과 PostgreSQL을 활용한 음식 추천 시스템의 백엔드 API 서버입니다. 사용자 기반 협업 필터링과 아이템 임베딩을 통한 개인화된 음식 추천을 제공합니다.

## 아키텍처

```
[Frontend App]
(Streamlit 등)
           ↓
      [Internet]
           ↓
   [Docker Compose]
           ↓
    [FastAPI Backend]
           ↓
  [PostgreSQL] ←→ [Redis Cache]
           ↑
    [Firebase Auth]
```

### 주요 특징
- **Firebase Authentication**: SNS/이메일 로그인 지원
- **PostgreSQL**: 사용자 데이터 및 비즈니스 로직 관리
- **Redis**: 세션 캐시 및 임시 데이터 저장
- **FAISS**: 벡터 유사도 검색 (User-to-User, Item-to-Item)
- **Docker Compose**: 개발/배포 환경 통합 관리
- **FastAPI**: 고성능 비동기 API 서버

## 주요 구성 요소

- **FastAPI**: REST API 및 비즈니스 로직
- **PostgreSQL**: 사용자, 리뷰, 음식점 데이터 저장
- **Redis**: 세션 캐시, 임시 데이터
- **Firebase Auth**: 사용자 인증 및 관리
- **FAISS**: 벡터 데이터베이스 및 유사도 검색
- **Docker Compose**: 컨테이너 오케스트레이션

## 프로젝트 구조

```
yamyam-ops/
├── docker-compose.yml           # Docker Compose 설정
├── env.example                  # 환경 변수 예시
├── README.md
│
├── backend/                     # FastAPI 백엔드 소스
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── firebase-key.json        # Firebase 서비스 계정 키
│   └── app/
│       ├── main.py              # FastAPI 엔트리포인트
│       ├── core/                # 핵심 설정
│       │   ├── config.py        # 설정 관리
│       │   ├── db.py            # 데이터베이스 연결
│       │   ├── dependencies.py  # 의존성 주입
│       │   └── firebase_auth.py # Firebase 인증
│       ├── api/v1/              # API 엔드포인트
│       │   ├── auth.py          # 인증 API
│       │   ├── items.py         # 음식점 관리 API
│       │   ├── kakao_diners.py  # 카카오 음식점 API
│       │   ├── kakao_reviews.py # 카카오 리뷰 API
│       │   ├── kakao_reviewers.py # 카카오 리뷰어 API
│       │   ├── reviews.py       # 리뷰 관리 API
│       │   ├── upload.py        # 파일 업로드 API
│       │   ├── users.py         # 사용자 관리 API
│       │   └── vectors.py       # 벡터 검색 API
│       ├── database/            # 데이터베이스 쿼리
│       │   ├── base_queries.py
│       │   ├── item_queries.py
│       │   ├── kakao_queries.py
│       │   ├── review_queries.py
│       │   └── user_queries.py
│       ├── models/              # SQLAlchemy 모델
│       │   ├── base.py
│       │   ├── embedding.py     # 임베딩 벡터 모델
│       │   ├── item.py
│       │   ├── kakao_diner.py
│       │   ├── kakao_review.py
│       │   ├── kakao_reviewer.py
│       │   ├── preference.py
│       │   ├── review.py
│       │   └── user.py
│       ├── processors/          # 데이터 처리
│       │   ├── file_processor.py
│       │   └── kakao_data_processor.py
│       ├── schemas/             # Pydantic 스키마
│       │   ├── item_kakao_mapping.py
│       │   ├── item.py
│       │   ├── kakao_diner.py
│       │   ├── kakao_review.py
│       │   ├── kakao_reviewer.py
│       │   ├── review.py
│       │   ├── token.py
│       │   ├── user.py
│       │   └── vector.py        # 벡터 검색 스키마
│       ├── services/            # 비즈니스 로직
│       │   ├── base_service.py
│       │   ├── kakao_diner_service.py
│       │   ├── kakao_review_service.py
│       │   ├── kakao_reviewer_service.py
│       │   ├── token_service.py
│       │   ├── upload_service.py
│       │   ├── user_service.py
│       │   └── vector_search_service.py  # FAISS 벡터 검색
│       └── utils/               # 유틸리티
│           ├── jwt_utils.py
│           └── ulid_utils.py
│
├── postgres/
│   └── init/
│       └── 01_init.sql          # DB 초기화 스크립트
│
├── nginx/
│   └── conf/
│       └── default.conf         # Nginx 설정 (CORS 포함)
│
├── docs/                        # 문서
│   ├── STREAMLIT_INTEGRATION.md
│   ├── UPLOAD_API_GUIDE.md
│   └── todo_list.md
│
└── scripts/                     # 스크립트
    ├── upload_seoul_data.py
    └── test_upload.py
```
## 배포 흐름 

```
[개발자] → [GitHub] → [GitHub Actions] → [Docker Hub] → [프로덕션 서버]
    ↓           ↓            ↓              ↓              ↓
  코드 작성    코드 푸시    자동 빌드      이미지 저장    배포 스크립트
```

## 시작하기

### 1. 환경 변수 설정

```bash
# 환경 변수 파일 복사
cp env.example .env

# .env 파일 편집 (필요한 값 설정)
# - DATABASE_URL: PostgreSQL 연결 정보
# - REDIS_URL: Redis 연결 정보
# - SECRET_KEY: JWT 시크릿 키
# - Firebase 설정: 인증용 서비스 계정 키
```

### 2. Docker Compose로 서비스 시작

```bash
# 모든 서비스 빌드 및 시작
docker-compose up --build

# 백그라운드에서 실행
docker-compose up -d --build

# 특정 서비스만 시작
docker-compose up backend postgres redis

# 서비스 재시작
docker-compose restart backend

# 로그 확인
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 3. 서비스 접근

- **FastAPI API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. 서비스 관리

```bash
# 서비스 중지
docker-compose down

# 볼륨 포함 완전 삭제 (데이터 삭제)
docker-compose down -v

# 특정 서비스만 중지
docker-compose stop backend

# 서비스 상태 확인
docker-compose ps

# 컨테이너 내부 접속
docker-compose exec backend bash
docker-compose exec postgres psql -U yamyam -d yamyamdb
```

## 벡터 검색 (FAISS) 사용법

### 1. 임베딩 벡터 저장

```bash
curl -X POST "http://localhost:8000/vectors/embeddings" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "user",
    "entity_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "embedding_type": "default",
    "dimension": 128,
    "vector": [0.1, 0.2, 0.3, ...]  # 128차원 벡터
  }'
```

### 2. User-to-User 유사도 검색

```bash
# 특정 사용자와 유사한 사용자 찾기
curl -X POST "http://localhost:8000/vectors/similarity/users/USER_ID?k=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Item-to-Item 유사도 검색

```bash
# 특정 아이템과 유사한 아이템 찾기
curl -X POST "http://localhost:8000/vectors/similarity/items/ITEM_ID?k=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 인덱스 관리

```bash
# 인덱스 재구축
curl -X POST "http://localhost:8000/vectors/indexes/user/rebuild" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 인덱스 정보 조회
curl -X GET "http://localhost:8000/vectors/indexes/user/info"
```

## 벡터 검색 아키텍처

```
[ML Model] → [Embedding Vector] → [PostgreSQL]
                                      ↓
                                   [FAISS Index]
                                      ↓
                           [Vector Search Service]
                                      ↓
                              [FastAPI Endpoint]
                                      ↓
                                  [Client]
```

### 주요 특징

- **Hybrid Search**: 벡터 유사도와 메타데이터 필터링 결합
- **Fast Index**: FAISS IndexFlatL2를 사용한 L2 거리 기반 정확 검색
- **Persistent**: 인덱스 자동 저장/로드
- **Batch Processing**: 벡터 일괄 추가 및 인덱스 재구축 지원

## API 엔드포인트

### 벡터 검색 API (`/vectors`)

- `POST /vectors/embeddings`: 임베딩 벡터 저장
- `POST /vectors/similarity/search`: 일반 유사도 검색
- `POST /vectors/similarity/users/{user_id}`: 사용자 유사도 검색
- `POST /vectors/similarity/items/{item_id}`: 아이템 유사도 검색
- `POST /vectors/indexes/{entity_type}/rebuild`: 인덱스 재구축
- `GET /vectors/indexes/{entity_type}/info`: 인덱스 정보 조회
