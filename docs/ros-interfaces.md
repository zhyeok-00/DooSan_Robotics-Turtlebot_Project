# ROS 2 인터페이스 계약

아래 이름은 로봇 네임스페이스에 상대적입니다. 예를 들어 `robot_mode`는 `robot4`에서 `/robot4/robot_mode`가 됩니다.

| 이름 | 타입 | 발행자 | 구독자 | QoS/용도 |
|---|---|---|---|---|
| `aim/set_ori` | `std_msgs/Float32` | YOLO detector | mission manager, azimuth, target | 화면 중심 오차 -1~1 |
| `enemy_distance` | `std_msgs/Float32` | YOLO detector | target | 목표 거리 m |
| `robot_mode` | `std_msgs/String` | mission manager | azimuth, target, random patrol | reliable + transient local |
| `cmd_vel` | `geometry_msgs/Twist` | Nav2/azimuth/target | mobile base | 모드별 단일 소유 |
| `track_complete` | `std_msgs/Bool` | target | mission manager | 도달 또는 fail-safe 종료 |
| `shoot_approval` | `std_msgs/Bool` | team UI | mission manager | 사람의 명시적 승인 |
| `fire_ready` | `std_msgs/Bool` | mission manager | shooter | 안전조건 만족 후 발사 요청 |
| `shoot_complete` | `std_msgs/Bool` | shooter | mission manager | 물리 발사 완료 |
| `status` | `socamaca_msgs/TeamStatus` | mission manager | team/judge UI | reliable + transient local |
| `battery_state` | `sensor_msgs/BatteryState` | Create 3 | mission manager | 배터리 상태 |
| `my_hp`, `enemy_hp` | `std_msgs/Int32` | judge system | mission manager | 허용 범위 0~3 |
| `explore/resume` | `std_msgs/Bool` | mission manager/random patrol | explore_lite | 순찰 일시정지/재개 |
| `navigate_to_pose` | `nav2_msgs/NavigateToPose` | mission manager | Nav2 | 홈 복귀 |

## 외부 웹 인터페이스

- React UI ↔ rosbridge: WebSocket
- Judge UI ↔ FastAPI: HTTP/WebSocket
- UI의 토픽 문자열은 `src/lib/topics.ts`, 백엔드는 `app/config.py`에서 관리합니다.
