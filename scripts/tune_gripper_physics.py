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
Isaac Sim Script: Automatically tunes OpenArm Gripper Finger Joint Drives for smooth motion.

Instructions:
1. In Isaac Sim, open Window -> Script Editor.
2. Paste and click Run.
"""

import omni.usd
from pxr import Usd, UsdPhysics


def tune_gripper_joints():
    stage = omni.usd.get_context().get_stage()
    if not stage:
        print("[Error] No active USD stage found.")
        return

    tuned = 0
    for prim in stage.Traverse():
        name = prim.GetName()
        if "finger_joint" in name and prim.IsA(UsdPhysics.RevoluteJoint):
            drive = UsdPhysics.DriveAPI.Get(prim, "angular")
            if not drive:
                drive = UsdPhysics.DriveAPI.Apply(prim, "angular")

            drive.CreateTypeAttr("force")

            if "joint2" in name:
                # Follower mimic joint: Zero stiffness so it follows mimic constraint freely
                drive.CreateStiffnessAttr(0.0)
                drive.CreateDampingAttr(5.0)
                print(f"[Gripper Tuner] Follower {name}: Stiffness=0.0, Damping=5.0 (Smooth Mimic Follower)")
            else:
                # Driver joint: Responsive position drive
                drive.CreateStiffnessAttr(250.0)
                drive.CreateDampingAttr(25.0)
                print(f"[Gripper Tuner] Driver {name}: Stiffness=250.0, Damping=25.0 (Active Driver)")

            tuned += 1

    if tuned == 0:
        # Check if joints are under physics joint schemas directly
        for prim in stage.Traverse():
            name = prim.GetName()
            if "finger_joint" in name:
                drive = UsdPhysics.DriveAPI.Apply(prim, "angular")
                if "joint2" in name:
                    drive.CreateStiffnessAttr(0.0)
                    drive.CreateDampingAttr(5.0)
                else:
                    drive.CreateStiffnessAttr(250.0)
                    drive.CreateDampingAttr(25.0)
                print(f"[Gripper Tuner] Tuned {name}")
                tuned += 1

    print(f"\n[SUCCESS] Tuned {tuned} finger joints for smooth gripper motion!")


tune_gripper_joints()
