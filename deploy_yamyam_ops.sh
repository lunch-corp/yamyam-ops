#!/bin/bash

# yamyam-ops 디렉토리를 원격 서버에 복사하는 스크립트

# 현재 스크립트가 있는 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# .env 파일 로드 (존재하는 경우)
if [ -f "$SCRIPT_DIR/.env" ]; then
    set -a  # 자동으로 export
    source "$SCRIPT_DIR/.env"
    set +a  # export 해제
    echo "✅ .env 파일을 로드했습니다."
else
    echo "⚠️  .env 파일을 찾을 수 없습니다. 환경 변수를 직접 설정해주세요."
fi

# SSH 설정 (환경 변수에서 읽기)
SSH_KEY="${SSH_KEY}"
SSH_PORT="${REMOTE_JSON_PORT}"
SSH_USER="${REMOTE_JSON_USER}"
SSH_HOST="${REMOTE_JSON_HOST}"
REMOTE_PATH="${REMOTE_PATH}"

# 필수 환경 변수 검증
if [ -z "$SSH_KEY" ] || [ -z "$SSH_USER" ] || [ -z "$SSH_HOST" ] || [ -z "$REMOTE_PATH" ]; then
    echo "❌ 오류: 필수 환경 변수가 설정되지 않았습니다."
    echo "다음 환경 변수를 설정해주세요:"
    echo "  - SSH_KEY"
    echo "  - REMOTE_JSON_USER"
    echo "  - REMOTE_JSON_HOST"
    echo "  - REMOTE_PATH"
    echo "  - REMOTE_JSON_PORT (선택, SSH 포트가 기본값이 아닌 경우)"
    exit 1
fi

# SSH 포트 옵션 구성 (포트가 설정된 경우에만)
if [ -n "$SSH_PORT" ]; then
    SSH_PORT_OPT="-p $SSH_PORT"
    SSH_RSYNC_OPT="-p $SSH_PORT"
else
    SSH_PORT_OPT=""
    SSH_RSYNC_OPT=""
fi

# 소스 디렉토리 (yamyam-ops 디렉토리 자체)
SOURCE_DIR="$SCRIPT_DIR"

echo "📦 yamyam-ops 디렉토리를 원격 서버에 복사합니다..."
echo "소스: $SOURCE_DIR"
echo "대상: $SSH_USER@$SSH_HOST:$REMOTE_PATH/yamyam-ops"

# rsync를 사용하여 디렉토리 복사
RSYNC_EXIT_CODE=0
if [ -n "$SSH_RSYNC_OPT" ]; then
    rsync -avz \
        -e "ssh -i $SSH_KEY $SSH_RSYNC_OPT" \
        --exclude='.git' \
        --exclude='.env' \
        --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        "$SOURCE_DIR/" \
        "$SSH_USER@$SSH_HOST:$REMOTE_PATH/yamyam-ops/" || RSYNC_EXIT_CODE=$?
else
    rsync -avz \
        -e "ssh -i $SSH_KEY" \
        --exclude='.git' \
        --exclude='.env' \
        --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        "$SOURCE_DIR/" \
        "$SSH_USER@$SSH_HOST:$REMOTE_PATH/yamyam-ops/" || RSYNC_EXIT_CODE=$?
fi

# rsync exit code 처리
# 0: 성공
# 23: 부분 전송 (타임스탬프 설정 실패 등, 파일 전송은 성공)
# 기타: 실제 오류
if [ $RSYNC_EXIT_CODE -eq 0 ]; then
    echo "✅ 성공적으로 복사되었습니다!"
elif [ $RSYNC_EXIT_CODE -eq 23 ]; then
    echo "⚠️  복사 완료 (일부 타임스탬프 설정 실패, 파일 전송은 성공)"
else
    echo "❌ 복사 중 오류가 발생했습니다. (exit code: $RSYNC_EXIT_CODE)"
    exit 1
fi

# 원격 서버에서 docker compose 재시작
echo ""
echo "🐳 원격 서버에서 docker compose를 재시작합니다..."

# 이미지 빌드 여부 확인
echo ""
echo "이미지 빌드가 필요하신가요?"
echo "  - 소스 코드나 Dockerfile이 변경된 경우: Y"
echo "  - 환경 변수나 설정만 변경된 경우: N"
read -p "이미지 빌드 진행? (Y/n): " BUILD_IMAGE

# 기본값은 Y (빌드)
if [[ -z "$BUILD_IMAGE" ]] || [[ "$BUILD_IMAGE" =~ ^[Yy]$ ]]; then
    BUILD_FLAG="--build"
    echo "✅ 이미지 빌드를 포함하여 재시작합니다."
else
    BUILD_FLAG=""
    echo "ℹ️  기존 이미지를 사용하여 재시작합니다."
fi

# 원격 경로 처리 (~를 $HOME으로 확장)
if [[ "$REMOTE_PATH" == "~" ]] || [[ "$REMOTE_PATH" == "~/"* ]]; then
    # ~를 $HOME으로 변환 (SSH 명령 내에서 확장)
    REMOTE_YAMYAM_OPS_PATH="\$HOME/yamyam-ops"
else
    REMOTE_YAMYAM_OPS_PATH="$REMOTE_PATH/yamyam-ops"
fi

# SSH 명령 구성
if [ -n "$SSH_PORT_OPT" ]; then
    ssh -i "$SSH_KEY" $SSH_PORT_OPT "$SSH_USER@$SSH_HOST" << EOF
    cd "$REMOTE_YAMYAM_OPS_PATH" || exit 1
    echo "현재 디렉토리: \$(pwd)"
    echo "docker compose down 실행 중..."
    docker compose down
    
    if [ -n "$BUILD_FLAG" ]; then
        echo "docker compose up $BUILD_FLAG -d 실행 중..."
        docker compose up $BUILD_FLAG -d
    else
        echo "docker compose up -d 실행 중..."
        docker compose up -d
    fi
EOF
else
    ssh -i "$SSH_KEY" "$SSH_USER@$SSH_HOST" << EOF
    cd "$REMOTE_YAMYAM_OPS_PATH" || exit 1
    echo "현재 디렉토리: \$(pwd)"
    echo "docker compose down 실행 중..."
    docker compose down
    
    if [ -n "$BUILD_FLAG" ]; then
        echo "docker compose up $BUILD_FLAG -d 실행 중..."
        docker compose up $BUILD_FLAG -d
    else
        echo "docker compose up -d 실행 중..."
        docker compose up -d
    fi
EOF
fi

if [ $? -eq 0 ]; then
    echo "✅ docker compose 재시작이 완료되었습니다!"
else
    echo "❌ docker compose 재시작 중 오류가 발생했습니다."
    exit 1
fi
