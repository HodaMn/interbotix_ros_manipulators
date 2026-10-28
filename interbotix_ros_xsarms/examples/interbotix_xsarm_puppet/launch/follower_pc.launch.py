from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

FOLLOWER_MODEL = 'wx250s'


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


def puppet(index, leader, follower):
    return Node(
        name=f'xsarm_puppet_{index}',
        package='interbotix_xsarm_puppet',
        executable='xsarm_puppet',
        output='screen',
        parameters=[{
            'robot_name_leader': leader,
            'robot_name_follower': follower,
        }],
    )


def generate_launch_description():
    return LaunchDescription([
        arm(FOLLOWER_MODEL, 'follower', 'follower_modes.yaml'),
        arm(FOLLOWER_MODEL, 'follower_2', 'follower2_modes.yaml'),
        puppet(1, 'leader', 'follower'),
        puppet(2, 'leader_2', 'follower_2'),
    ])