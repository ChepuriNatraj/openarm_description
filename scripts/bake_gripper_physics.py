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
Bakes optimal physics drive parameters permanently into OpenArm USD files.

Usage:
    python3 src/openarm_description/scripts/bake_gripper_physics.py
"""

import glob
import os
import subprocess
import sys

# Auto-locate an environment with USD / pxr installed if missing from current interpreter
try:
    from pxr import Usd, UsdPhysics
except ImportError:
    candidate_pythons = [
        "/home/amit/miniconda3/bin/python",
        os.path.expanduser("~/miniconda3/bin/python"),
        os.path.expanduser("~/anaconda3/bin/python"),
    ] + glob.glob(os.path.expanduser("~/.local/share/ov/pkg/*isaac*/python.sh"))

    found = None
    for p in candidate_pythons:
        if os.path.exists(p):
            # Test if it has pxr
            res = subprocess.run([p, "-c", "import pxr"], capture_output=True)
            if res.returncode == 0:
                found = p
                break

    if found:
        print(f"[Note] Re-launching with USD-enabled Python: {found}")
        os.execv(found, [found] + sys.argv)
    else:
        print("[Error] No Python interpreter with 'pxr' (USD) was found.")
        print("Please install usd-core via: pip install usd-core")
        print("Or run this script in Isaac Sim's Script Editor.")
        sys.exit(1)


def bake_gripper_physics(usd_path, stiffness=150.0, damping=15.0, max_force=20.0):
    if not os.path.exists(usd_path):
        return

    print(f"[Bake Gripper Physics] Updating: {usd_path}")
    stage = Usd.Stage.Open(usd_path)
    count = 0

    for prim in stage.Traverse():
        name = prim.GetName()
        if "finger_joint" in name and prim.GetTypeName() == "PhysicsRevoluteJoint":
            drive = UsdPhysics.DriveAPI.Apply(prim, "angular")
            drive.CreateTypeAttr("force")
            drive.CreateStiffnessAttr(stiffness)
            drive.CreateDampingAttr(damping)
            drive.CreateMaxForceAttr(max_force)
            print(f"  -> {name}: stiffness={stiffness}, damping={damping}, maxForce={max_force}")
            count += 1

    stage.GetRootLayer().Save()
    print(f"  -> Saved {count} joints permanently to disk!\n")


def main():
    target_files = [
        "src/openarm_description/usd/openarm.usd",
        "src/openarm_description/assets/robot/openarm_v2.0/urdf/example/v2/configuration/v2_physics.usd",
    ]
    for f in target_files:
        bake_gripper_physics(f)
    print("[SUCCESS] All OpenArm USD files now have permanent smooth gripper mimic drives!")


if __name__ == "__main__":
    main()
