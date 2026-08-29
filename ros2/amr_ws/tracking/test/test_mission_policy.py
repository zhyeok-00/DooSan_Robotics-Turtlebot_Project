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

"""HP 및 휴먼인더루프 발사 정책 테스트."""

import pytest

from tracking.mission_policy import (
    fire_authorized,
    priority_return_reason,
    valid_hp,
)


@pytest.mark.parametrize("hp", [0, 1, 2, 3])
def test_valid_hp_accepts_game_range(hp):
    assert valid_hp(hp)


@pytest.mark.parametrize("hp", [-1, 4, 99])
def test_valid_hp_rejects_out_of_range_values(hp):
    assert not valid_hp(hp)


def test_own_destroyed_state_has_highest_return_priority():
    assert priority_return_reason(0, 0) == "내 HP 0 (사망)"
    assert priority_return_reason(3, 0) == "상대 HP 0 (미션 완료)"
    assert priority_return_reason(3, 1) is None


@pytest.mark.parametrize(
    "override",
    [
        {"aligned": False},
        {"human_approved": False},
        {"already_requested": True},
        {"ammo": 0},
        {"reload_remaining": 0.1},
    ],
)
def test_fire_requires_every_safety_condition(override):
    conditions = {
        "aligned": True,
        "human_approved": True,
        "already_requested": False,
        "ammo": 1,
        "reload_remaining": 0.0,
    }
    conditions.update(override)
    assert not fire_authorized(**conditions)


def test_fire_is_authorized_only_when_all_conditions_pass():
    assert fire_authorized(
        aligned=True,
        human_approved=True,
        already_requested=False,
        ammo=1,
        reload_remaining=0.0,
    )
