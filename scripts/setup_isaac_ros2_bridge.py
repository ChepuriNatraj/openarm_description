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
Isaac Sim Script to set up ROS 2 Joint State Subscriber ActionGraph for OpenArm v2.0.

Instructions:
1. Open Isaac Sim with ROS 2 environment:
   export ROS_DISTRO=jazzy
   isaac src/openarm_description/usd/openarm.usd
2. Open Window -> Script Editor (or press Ctrl+Shift+E).
3. Paste and Run this script.
4. Press 'Play' (Space or Play button) in Isaac Sim.
5. Move the sliders in ROS 2 joint_state_publisher_gui or run publish_test_motion.py.
"""

import omni.graph.core as og
import omni.usd
from pxr import Usd, UsdGeom


def find_robot_articulation_prim():
    stage = omni.usd.get_context().get_stage()
    # Check common articulation root names
    for prim in stage.Traverse():
        if prim.GetName() in ("openarm", "openarm_v20"):
            return prim.GetPath().pathString
    return "/openarm_v20"


def get_available_node_type(candidates, default):
    try:
        registered = {t.get_node_type() for t in og.core.get_node_types()}
        for c in candidates:
            if c in registered:
                return c
    except Exception:
        pass
    return default


def setup_ros2_joint_state_bridge():
    stage = omni.usd.get_context().get_stage()
    if not stage:
        print("[Error] No active USD stage found. Please open openarm.usd first.")
        return

    robot_prim_path = find_robot_articulation_prim()
    print(f"[OpenArm ROS2 Bridge] Configuring ActionGraph for robot at: {robot_prim_path}")

    # Resolve node type names across Isaac Sim versions
    tick_type = get_available_node_type(
        ["omni.graph.action.OnPlaybackTick", "omni.graph.action.OnImpulseEvent"],
        "omni.graph.action.OnPlaybackTick"
    )
    context_type = get_available_node_type(
        ["isaacsim.ros2.bridge.ROS2Context", "omni.isaac.ros2_bridge.ROS2Context", "omni.isaac.ros_bridge.ROS2Context"],
        "isaacsim.ros2.bridge.ROS2Context"
    )
    sub_type = get_available_node_type(
        ["isaacsim.ros2.bridge.ROS2SubscribeJointState", "omni.isaac.ros2_bridge.ROS2SubscribeJointState", "omni.isaac.ros_bridge.ROS2SubscribeJointState"],
        "isaacsim.ros2.bridge.ROS2SubscribeJointState"
    )
    art_type = get_available_node_type(
        ["isaacsim.core.nodes.IsaacArticulationController", "omni.isaac.core_nodes.IsaacArticulationController", "omni.isaac.core.nodes.IsaacArticulationController"],
        "isaacsim.core.nodes.IsaacArticulationController"
    )

    print(f"  Using Tick Node: {tick_type}")
    print(f"  Using Context Node: {context_type}")
    print(f"  Using Subscribe Node: {sub_type}")
    print(f"  Using Articulation Node: {art_type}")

    graph_path = "/ActionGraph_OpenArm_ROS2"

    # Remove existing graph prim if present to ensure clean recreation
    if stage.GetPrimAtPath(graph_path).IsValid():
        stage.RemovePrim(graph_path)

    keys = og.Controller.Keys

    try:
        # Create ActionGraph cleanly
        graph = og.Controller.create_graph(
            {"graph_path": graph_path, "evaluator_name": "execution"}
        )

        og.Controller.edit(
            graph,
            {
                keys.CREATE_NODES: [
                    ("OnPlaybackTick", tick_type),
                    ("ROS2Context", context_type),
                    ("ROS2SubscribeJointState", sub_type),
                    ("ArticulationController", art_type),
                ],
                keys.CONNECT: [
                    ("OnPlaybackTick.outputs:tick", "ROS2SubscribeJointState.inputs:execIn"),
                    ("ROS2SubscribeJointState.outputs:execOut", "ArticulationController.inputs:execIn"),
                    ("ROS2SubscribeJointState.outputs:jointNames", "ArticulationController.inputs:jointNames"),
                    ("ROS2SubscribeJointState.outputs:positionCommand", "ArticulationController.inputs:positionCommand"),
                    ("ROS2Context.outputs:context", "ROS2SubscribeJointState.inputs:context"),
                ],
                keys.SET_VALUES: [
                    ("ROS2SubscribeJointState.inputs:topicName", "/joint_states"),
                    ("ArticulationController.inputs:targetPrim", robot_prim_path),
                ],
            },
        )
        print("\n" + "="*60)
        print("  [SUCCESS] ROS 2 Joint State ActionGraph configured!")
        print("  Subscribed Topic : /joint_states")
        print("  Target Robot     : " + robot_prim_path)
        print("  Press 'Play' (Spacebar) in Isaac Sim to start receiving!")
        print("="*60 + "\n")
    except Exception as err:
        print(f"[OpenArm ROS2 Bridge Error]: {err}")
        print("\nAlternative: You can manually create the ActionGraph in Isaac Sim UI:")
        print("  1. Window -> Visual Scripting -> Action Graph -> New Action Graph")
        print("  2. Add: On Playback Tick, ROS2 Context, ROS2 Subscribe Joint State, Isaac Articulation Controller")
        print("  3. Connect Tick -> Subscribe -> Controller, and set targetPrim to " + robot_prim_path)


setup_ros2_joint_state_bridge()
