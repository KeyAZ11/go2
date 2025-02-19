import time
import sys
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_go_msg_dds__LowState_
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_
from unitree_sdk2py.go2.robot_state.robot_state_client import RobotStateClient
from unitree_sdk2py.go2.sport.sport_client import SportClient

@dataclass
class RobotState:
    """Robot state data structure"""
    # System states
    is_active: bool = False
    timestamp: float = 0.0
    
    # IMU states
    quaternion: tuple = (0.0, 0.0, 0.0, 0.0)  # w, x, y, z
    rpy: tuple = (0.0, 0.0, 0.0)  # roll, pitch, yaw
    acceleration: tuple = (0.0, 0.0, 0.0)  # x, y, z
    angular_velocity: tuple = (0.0, 0.0, 0.0)  # x, y, z
    
    # Motion states
    position: tuple = (0.0, 0.0, 0.0)  # x, y, z
    velocity: tuple = (0.0, 0.0, 0.0)  # x, y, z
    
    # Power states
    battery_voltage: float = 0.0
    battery_current: float = 0.0
    
    # Motor states
    motor_angles: Dict[str, float] = None
    motor_velocities: Dict[str, float] = None
    motor_torques: Dict[str, float] = None

class RobotStateManager:
    def __init__(self, network_interface: str):
        """Initialize robot state manager
        
        Args:
            network_interface: Network interface name (e.g. 'enp2s0')
        """
        # Initialize DDS communication
        ChannelFactoryInitialize(0, network_interface)
        
        # Initialize clients
        self.robot_state_client = RobotStateClient()
        self.sport_client = SportClient()
        
        # Initialize state subscriber
        self.state_subscriber = ChannelSubscriber(
            "rt/lowstate",
            unitree_go_msg_dds__LowState_(),
        )
        self.state_subscriber.Init(handler=self._state_callback)  # 正确注册回调


        # Initialize state storage
        self.state = RobotState()
        self._last_update = time.time()
        self._motor_id_map = {
            "FR_0": 0, "FR_1": 1, "FR_2": 2,  # Front right leg
            "FL_0": 3, "FL_1": 4, "FL_2": 5,  # Front left leg
            "RR_0": 6, "RR_1": 7, "RR_2": 8,  # Rear right leg
            "RL_0": 9, "RL_1": 10, "RL_2": 11,  # Rear left leg
            "FR_w": 12, "FL_w": 13,  # Front wheels
            "RR_w": 14, "RL_w": 15,  # Rear wheels
        }
        
        # Initialize motor state dictionaries
        self.state.motor_angles = {name: 0.0 for name in self._motor_id_map}
        self.state.motor_velocities = {name: 0.0 for name in self._motor_id_map}
        self.state.motor_torques = {name: 0.0 for name in self._motor_id_map}

    def _state_callback(self, msg: LowState_) -> None:
        """Update robot state from low state message"""
        self._last_update = time.time()
        
        # Update IMU states
        self.state.quaternion = (
            msg.imu_state.quaternion[0],
            msg.imu_state.quaternion[1],
            msg.imu_state.quaternion[2],
            msg.imu_state.quaternion[3]
        )
        self.state.rpy = (
            msg.imu_state.rpy[0],
            msg.imu_state.rpy[1],
            msg.imu_state.rpy[2]
        )
        self.state.accelerometer = (
            msg.imu_state.accelerometer[0],
            msg.imu_state.accelerometer[1],
            msg.imu_state.accelerometer[2]
        )
        self.state.gyroscope = (
            msg.imu_state.gyroscope[0],
            msg.imu_state.gyroscope[1],
            msg.imu_state.gyroscope[2]
        )
        
        # Update power states
        self.state.battery_voltage = msg.power_v
        self.state.battery_current = msg.power_a
        
        # Update motor states
        for name, idx in self._motor_id_map.items():
            self.state.motor_angles[name] = msg.motor_state[idx].q
            self.state.motor_velocities[name] = msg.motor_state[idx].dq
            self.state.motor_torques[name] = msg.motor_state[idx].tau_est
        
        # Update timestamp
        self.state.timestamp = time.time()

    def get_state_dict(self) -> Dict[str, Any]:
        """Get current robot state as dictionary"""
        return {
            "system": {
                "is_active": self.state.is_active,
                "timestamp": self.state.timestamp,
                "last_update": self._last_update
            },
            "imu": {
                "quaternion": self.state.quaternion,
                "rpy": self.state.rpy,
                "acceleration": self.state.acceleration,
                "angular_velocity": self.state.angular_velocity
            },
            "motion": {
                "position": self.state.position,
                "velocity": self.state.velocity
            },
            "power": {
                "battery_voltage": self.state.battery_voltage,
                "battery_current": self.state.battery_current
            },
            "motors": {
                "angles": self.state.motor_angles,
                "velocities": self.state.motor_velocities,
                "torques": self.state.motor_torques
            }
        }

    def is_connected(self) -> bool:
        """Check if robot state is being updated"""
        return (time.time() - self._last_update) < 1.0  # Consider stale after 1 second

if __name__ == "__main__":
    # Initialize robot state manager
    robot = RobotStateManager("eth0")  # Replace with your network interface
    
    try:
        while True:
            # Get current state
            state = robot.get_state_dict()
            
            # Print some interesting values
            print(f"Robot connected: {robot.is_connected()}")
            print(f"Battery voltage: {state['power']['battery_voltage']:.2f}V")
            print(f"IMU Roll/Pitch/Yaw: {state['imu']['rpy']}")
            print(f"Front right hip angle: {state['motors']['angles']['FR_0']:.2f}")
            
            time.sleep(0.1)  # Update at 10Hz
            
    except KeyboardInterrupt:
        print("Shutting down...")