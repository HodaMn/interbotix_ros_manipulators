from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def control_include(model, name, mode_configs, use_sim):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_control'),
                'launch',
                'xsarm_control.launch.py',
            ])
        ]),
        launch_arguments={
            'robot_model': model,
            'robot_name': name,
            'base_link_frame': 'base_link',
            'use_rviz': 'false',
            'mode_configs': mode_configs,
            'use_sim': use_sim,
        }.items(),
    )


def puppet_pair(index, leader_model, follower_model, use_sim, x_offset):
    leader = f'leader_{index}'
    follower = f'follower_{index}'
    leader_modes = PathJoinSubstitution([
        FindPackageShare('interbotix_xsarm_puppet'), 'config', 'leader_modes.yaml'])
    follower_modes = PathJoinSubstitution([
        FindPackageShare('interbotix_xsarm_puppet'), 'config', 'follower_modes.yaml'])

    return [
        control_include(leader_model, leader, leader_modes, use_sim),
        control_include(follower_model, follower, follower_modes, use_sim),
        Node(
            name=f'xsarm_puppet_{index}',
            package='interbotix_xsarm_puppet',
            executable='xsarm_puppet',
            output='screen',
            parameters=[{
                'robot_name_leader': leader,
                'robot_name_follower': follower,
            }],
        ),
        Node(
            name=f'tf_leader_{index}',
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=[
                '--x', str(x_offset), '--y', '-0.25', '--z', '0.0',
                '--frame-id', '/world',
                '--child-frame-id', (leader, '/base_link'),
            ],
        ),
        Node(
            name=f'tf_follower_{index}',
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=[
                '--x', str(x_offset), '--y', '0.25', '--z', '0.0',
                '--frame-id', '/world',
                '--child-frame-id', (follower, '/base_link'),
            ],
        ),
    ]


def generate_launch_description():
    declared = [
        DeclareLaunchArgument('robot_model_1', default_value='wx250s',
                              description='model for pair 1 (leader and follower)'),
        DeclareLaunchArgument('robot_model_2', default_value='wx250s',
                              description='model for pair 2 (leader and follower)'),
        DeclareLaunchArgument('use_sim', default_value='false', choices=('true', 'false')),
    ]
    use_sim = LaunchConfiguration('use_sim')
    pair_1 = puppet_pair(1, LaunchConfiguration('robot_model_1'),
                         LaunchConfiguration('robot_model_1'), use_sim, 0.0)
    pair_2 = puppet_pair(2, LaunchConfiguration('robot_model_2'),
                         LaunchConfiguration('robot_model_2'), use_sim, 0.6)
    return LaunchDescription(declared + pair_1 + pair_2)
