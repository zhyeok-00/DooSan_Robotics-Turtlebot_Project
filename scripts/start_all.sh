#!/usr/bin/env bash
# SOCAMACA 전체 파이프라인 실행. 로컬 비밀정보는 프로젝트 루트 .env에서 읽습니다.

set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${SOCAMACA_ENV_FILE:-$PROJECT_ROOT/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "설정 파일이 없습니다: $ENV_FILE"
  echo ".env.example을 .env로 복사한 뒤 실제 환경 값을 입력하세요."
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${ROS_SETUP:?ROS_SETUP을 .env에 설정하세요}"
: "${TB4_SETUP:?TB4_SETUP을 .env에 설정하세요}"
: "${ROBOT_HOST:?ROBOT_HOST를 .env에 설정하세요}"
: "${ROBOT_USER:?ROBOT_USER를 .env에 설정하세요}"
: "${ROBOT_WORKSPACE_SETUP:?ROBOT_WORKSPACE_SETUP을 .env에 설정하세요}"

ROBOT_NAMESPACE="${ROBOT_NAMESPACE:-robot4}"
PATROL_SETUP="${PATROL_SETUP:-$PROJECT_ROOT/ros2/perception_ws/install/setup.bash}"
AMR_SETUP="${AMR_SETUP:-$PROJECT_ROOT/ros2/amr_ws/install/setup.bash}"
UI_DIR="${UI_DIR:-$PROJECT_ROOT/web/frontend-team-pc}"
LOGDIR="${LOGDIR:-/tmp/socamaca_logs}"
ROBOT_ROS_SETUP="${ROBOT_ROS_SETUP:-/opt/ros/humble/setup.bash}"
ROBOT_LOG_PATH="${ROBOT_LOG_PATH:-/tmp/arduino_shooter.log}"
ARDUINO_PORT_GLOB="${ARDUINO_PORT_GLOB:-/dev/ttyACM*}"

for required_file in "$ROS_SETUP" "$TB4_SETUP" "$PATROL_SETUP" "$AMR_SETUP"; do
  if [[ ! -f "$required_file" ]]; then
    echo "필수 setup 파일이 없습니다: $required_file"
    exit 1
  fi
done

mkdir -p "$LOGDIR"

echo "[1/10] SLAM"
( source "$ROS_SETUP" && source "$TB4_SETUP" && \
  nohup ros2 launch turtlebot4_navigation slam.launch.py namespace:="$ROBOT_NAMESPACE" \
    > "$LOGDIR/slam.log" 2>&1 & disown )
sleep 6

echo "[2/10] Nav2"
( source "$ROS_SETUP" && source "$TB4_SETUP" && \
  nohup ros2 launch turtlebot4_navigation nav2.launch.py namespace:="$ROBOT_NAMESPACE" \
    > "$LOGDIR/nav2.log" 2>&1 & disown )
echo "  -> Nav2 활성화 대기 중 (약 20초)..."
sleep 20

echo "[3/10] Iriun Webcam"
nohup iriunwebcam > "$LOGDIR/iriun.log" 2>&1 &
disown

echo "[4/10] phone_cam_detector"
( source "$ROS_SETUP" && source "$PATROL_SETUP" && \
  nohup ros2 run yolo_detector phone_cam_detector --ros-args -r __ns:="/$ROBOT_NAMESPACE" \
    > "$LOGDIR/phone_cam_detector.log" 2>&1 & disown )

echo "[5/10] mission_manager"
( source "$ROS_SETUP" && source "$PATROL_SETUP" && source "$AMR_SETUP" && \
  nohup ros2 run tracking mission_manager --ros-args -r __ns:="/$ROBOT_NAMESPACE" \
    > "$LOGDIR/mission_manager.log" 2>&1 & disown )

echo "[6/10] azimuth"
( source "$ROS_SETUP" && source "$AMR_SETUP" && \
  nohup ros2 run tracking azimuth --ros-args -r __ns:="/$ROBOT_NAMESPACE" \
    > "$LOGDIR/azimuth.log" 2>&1 & disown )

echo "[7/10] target"
( source "$ROS_SETUP" && source "$AMR_SETUP" && \
  nohup ros2 run tracking target --ros-args -r __ns:="/$ROBOT_NAMESPACE" \
    > "$LOGDIR/target.log" 2>&1 & disown )

echo "[8/10] rosbridge"
( source "$ROS_SETUP" && source "$PATROL_SETUP" && \
  nohup ros2 launch rosbridge_server rosbridge_websocket_launch.xml \
    > "$LOGDIR/rosbridge.log" 2>&1 & disown )

echo "[9/10] frontend"
( cd "$UI_DIR" && nohup npm run dev > "$LOGDIR/vite.log" 2>&1 & disown )

echo "[10/10] 아두이노 슈터 (SSH 키 인증)"
ARDUINO_PORT="$(ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 \
  "$ROBOT_USER@$ROBOT_HOST" "ls $ARDUINO_PORT_GLOB 2>/dev/null | head -1")"
if [[ -z "$ARDUINO_PORT" ]]; then
  echo "  -> 아두이노 포트를 못 찾았습니다. 슈터 노드는 건너뜁니다."
else
  ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 \
    "$ROBOT_USER@$ROBOT_HOST" "
      export ROS_DOMAIN_ID='${ROS_DOMAIN_ID:-5}'
      export ROS_DISCOVERY_SERVER='${ROS_DISCOVERY_SERVER:-;;;;127.0.0.1:11811;}'
      export ROS_SUPER_CLIENT='${ROS_SUPER_CLIENT:-False}'
      source '$ROBOT_ROS_SETUP'
      source '$ROBOT_WORKSPACE_SETUP'
      nohup ros2 run turtlebot4_beep arduino_shooter_node --ros-args \
        -r __ns:='/$ROBOT_NAMESPACE' -p port:='$ARDUINO_PORT' \
        > '$ROBOT_LOG_PATH' 2>&1 < /dev/null &
    "
fi

echo "완료. 로그: $LOGDIR"
echo "브라우저: http://localhost:5173"
