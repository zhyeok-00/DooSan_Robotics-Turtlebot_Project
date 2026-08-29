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

"""MissionManager에서 공유하는 ROS 독립 안전 정책."""


def valid_hp(value: int, minimum: int = 0, maximum: int = 3) -> bool:
    """심판 시스템에서 받은 HP가 허용 범위인지 검사한다."""
    return minimum <= value <= maximum


def priority_return_reason(my_hp: int, enemy_hp: int) -> str | None:
    """모든 일반 상태 전이보다 우선하는 복귀 사유를 반환한다."""
    if my_hp <= 0:
        return "내 HP 0 (사망)"
    if enemy_hp <= 0:
        return "상대 HP 0 (미션 완료)"
    return None


def fire_authorized(
    *,
    aligned: bool,
    human_approved: bool,
    already_requested: bool,
    ammo: int,
    reload_remaining: float,
) -> bool:
    """사람 승인과 기계 상태를 모두 만족할 때만 발사를 허용한다."""
    return (
        aligned
        and human_approved
        and not already_requested
        and ammo > 0
        and reload_remaining <= 0.0
    )
