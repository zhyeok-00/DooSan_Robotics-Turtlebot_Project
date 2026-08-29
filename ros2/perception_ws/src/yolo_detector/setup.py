# Copyright 2026 SOCAMACA contributors
# SPDX-License-Identifier: Apache-2.0

from setuptools import find_packages, setup

package_name = 'yolo_detector'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy', 'ultralytics'],
    zip_safe=True,
    maintainer='SOCAMACA contributors',
    maintainer_email='contact@example.com',
    description='ROS 2 YOLO detectors for the SOCAMACA robot system',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'bbox4 = yolo_detector.bbox4:main',
            'phone_cam_detector = yolo_detector.phone_cam_detector:main',
        ],
    },
)
