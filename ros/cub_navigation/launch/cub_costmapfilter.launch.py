import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, LoadComposableNodes
from launch_ros.actions import PushRosNamespace
from launch_ros.descriptions import ComposableNode
from nav2_common.launch import RewrittenYaml

def generate_launch_description():
    # Get the launch directory
    # costmap_filters_demo_dir = get_package_share_directory('nav2_costmap_filters_demo')

    lifecycle_nodes = ['filter_mask_server', 'costmap_filter_info_server']

    # Parameters
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    params_file = LaunchConfiguration('params_file')
    mask_yaml_file = LaunchConfiguration('mask')
    use_composition = LaunchConfiguration('use_composition')
    container_name = LaunchConfiguration('container_name')
    container_name_full = (namespace, '/', container_name)
    
    # modify for cub
    cub_target = os.getenv('CUB_TARGET', 'cub3')
    if cub_target == 'cub3':
        param_file_name = 'cub3_nav2.yaml'
    elif cub_target == 'mcub':
        param_file_name = 'mcub_nav2.yaml'
    else:
        param_file_name = 'cub3_nav2.yaml'

    param_dir = LaunchConfiguration(
        'params_file',
        default=os.path.join(
            get_package_share_directory('cub_navigation'),
            'param',
            param_file_name))

    # Declare the launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Top-level namespace')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true')

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart', default_value='true',
        description='Automatically startup the nav2 stack')

    declare_params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value = param_dir,
        description='Full path to the ROS2 parameters file to use')

    declare_mask_yaml_file_cmd = DeclareLaunchArgument(
        'mask',
        default_value = "/home/cub/maps/oudanhodoumade/mapoudanhodoumade_keepOut.yaml",
        description='Full path to filter mask yaml file to load')

    declare_use_composition_cmd = DeclareLaunchArgument(
        'use_composition', default_value='True',
        description='Use composed bringup if True')

    declare_container_name_cmd = DeclareLaunchArgument(
        'container_name', default_value='nav2_container',
        description='The name of container that nodes will load in if use composition')

            
    # Make re-written yaml
    param_substitutions = {
        'use_sim_time': use_sim_time,
        'yaml_filename': mask_yaml_file}
        

    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key=namespace,
        param_rewrites=param_substitutions,
        convert_types=True)

    load_nodes = GroupAction(
        condition=IfCondition(PythonExpression(['not ', use_composition])),
        actions=[
            Node(
                package='nav2_map_server',
                executable='map_server',
                name='filter_mask_server',
                namespace=namespace,
                output='screen',
                emulate_tty=True,  # https://github.com/ros2/launch/issues/188
                parameters=[configured_params]),
            Node(
                package='nav2_map_server',
                executable='costmap_filter_info_server',
                name='costmap_filter_info_server',
                namespace=namespace,
                output='screen',
                emulate_tty=True,  # https://github.com/ros2/launch/issues/188
                parameters=[configured_params]),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_costmap_filters',
                namespace=namespace,
                output='screen',
                emulate_tty=True,  # https://github.com/ros2/launch/issues/188
                parameters=[{'use_sim_time': use_sim_time},
                            {'autostart': autostart},
                            {'node_names': lifecycle_nodes}])
        ]
    )

    load_composable_nodes = GroupAction(
        condition=IfCondition(use_composition),
        actions=[
            PushRosNamespace(
                condition=IfCondition(
                    PythonExpression([
                        "'", LaunchConfiguration('namespace'), "' != ''"
                    ])
                ),
                namespace=LaunchConfiguration('namespace')  # 必要に応じて適切なサブスティチューションをセット
            ),
            LoadComposableNodes(
                target_container=container_name_full,
                composable_node_descriptions=[
                    ComposableNode(
                        package='nav2_map_server',
                        plugin='nav2_map_server::MapServer',
                        name='filter_mask_server',
                        parameters=[configured_params]),
                    ComposableNode(
                        package='nav2_map_server',
                        plugin='nav2_map_server::CostmapFilterInfoServer',
                        name='costmap_filter_info_server',
                        parameters=[configured_params]),
                    ComposableNode(
                        package='nav2_lifecycle_manager',
                        plugin='nav2_lifecycle_manager::LifecycleManager',
                        name='lifecycle_manager_costmap_filters',
                        parameters=[{'use_sim_time': use_sim_time},
                                    {'autostart': autostart},
                                    {'node_names': lifecycle_nodes}]),
                ]
            )
        ]
    )

    ld = LaunchDescription()

    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_mask_yaml_file_cmd)

    ld.add_action(declare_use_composition_cmd)
    ld.add_action(declare_container_name_cmd)

    ld.add_action(load_nodes)
    ld.add_action(load_composable_nodes)

    return ld