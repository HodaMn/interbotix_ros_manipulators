from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

LEADER_MODEL = 'wx250s'


def arm(model, name, modes):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_control'), 'launch', 'xsarm_control.launch.py',
            ])
        ]),
        launch_arguments={
            'robot_model': model,
            'robot_name': name,
            'use_rviz': 'false',
            'mode_configs': PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_puppet'), 'config', modes,
            ]),
        }.items(),
    )


def generate_launch_description():
    return LaunchDescription([
        arm(LEADER_MODEL, 'leader', 'leader_modes.yaml'),
        arm(LEADER_MODEL, 'leader_2', 'leader_modes_2.yaml'),
    ])