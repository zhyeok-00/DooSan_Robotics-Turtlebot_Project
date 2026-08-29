# Copyright 2026 SOCAMACA contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ROS에 의존하지 않는 SOCAMACA 이동 제어 및 안전 판단 함수."""

from dataclasses import dataclass
from enum import Enum
import math


class TargetAction(Enum):
    """TRACK 제어기의 현재 안전 동작."""

    WAITING = "waiting"
    ACTIVE = "active"
    COMPLETE = "complete"
    LOST = "lost"
    INVALID = "invalid"


@dataclass(frozen=True)
class TargetControl:
    action: TargetAction
    linear_x: float = 0.0
    angular_z: float = 0.0


def clamp(value: float, lower: float, upper: float) -> float:
    """value를 닫힌 구간 [lower, upper]로 제한한다."""
    if lower > upper:
        raise ValueError("lower must not exceed upper")
    return max(lower, min(upper, value))


def angular_command(error: float | None, kp: float, deadband: float, max_angular: float) -> float:
    """화면 수평 오차를 제한된 회전 속도로 변환한다."""
    if error is None:
        return 0.0
    if not math.isfinite(error):
        raise ValueError("error must be finite")
    if kp < 0.0 or deadband < 0.0 or max_angular < 0.0:
        raise ValueError("control gains and limits must be non-negative")
    if abs(error) < deadband:
        return 0.0
    return clamp(-kp * error, -max_angular, max_angular)


def slew_rate(current: float, target: float, max_delta: float) -> float:
    """한 제어 주기 동안 속도 변화량을 제한한다."""
    if max_delta < 0.0:
        raise ValueError("max_delta must be non-negative")
    return current + clamp(target - current, -max_delta, max_delta)


def target_control(
    *,
    error: float | None,
    distance: float | None,
    orientation_age: float | None,
    distance_age: float | None,
    session_age: float,
    signal_timeout: float,
    kp: float,
    deadband: float,
    max_angular: float,
    linear_speed: float,
    stop_distance: float,
) -> TargetControl:
    """TRACK 입력의 완전성·신선도·유효성을 검사하고 안전 명령을 계산한다."""
    if signal_timeout <= 0.0 or linear_speed < 0.0 or stop_distance <= 0.0:
        raise ValueError("timeouts and distances must be positive; speed must be non-negative")

    missing = error is None or distance is None or orientation_age is None or distance_age is None
    if missing:
        action = TargetAction.LOST if session_age > signal_timeout else TargetAction.WAITING
        return TargetControl(action)

    if not all(math.isfinite(v) for v in (error, distance, orientation_age, distance_age)):
        return TargetControl(TargetAction.INVALID)
    if distance <= 0.0:
        return TargetControl(TargetAction.INVALID)
    if orientation_age > signal_timeout or distance_age > signal_timeout:
        return TargetControl(TargetAction.LOST)
    if distance <= stop_distance:
        return TargetControl(TargetAction.COMPLETE)

    return TargetControl(
        TargetAction.ACTIVE,
        linear_x=linear_speed,
        angular_z=angular_command(error, kp, deadband, max_angular),
    )
