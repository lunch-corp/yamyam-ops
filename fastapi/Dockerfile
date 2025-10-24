FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치
RUN pip install uv

# Python 의존성 설치 (uv 사용)
COPY pyproject.toml .
RUN uv pip install --system -e .

# 애플리케이션 코드 복사
COPY . .

# 비root 사용자 생성 및 권한 설정
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 포트 노출
EXPOSE 8000

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 서버 실행
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers $WORKERS"]






