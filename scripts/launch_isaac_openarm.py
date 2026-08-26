#!/usr/bin/env python3
# Copyright 2026 Enactic, Inc.
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

"""
Standalone Isaac Sim Application Launcher for OpenArm v2.0 with ROS 2 Joint States.

Usage:
    isaac-sim.sh --exec src/openarm_description/scripts/launch_isaac_openarm.py
    or:
    python.sh src/openarm_description/scripts/launch_isaac_openarm.py
"""

import os
import sys

try:
    from isaacsim import SimulationApp
except ImportError:
    try:
        from omni.isaac.kit import SimulationApp
    except ImportError:
        print("[Error] This script must be run with Isaac Sim's Python environment (e.g. ./python.sh or isaac-sim).")
        sys.exit(1)

simulation_app = SimulationApp({"headless": False})

import omni.graph.core as og
import omni.usd
from ament_index_python.packages import get_package_share_directory
from pxr import Usd, UsdGeom
import carb


def get_usd_path():
    possible_paths = [
        os.path.abspath("src/openarm_description/usd/openarm.usd"),
        os.path.abspath("src/openarm_description/assets/robot/openarm_v2.0/urdf/example/v2/v2.usd"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return possible_paths[0]


def main():
    # Enable ROS2 bridge extension
    from omni.isaac.core.utils.extensions import enable_extension
    try:
        enable_extension("isaacsim.ros2.bridge")
    except Exception:
        enable_extension("omni.isaac.ros2_bridge")

    usd_path = get_usd_path()
    print(f"[Isaac Sim OpenArm] Loading USD: {usd_path}")

    # Open the stage
    omni.usd.get_context().open_stage(usd_path)

    # Setup the ActionGraph
    from setup_isaac_ros2_bridge import setup_ros2_joint_state_bridge
    setup_ros2_joint_state_bridge()

    print("[Isaac Sim OpenArm] Ready! Moving OpenArm in ROS 2 will reflect here in real-time.")

    # Simulation loop
    while simulation_app.is_running():
        simulation_app.update()

    simulation_app.close()


if __name__ == "__main__":
    main()
