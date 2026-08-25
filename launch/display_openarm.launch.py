# Copyright 2025 Enactic, Inc.
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
import os

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, LaunchContext
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# All accepted arm_type values
VALID_ARM_TYPES = {
    "v2.0", "v20", "v2_0", "openarm_v2.0", "openarm_v20", "openarm_v2_0",
}


def robot_state_publisher_spawner(
    context: LaunchContext,
    arm_type,
    robot_preset,
    collapse_internal_empty_links,
    emit_grasp_frame,
    use_fake_hardware,
):
    arm_type_str = context.perform_substitution(arm_type)
    if arm_type_str not in VALID_ARM_TYPES:
        raise ValueError(
            f"Invalid arm_type: '{arm_type_str}'. "
            f"Accepted values: {sorted(VALID_ARM_TYPES)}."
        )

    pkg_share = get_package_share_directory("openarm_description")

    xacro_path = os.path.join(
        pkg_share,
        "assets",
        "robot",
        "openarm_v2.0",
        "urdf",
        "openarm_v20.urdf.xacro",
    )

    mappings = {
        "robot_preset": context.perform_substitution(robot_preset),
        "collapse_internal_empty_links": context.perform_substitution(collapse_internal_empty_links),
        "emit_grasp_frame": context.perform_substitution(emit_grasp_frame),
        "use_fake_hardware": context.perform_substitution(use_fake_hardware),
    }

    robot_description = xacro.process_file(
        xacro_path,
        mappings=mappings,
    ).toprettyxml(indent="  ")

    return [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description}],
        )
    ]


def generate_launch_description():
    arm_type_arg = DeclareLaunchArgument(
        "arm_type",
        default_value="v20",
        description="Arm type. Accepts: v2.0, v20, openarm_v2.0, etc.",
    )
    robot_preset_arg = DeclareLaunchArgument(
        "robot_preset",
        default_value="default_bimanual",
        description="Robot preset for v2.0 (e.g. default_bimanual, right_arm, left_arm, right_arm_with_pinch_gripper, left_arm_with_pinch_gripper).",
    )
    rviz_config_arg = DeclareLaunchArgument(
        "rviz_config",
        default_value="bimanual.rviz",
    )
    collapse_arg = DeclareLaunchArgument(
        "collapse_internal_empty_links",
        default_value="true",
    )
    grasp_frame_arg = DeclareLaunchArgument(
        "emit_grasp_frame",
        default_value="false",
    )
    use_fake_hardware_arg = DeclareLaunchArgument(
        "use_fake_hardware",
        default_value="true",
    )

    arm_type = LaunchConfiguration("arm_type")
    robot_preset = LaunchConfiguration("robot_preset")
    rviz_config = LaunchConfiguration("rviz_config")
    collapse = LaunchConfiguration("collapse_internal_empty_links")
    grasp_frame = LaunchConfiguration("emit_grasp_frame")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")

    pkg_share = get_package_share_directory("openarm_description")

    return LaunchDescription([
        arm_type_arg,
        robot_preset_arg,
        rviz_config_arg,
        collapse_arg,
        grasp_frame_arg,
        use_fake_hardware_arg,
        OpaqueFunction(
            function=robot_state_publisher_spawner,
            args=[
                arm_type,
                robot_preset,
                collapse,
                grasp_frame,
                use_fake_hardware,
            ],
        ),
        Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["--display-config",
                       [os.path.join(pkg_share, "rviz/"), rviz_config]],
        ),
    ])
