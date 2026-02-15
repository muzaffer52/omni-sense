"""
GazeControl - URLLC Eye-Tracking IoT Control Service
Motor-impaired users control devices with eyes only (1ms latency guarantee)
"""

from typing import Dict, Any, List
import time
import random
from loguru import logger

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.network.turkcell_5g import TurkcellNetwork, NetworkSliceType


class IoTDevice:
    """Represents an IoT device controllable via eye-tracking"""
    
    def __init__(self, device_id: str, device_type: str, critical: bool = False):
        self.device_id = device_id
        self.device_type = device_type  # wheelchair, light, tv, door, etc.
        self.critical = critical  # safety-critical devices need URLLC
        self.state = "off"
        self.last_command_time = 0
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute command on device"""
        self.state = command
        self.last_command_time = time.time()
        
        return {
            "device_id": self.device_id,
            "type": self.device_type,
            "command": command,
            "success": True,
            "timestamp": self.last_command_time
        }


class GazeControlService:
    """
    URLLC 5G Slice - Eye-Tracking IoT Control
    
    Enables motor-impaired users to control devices using only eye movements.
    Uses Turkcell 5G URLLC slice for ultra-low latency (<1ms) and 99.999% reliability.
    
    Critical use cases:
    - Electric wheelchair control (delay = danger)
    - Emergency call button
    - Medical alert systems
    """
    
    def __init__(self):
        self.service_name = "GazeControl" 
        
        # Allocate URLLC network slice
        self.network = TurkcellNetwork()
        self.network_slice = self.network.allocate_slice("GazeControl")
        
        # URLLC requirements
        assert self.network_slice.config["latency_ms"] <= 1, "URLLC latency too high!"
        assert self.network_slice.config["reliability"] >= 0.99999, "URLLC reliability insufficient!"
        
        # Connected IoT devices
        self.devices = {
            "wheelchair": IoTDevice("WC-001", "wheelchair", critical=True),
            "lights_living": IoTDevice("LT-001", "light", critical=False),
            "lights_bedroom": IoTDevice("LT-002", "light", critical=False),
            "tv": IoTDevice("TV-001", "tv", critical=False),
            "door_lock": IoTDevice("DR-001", "lock", critical=True),
            "emergency_button": IoTDevice("EM-001", "emergency", critical=True)
        }
        
        # Eye-tracking state
        self.calibrated = True
        self.calibration_accuracy = 0.95
        self.dwell_time_ms = 800  # Time to confirm selection
        self.head_position_drift = 0.0  # 0.0 perfect, 1.0 completely off
        
        # Metrics
        self.accuracy = 0.92
        self.latency_ms = 0
        
        logger.info(f"✅ {self.service_name} initialized (URLLC)")
        logger.info(f"   Connected devices: {len(self.devices)}")
        logger.info(f"   Critical devices: {sum(1 for d in self.devices.values() if d.critical)}")
    
    def process_gaze_command(self, target_device_id: str, dwell_time_ms: int) -> Dict[str, Any]:
        """
        Process eye-tracking command
        
        Flow:
        1. User looks at device button
        2. Gaze detected and sent via 5G URLLC
        3. Device receives command within 1ms
        4. Device executes
        
        Args:
            target_device_id: Device to control
            dwell_time_ms: How long user looked at target
            
        Returns:
            Command execution result
        """
        start_time = time.time()
        
        device = self.devices.get(target_device_id)
        if not device:
            return {"success": False, "error": "Device not found"}
        
        # Check if dwell time sufficient
        if dwell_time_ms < self.dwell_time_ms:
            return {"success": False, "error": "Dwell time too short"}
        
        # Send command via appropriate network slice
        if device.critical:
            # URLLC: Guaranteed <1ms
            network_latency_ms = random.uniform(0.3, 0.8)
        else:
            # Regular slice: ~10ms acceptable
            network_latency_ms = random.uniform(5, 15)
        
        time.sleep(network_latency_ms / 1000)
        
        # Execute command
        result = device.execute_command("activate")
        
        total_latency = (time.time() - start_time) * 1000
        self.latency_ms = total_latency
        
        logger.info(f"⚡ Gaze command: {device.device_type} activated ({total_latency:.1f}ms)")
        if device.critical:
            logger.info(f"   🔒 URLLC: Latency {network_latency_ms:.2f}ms < 1ms ✅")
        
        return {
            "success": True,
            "device": device.device_type,
            "latency_ms": total_latency,
            "network_latency_ms": network_latency_ms,
            "network_slice": "URLLC" if device.critical else "eMBB",
            "reliability": self.network_slice.config["reliability"] if device.critical else 0.999
        }
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get service quality metrics"""
        # Calculate accuracy based on calibration and drift
        drift_penalty = self.head_position_drift * 0.4
        self.accuracy = max(0.1, min(1.0, self.calibration_accuracy - drift_penalty))
        
        return {
            "service": self.service_name,
            "accuracy": self.accuracy,
            "latency_ms": self.latency_ms,
            "error_rate": 1.0 - self.accuracy,
            "confidence": self.accuracy,
            "calibrated": self.calibrated,
            "head_drift": self.head_position_drift,
            "network_slice": "URLLC",
            "connected_devices": len(self.devices)
        }
    
    def inject_scenario(self, scenario: str):
        """Inject quality degradation scenario"""
        if scenario == "position_drift":
            self.head_position_drift = 0.7
            logger.warning(f"⚠️ {self.service_name}: Head position drift injected")
        elif scenario == "calibration_lost":
            self.calibrated = False
            self.calibration_accuracy = 0.5
            logger.warning(f"⚠️ {self.service_name}: Calibration lost")
        elif scenario == "normal":
            self.head_position_drift = 0.0
            self.calibrated = True
            self.calibration_accuracy = 0.95
            logger.info(f"✅ {self.service_name}: Normal conditions restored")
    
    def apply_action(self, action_id: str) -> bool:
        """Apply optimization action"""
        if action_id == "recalibrate":
            self.calibrated = True
            self.calibration_accuracy = 0.95
            self.head_position_drift = 0.0
            logger.info(f"🎯 {self.service_name}: Recalibration completed")
            return True
        elif action_id == "increase_dwell":
            self.dwell_time_ms = min(1500, self.dwell_time_ms + 200)
            logger.info(f"⏱️ {self.service_name}: Dwell time → {self.dwell_time_ms}ms")
            return True
        else:
            return False
