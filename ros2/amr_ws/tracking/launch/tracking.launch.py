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

"""Launch the SOCAMACA mission, aiming, and target tracking nodes."""

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from pathlib import Path


def generate_launch_description():
    namespace = LaunchConfiguration("namespace")
    config = str(
        Path(get_package_share_directory("tracking")) / "config" / "tracking.yaml"
    )

    return LaunchDescription([
        DeclareLaunchArgument("namespace", default_value="robot4"),
        Node(
            package="tracking",
            executable="mission_manager",
            namespace=namespace,
            output="screen",
        ),
        Node(
            package="tracking",
            executable="azimuth",
            namespace=namespace,
            parameters=[config],
            output="screen",
        ),
        Node(
            package="tracking",
            executable="target",
            namespace=namespace,
            parameters=[config],
            output="screen",
        ),
    ])
