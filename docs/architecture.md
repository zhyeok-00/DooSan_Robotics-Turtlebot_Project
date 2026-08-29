# SOCAMACA 시스템 아키텍처

## 전체 데이터 흐름

```mermaid
flowchart LR
    CAM[Phone / OAK-D Camera] --> DET[YOLO Detector]
    DET -->|aim/set_ori| MM[Mission Manager]
    DET -->|enemy_distance| TRACK[Target Navigation]
    MM -->|robot_mode| AIM[Azimuth Controller]
    MM -->|robot_mode| TRACK
    MM -->|robot_mode| PATROL[Explore Lite / Nav2]
    AIM --> MUX{Mode-based cmd_vel ownership}
    TRACK --> MUX
    PATROL --> MUX
    MUX --> BASE[TurtleBot4 Base]
    MM -->|status, aim/complete| BRIDGE[rosbridge]
    BRIDGE <--> UI[React Team UI]
    UI -->|shoot_approval| MM
    MM -->|fire_ready| SHOOTER[Arduino Shooter]
    SHOOTER -->|shoot_complete| MM
```

`cmd_vel`은 별도 소프트웨어 mux가 아니라 `robot_mode`에 따른 상호 배타적 발행으로 소유권을 나눕니다.

| 모드 | `cmd_vel` 소유자 | 동작 |
|---|---|---|
| `PATROL`, `COOLDOWN`, `RETURN` | Nav2 / explore_lite | 순찰 또는 복귀 |
| `WAIT_COMMAND` | `azimuth_tracker` | 제자리 조준 회전 |
| `TRACK` | `target_nav` | 목표 방향 회전 및 제한 속도 접근 |

## 배포 구성

```mermaid
flowchart TB
    subgraph TeamPC[Team PC]
      PERCEPTION[YOLO / Camera]
      CONTROL[Mission and Control Nodes]
      WEB[React UI + rosbridge]
    end
    subgraph RobotPC[TurtleBot4 Raspberry Pi]
      NAV[Create 3 / Nav2 / SLAM]
      MCU[Arduino Shooter]
    end
    subgraph JudgePC[Judge PC]
      JUDGE[Judge UI / Vision / FastAPI]
    end
    TeamPC <-->|DDS discovery| RobotPC
    WEB <-->|WebSocket / HTTP| JudgePC
    RobotPC -->|Serial| MCU
```

환경별 IP, ROS workspace 경로와 계정은 저장소가 아닌 루트 `.env`에서 주입합니다.
