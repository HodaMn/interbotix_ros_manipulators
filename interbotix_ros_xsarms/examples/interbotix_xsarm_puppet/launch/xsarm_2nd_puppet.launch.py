from typing import List

from interbotix_xs_modules.xs_common import (
    get_interbotix_xsarm_models,
)
from interbotix_xs_modules.xs_launch import (
    declare_interbotix_xsarm_robot_description_launch_arguments,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.conditions import (
  IfCondition,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    robot_model_leader_launch_arg = LaunchConfiguration('robot_model_leader_2')
    robot_name_leader_launch_arg = LaunchConfiguration('robot_name_leader_2')
    robot_model_follower_launch_arg = LaunchConfiguration('robot_model_follower_2')
    robot_name_follower_launch_arg = LaunchConfiguration('robot_name_follower_2')
    use_puppet_rviz_launch_arg = LaunchConfiguration('use_puppet_rviz')
    launch_driver_launch_arg = LaunchConfiguration('launch_driver')
    use_sim_launch_arg = LaunchConfiguration('use_sim')
    xs_driver_logging_level_launch_arg = LaunchConfiguration('xs_driver_logging_level')
    tf_x_offset_launch_arg = LaunchConfiguration('tf_x_offset')

    xsarm_control_launch_leader = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_control'),
                'launch',
                'xsarm_control.launch.py'
            ])
        ]),
        launch_arguments={
            'robot_model': robot_model_leader_launch_arg,
            'robot_name': robot_name_leader_launch_arg,
            'base_link_frame': 'base_link',
            'use_rviz': 'false',
            'mode_configs': LaunchConfiguration('mode_configs_leader'),
            'motor_configs': LaunchConfiguration('motor_configs_leader'),
            'use_sim': use_sim_launch_arg,
            'robot_description': LaunchConfiguration('robot_description_leader'),
            'xs_driver_logging_level': xs_driver_logging_level_launch_arg,
        }.items(),
        condition=IfCondition(launch_driver_launch_arg),
    )

    xsarm_control_launch_follower = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_control'),
                'launch',
                'xsarm_control.launch.py'
            ])
        ]),
        launch_arguments={
            'robot_model': robot_model_follower_launch_arg,
            'robot_name': robot_name_follower_launch_arg,
            'base_link_frame': 'base_link',
            'use_rviz': 'false',
            'mode_configs': LaunchConfiguration('mode_configs_follower'),
            'motor_configs': LaunchConfiguration('motor_configs_follower'),
            'use_sim': use_sim_launch_arg,
            'robot_description': LaunchConfiguration('robot_description_follower'),
            'xs_driver_logging_level': xs_driver_logging_level_launch_arg,
        }.items(),
        condition=IfCondition(launch_driver_launch_arg),
    )

    xsarm_puppet_node = Node(
        name='xsarm_puppet_2',
        package='interbotix_xsarm_puppet',
        executable='xsarm_puppet',
        output='screen',
        parameters=[
            {
                'robot_name_leader': LaunchConfiguration('robot_name_leader_2'),
                'robot_name_follower': LaunchConfiguration('robot_name_follower_2'),
            }
        ]
    )

    tf_broadcaster_leader = Node(
        name='tf_broadcaster_leader_2',
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', tf_x_offset_launch_arg,
            '--y', '-0.25',
            '--z', '0.0',
            '--frame-id', '/world',
            '--child-frame-id', (robot_name_leader_launch_arg, '/base_link'),
        ]
    )

    tf_broadcaster_follower = Node(
        name='tf_broadcaster_follower_2',
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', tf_x_offset_launch_arg,
            '--y', '0.25',
            '--z', '0.0',
            '--frame-id', '/world',
            '--child-frame-id', (robot_name_follower_launch_arg, '/base_link'),
        ]
    )

    rviz2_node = Node(
        condition=IfCondition(use_puppet_rviz_launch_arg),
        package='rviz2',
        executable='rviz2',
        name='rviz2_2',
        arguments=[
            '-d', LaunchConfiguration('rvizconfig'),
        ],
        output={'both': 'log'},
    )

    return [
        xsarm_control_launch_leader,
        xsarm_control_launch_follower,
        xsarm_puppet_node,
        tf_broadcaster_leader,
        tf_broadcaster_follower,
        rviz2_node,
    ]


def generate_launch_description():
    declared_arguments: List[DeclareLaunchArgument] = []
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_model_leader_2',
            choices=get_interbotix_xsarm_models(),
            description='model type of the leader (pair 2) Interbotix Arm such as `wx200`.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_name_leader_2',
            default_value='leader_2',
            description='name of the leader robot (pair 2).',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_model_follower_2',
            choices=get_interbotix_xsarm_models(),
            description='model type of the follower (pair 2) Interbotix Arm such as `vx300`.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_name_follower_2',
            default_value='follower_2',
            description='name of the follower robot (pair 2).',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'mode_configs_leader',
            default_value=PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_puppet'),
                'config',
                'leader_modes_2.yaml',
            ]),
            description="the file path to the 'mode config' YAML file for the leader arm (pair 2).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'mode_configs_follower',
            default_value=PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_puppet'),
                'config',
                'follower_modes_2.yaml',
            ]),
            description="the file path to the 'mode config' YAML file for the follower arm (pair 2).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'motor_configs_leader',
            default_value=(PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_control'),
                'config',
                LaunchConfiguration('robot_model_leader_2')]), '.yaml'),
            description="the file path to the 'motor config' YAML file for the leader arm (pair 2).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'motor_configs_follower',
            default_value=(PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_control'),
                'config',
                LaunchConfiguration('robot_model_follower_2')]), '.yaml'),
            description="the file path to the 'motor config' YAML file for the follower arm (pair 2).",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_puppet_rviz',
            default_value='false',
            choices=('true', 'false'),
            description='launches RViz if set to `true`. Off by default so pair 1 keeps the window.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'rvizconfig',
            default_value=PathJoinSubstitution([
                FindPackageShare('interbotix_xsarm_puppet'),
                'rviz',
                'xsarm_puppet_two_pairs.rviz',
            ]),
            description='file path to the config file RViz should load.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'tf_x_offset',
            default_value='0.6',
            description='x position of this pair in RViz, so it does not overlap pair 1.',
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'launch_driver',
            default_value='true',
            choices=('true', 'false'),
            description=(
                '`true` if xsarm_control should be launched - set to `false` if you would like to '
                'run your own version of this file separately.'
            ),
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'xs_driver_logging_level',
            default_value='INFO',
            choices=('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'),
            description='set the logging level of the X-Series Driver.'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim',
            default_value='false',
            choices=('true', 'false'),
            description=(
                "if `true`, the DYNAMIXEL simulator node is run; use RViz to visualize the robot's"
                ' motion; if `false`, the real DYNAMIXEL driver node is run.'
            ),
        )
    )
    declared_arguments.extend(
        declare_interbotix_xsarm_robot_description_launch_arguments(
            robot_description_launch_config_name='robot_description_leader',
            robot_model_launch_config_name='robot_model_leader_2',
            robot_name_launch_config_name='robot_name_leader_2',
            use_world_frame='false',
        )
    )
    declared_arguments.extend(
        declare_interbotix_xsarm_robot_description_launch_arguments(
            robot_description_launch_config_name='robot_description_follower',
            robot_model_launch_config_name='robot_model_follower_2',
            robot_name_launch_config_name='robot_name_follower_2',
            use_world_frame='false',
        )
    )
    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
