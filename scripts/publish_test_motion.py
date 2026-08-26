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

import math
import sys
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class OpenArmMotionPublisher(Node):
    """Publishes continuous smooth wave trajectories to /joint_states for visualization."""

    def __init__(self):
        super().__init__("openarm_motion_publisher")
        self.publisher_ = self.create_publisher(JointState, "/joint_states", 10)
        self.timer_period = 0.02  # 50 Hz
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.start_time = self.get_clock().now()

        # All controllable joints for OpenArm v2.0 bimanual setup
        self.joint_names = [
            "openarm_left_joint1",
            "openarm_left_joint2",
            "openarm_left_joint3",
            "openarm_left_joint4",
            "openarm_left_joint5",
            "openarm_left_joint6",
            "openarm_left_joint7",
            "openarm_left_finger_joint1",
            "openarm_left_finger_joint2",
            "openarm_right_joint1",
            "openarm_right_joint2",
            "openarm_right_joint3",
            "openarm_right_joint4",
            "openarm_right_joint5",
            "openarm_right_joint6",
            "openarm_right_joint7",
            "openarm_right_finger_joint1",
            "openarm_right_finger_joint2",
        ]

        self.get_logger().info("OpenArm v2.0 Motion Publisher started. Publishing to /joint_states at 50Hz...")

    def timer_callback(self):
        now = self.get_clock().now()
        t = (now - self.start_time).nanoseconds / 1e9

        msg = JointState()
        msg.header.stamp = now.to_msg()
        msg.name = self.joint_names

        # Wave generation with gentle amplitudes inside safe joint limits
        # Left arm
        l_j1 = 0.4 * math.sin(0.8 * t)
        l_j2 = 0.3 * math.sin(0.6 * t + 0.5)
        l_j3 = 0.5 * math.sin(0.7 * t + 1.0)
        l_j4 = 0.6 * math.sin(0.9 * t) + 0.6  # elbow flexion
        l_j5 = 0.4 * math.sin(1.1 * t)
        l_j6 = 0.3 * math.sin(0.8 * t + 0.2)
        l_j7 = 0.5 * math.sin(1.0 * t)
        l_finger = 0.25 * (math.sin(1.2 * t) + 1.0) * 0.5  # smooth 0.0 to 0.25 rad

        # Right arm (mirrored phase)
        r_j1 = -0.4 * math.sin(0.8 * t)
        r_j2 = -0.3 * math.sin(0.6 * t + 0.5)
        r_j3 = -0.5 * math.sin(0.7 * t + 1.0)
        r_j4 = 0.6 * math.sin(0.9 * t + math.pi) + 0.6
        r_j5 = -0.4 * math.sin(1.1 * t)
        r_j6 = -0.3 * math.sin(0.8 * t + 0.2)
        r_j7 = -0.5 * math.sin(1.0 * t)
        r_finger = 0.25 * (math.sin(1.2 * t + math.pi) + 1.0) * 0.5

        msg.position = [
            l_j1, l_j2, l_j3, l_j4, l_j5, l_j6, l_j7, l_finger, l_finger,
            r_j1, r_j2, r_j3, r_j4, r_j5, r_j6, r_j7, r_finger, r_finger,
        ]

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = OpenArmMotionPublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
