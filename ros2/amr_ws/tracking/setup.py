# Copyright 2026 SOCAMACA contributors
# SPDX-License-Identifier: Apache-2.0

from glob import glob
import os

from setuptools import find_packages, setup


package_name = "tracking"


setup(
    name=package_name,
    version="0.1.0",

    packages=find_packages(
        exclude=["test"]
    ),

    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        (
            "share/" + package_name,
            ["package.xml"],
        ),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],

    install_requires=[
        "setuptools",
    ],

    zip_safe=True,

    maintainer="rokey",
    maintainer_email="rokey@example.com",

    description="SOCAMACA mission state, aiming, tracking, and patrol controllers",

    license="Apache-2.0",

    extras_require={"test": ["pytest"]},

    entry_points={
        "console_scripts": [
            "azimuth = tracking.azimuth_tracker:main",
            "target = tracking.target_nav:main",
            "follow = tracking.tb4_follower:main",
            "mission_manager = tracking.mission_manager:main",
            "random_patrol = tracking.random_patrol:main",
        ],
    },
)
