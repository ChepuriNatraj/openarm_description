# Robot Description files for OpenArm

This package contains description files to generate **OpenArm v2.0** URDFs (Universal Robot Description Format) and launch visualization in ROS 2. See [documentation](https://docs.openarm.dev/software/description) for details.

---

## Package Overview

* **Robot**: OpenArm v2.0 (`assets/robot/openarm_v2.0`)
* **End Effector**: Pinch Gripper (`assets/end_effector/pinch_gripper`)
* **Sensor**: ZED Camera Wrapper (`assets/sensor/zed`)

---

## Build

From your ROS 2 workspace root (e.g. `~/Desktop/real_robot`):

```bash
colcon build --packages-select openarm_description
source install/setup.bash
```

---

## Visualization

Launch the interactive RViz2 viewer and joint state publisher GUI:

```bash
ros2 launch openarm_description display_openarm.launch.py
```

### Available Presets (`robot_preset`)

You can select a robot configuration preset at launch:

* **`default_bimanual`** *(default)*: Dual-arm configuration
  ```bash
  ros2 launch openarm_description display_openarm.launch.py robot_preset:=default_bimanual
  ```
* **`right_arm`**: Single right arm without gripper
  ```bash
  ros2 launch openarm_description display_openarm.launch.py robot_preset:=right_arm
  ```
* **`left_arm`**: Single left arm without gripper
  ```bash
  ros2 launch openarm_description display_openarm.launch.py robot_preset:=left_arm
  ```
* **`right_arm_with_pinch_gripper`**: Single right arm with pinch gripper
  ```bash
  ros2 launch openarm_description display_openarm.launch.py robot_preset:=right_arm_with_pinch_gripper
  ```
* **`left_arm_with_pinch_gripper`**: Single left arm with pinch gripper
  ```bash
  ros2 launch openarm_description display_openarm.launch.py robot_preset:=left_arm_with_pinch_gripper
  ```

### Launch Arguments

| Argument | Default | Description |
|---|---|---|
| `robot_preset` | `default_bimanual` | Configuration preset to load |
| `arm_type` | `v20` | Arm model type (`v20`, `v2.0`, `openarm_v2.0`) |
| `rviz_config` | `bimanual.rviz` | RViz configuration file to load |
| `collapse_internal_empty_links` | `true` | Simplify internal intermediate link frames |
| `emit_grasp_frame` | `false` | Expose helper grasp frames on the end effector |
| `use_fake_hardware` | `true` | Use ROS 2 mock hardware interface |

---

## Standalone URDF Generation

To generate a standalone `.urdf` file using `xacro`:

```bash
xacro $(ros2 pkg prefix --share openarm_description)/assets/robot/openarm_v2.0/urdf/openarm_v20.urdf.xacro robot_preset:=default_bimanual > openarm_v20.urdf
```

---

## Isaac Sim & ROS 2 Real-Time Visualization

You can synchronize robot motions in real-time between ROS 2 (`/joint_states`) and Isaac Sim:

### 1. Open the Robot in Isaac Sim
```bash
isaac src/openarm_description/usd/openarm.usd
```

### 2. Connect ROS 2 Joint State Bridge in Isaac Sim
Inside Isaac Sim:
* Open **Window** $\rightarrow$ **Script Editor** (or press `Ctrl+Shift+E`).
* Open and run [`scripts/setup_isaac_ros2_bridge.py`](src/openarm_description/scripts/setup_isaac_ros2_bridge.py).
* Press the **Play** ($\blacktriangleright$) button in Isaac Sim.

### 3. Drive Robot Motions from ROS 2
* **Option A - Interactive GUI Sliders**:
  ```bash
  ros2 launch openarm_description display_openarm.launch.py
  ```
  *(Moving the joint sliders in the GUI will move the robot in both RViz and Isaac Sim)*.

* **Option B - Automated Smooth Motion Test**:
  ```bash
  source /opt/ros/jazzy/setup.bash
  python3 src/openarm_description/scripts/publish_test_motion.py
  ```

---

## Related Links

- 📚 Read the [documentation](https://docs.openarm.dev/software/description)
- 💬 Join the community on [Discord](https://discord.gg/FsZaZ4z3We)
- 📬 Contact us through <openarm@enactic.ai>

## License

[Apache License 2.0](LICENSE.txt)

Copyright 2026 Enactic, Inc.

## Code of Conduct

All participation in the OpenArm project is governed by our [Code of Conduct](CODE_OF_CONDUCT.md).
