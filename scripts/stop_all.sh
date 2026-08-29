#!/usr/bin/env bash
# start_all.sh로 실행한 SOCAMACA 프로세스를 정상 종료합니다.

set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${SOCAMACA_ENV_FILE:-$PROJECT_ROOT/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "설정 파일이 없습니다: $ENV_FILE"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${ROBOT_HOST:?ROBOT_HOST를 .env에 설정하세요}"
: "${ROBOT_USER:?ROBOT_USER를 .env에 설정하세요}"

echo "=== 로컬 프로세스 종료 ==="
pkill -SIGINT -f "phone_cam_detector|bbox4|mission_manager|tracking/lib/tracking|explore_lite/lib|rosbridge_websocket|iriunwebcam|slam_toolbox|nav2_|lifecycle_manager|node_modules/.bin/vite" || true

echo "=== 로봇 아두이노 슈터 종료 ==="
ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 \
  "$ROBOT_USER@$ROBOT_HOST" "pkill -SIGINT -f arduino_shooter_node || true"

echo "=== 완료 ==="
