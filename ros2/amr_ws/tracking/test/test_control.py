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

"""ROS 없이 실행 가능한 핵심 이동 제어 단위 테스트."""

import math

import pytest

from tracking.control import (
    TargetAction,
    angular_command,
    slew_rate,
    target_control,
)


def target(**overrides):
    values = {
        "error": 0.25,
        "distance": 2.0,
        "orientation_age": 0.1,
        "distance_age": 0.1,
        "session_age": 0.2,
        "signal_timeout": 1.0,
        "kp": 0.8,
        "deadband": 0.05,
        "max_angular": 0.3,
        "linear_speed": 0.15,
        "stop_distance": 1.0,
    }
    values.update(overrides)
    return target_control(**values)


def test_angular_command_applies_deadband_and_limit():
    assert angular_command(0.01, 0.8, 0.05, 0.3) == 0.0
    assert angular_command(1.0, 0.8, 0.05, 0.3) == -0.3
    assert angular_command(-1.0, 0.8, 0.05, 0.3) == 0.3


def test_slew_rate_limits_each_control_tick():
    assert slew_rate(0.0, 0.3, 0.05) == pytest.approx(0.05)
    assert slew_rate(0.2, -0.3, 0.05) == pytest.approx(0.15)


def test_track_waits_for_both_fresh_signals_without_moving():
    decision = target(distance=None, distance_age=None)
    assert decision.action is TargetAction.WAITING
    assert decision.linear_x == 0.0
    assert decision.angular_z == 0.0


def test_missing_or_stale_signal_fails_safe():
    assert target(distance=None, distance_age=None, session_age=1.1).action is TargetAction.LOST
    assert target(orientation_age=1.1).action is TargetAction.LOST


@pytest.mark.parametrize("distance", [0.0, -1.0, math.nan, math.inf])
def test_invalid_distance_never_commands_motion(distance):
    decision = target(distance=distance)
    assert decision.action is TargetAction.INVALID
    assert decision.linear_x == 0.0


def test_stop_distance_completes_and_stops():
    decision = target(distance=1.0)
    assert decision.action is TargetAction.COMPLETE
    assert decision.linear_x == 0.0


def test_valid_target_combines_forward_and_turn_commands():
    decision = target(error=0.5, distance=2.0)
    assert decision.action is TargetAction.ACTIVE
    assert decision.linear_x == pytest.approx(0.15)
    assert decision.angular_z == pytest.approx(-0.3)
