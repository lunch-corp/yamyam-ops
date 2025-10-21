#!/bin/bash

# yamyam-ops 프로덕션 배포 스크립트
# GitHub + Docker Hub 워크플로우용

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 변수 확인
check_env_vars() {
    log_info "환경 변수 확인 중..."
    
    required_vars=(
        "DOCKERHUB_USERNAME"
        "DATABASE_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "POSTGRES_DB"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "다음 환경 변수가 설정되지 않았습니다:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
    
    log_success "환경 변수 확인 완료"
}

# Docker Hub 이미지 풀
pull_image() {
    local image_tag=${1:-latest}
    local image_name="${DOCKERHUB_USERNAME}/yamyam-ops:${image_tag}"
    
    log_info "Docker Hub에서 이미지 풀 중: $image_name"
    
    if docker pull "$image_name"; then
        log_success "이미지 풀 완료: $image_name"
    else
        log_error "이미지 풀 실패: $image_name"
        exit 1
    fi
}

# 기존 컨테이너 중지
stop_containers() {
    log_info "기존 컨테이너 중지 중..."
    
    if docker-compose -f docker-compose.prod.yml down; then
        log_success "기존 컨테이너 중지 완료"
    else
        log_warning "기존 컨테이너가 없거나 이미 중지됨"
    fi
}

# 새 컨테이너 시작
start_containers() {
    local image_tag=${1:-latest}
    
    log_info "새 컨테이너 시작 중 (태그: $image_tag)..."
    
    # 환경 변수 설정
    export IMAGE_TAG="$image_tag"
    
    if docker-compose -f docker-compose.prod.yml up -d; then
        log_success "컨테이너 시작 완료"
    else
        log_error "컨테이너 시작 실패"
        exit 1
    fi
}

# 헬스 체크
health_check() {
    local max_attempts=30
    local attempt=1
    
    log_info "헬스 체크 시작..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_success "헬스 체크 통과 (시도: $attempt/$max_attempts)"
            return 0
        fi
        
        log_info "헬스 체크 시도 중... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    log_error "헬스 체크 실패"
    return 1
}

# 로그 확인
show_logs() {
    log_info "최근 로그 확인 중..."
    docker-compose -f docker-compose.prod.yml logs --tail=50
}

# 메인 함수
main() {
    local image_tag=${1:-latest}
    
    log_info "yamyam-ops 프로덕션 배포 시작 (태그: $image_tag)"
    
    # 1. 환경 변수 확인
    check_env_vars
    
    # 2. Docker Hub에서 이미지 풀
    pull_image "$image_tag"
    
    # 3. 기존 컨테이너 중지
    stop_containers
    
    # 4. 새 컨테이너 시작
    start_containers "$image_tag"
    
    # 5. 헬스 체크
    if health_check; then
        log_success "배포 완료!"
        show_logs
    else
        log_error "배포 실패 - 헬스 체크 실패"
        show_logs
        exit 1
    fi
}

# 사용법 출력
usage() {
    echo "사용법: $0 [이미지_태그]"
    echo ""
    echo "예시:"
    echo "  $0                    # latest 태그로 배포"
    echo "  $0 v1.0.0            # v1.0.0 태그로 배포"
    echo "  $0 dev               # dev 태그로 배포"
    echo ""
    echo "환경 변수:"
    echo "  DOCKERHUB_USERNAME   Docker Hub 사용자명"
    echo "  DATABASE_URL         PostgreSQL 연결 URL"
    echo "  REDIS_URL           Redis 연결 URL"
    echo "  SECRET_KEY          JWT 시크릿 키"
    echo "  POSTGRES_USER       PostgreSQL 사용자명"
    echo "  POSTGRES_PASSWORD   PostgreSQL 비밀번호"
    echo "  POSTGRES_DB         PostgreSQL 데이터베이스명"
}

# 스크립트 실행
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    usage
    exit 0
fi

main "$@"
