"""
Omni-Sense - PathSense Service Simulator
Simulates V2X spatial navigation service for vision-impaired users.
"""

import random
import time
from typing import Dict, Any
from loguru import logger


class PathSenseService:
    """
    PathSense Service: V2X Spatial Navigation
    
    Simulates a spatial audio navigation system that uses city IoT infrastructure
    (buses, traffic lights, stores) to guide vision-impaired users.
    """
    
    def __init__(self):
        self.service_name = "PathSense"
        self.is_running = True
        
        # Current state
        self.current_accuracy = 0.90
        self.current_latency = 100  # ms
        self.current_error_rate = 0.10
        
        # Navigation settings (controllable by Execution Agent)
        self.gps_mode = "standard"  # standard, wifi_triangulation, beacon
        self.audio_volume = 0.7  # 0.0 to 1.0
        self.instruction_complexity = "detailed"  # simple, detailed
        
        # Environment (can degrade for scenarios)
        self.gps_accuracy = 1.0  # 1.0 (perfect) to 0.0 (no signal)
        self.iot_coverage = 1.0  # 1.0 (full coverage) to 0.0 (no devices)
        self.obstacle_detection = 1.0  # 1.0 (all seen) to 0.0 (blind)
        
        logger.info(f"✅ PathSense service initialized")
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current service quality metrics."""
        # Calculate accuracy based on GPS and IoT coverage
        base_accuracy = 0.95
        
        # GPS accuracy impact
        gps_penalty = (1.0 - self.gps_accuracy) * 0.5  # Max 50% penalty
        
        # IoT coverage impact
        iot_penalty = (1.0 - self.iot_coverage) * 0.3  # Max 30% penalty
        
        # Obstacle detection impact
        obstacle_penalty = (1.0 - self.obstacle_detection) * 0.4  # Max 40% penalty
        
        # WiFi triangulation bonus when GPS poor
        if self.gps_mode == "wifi_triangulation" and self.gps_accuracy < 0.5:
            mode_bonus = 0.25
        elif self.gps_mode == "beacon":
            mode_bonus = 0.15
        else:
            mode_bonus = 0.0
        
        # Simple instructions are more reliable
        complexity_bonus = 0.1 if self.instruction_complexity == "simple" else 0.0
        
        # Calculate final accuracy
        self.current_accuracy = max(0.1, min(1.0,
            base_accuracy - gps_penalty - iot_penalty - obstacle_penalty + mode_bonus + complexity_bonus
        ))
        
        # Latency varies by mode
        if self.gps_mode == "wifi_triangulation":
            self.current_latency = 150
        elif self.gps_mode == "beacon":
            self.current_latency = 80
        else:
            self.current_latency = 100
        
        # Error rate inversely related to accuracy
        self.current_error_rate = 1.0 - self.current_accuracy
        
        return {
            "service": self.service_name,
            "accuracy": self.current_accuracy,
            "latency_ms": self.current_latency,
            "error_rate": self.current_error_rate,
            "confidence": self.current_accuracy,
            "gps_mode": self.gps_mode,
            "audio_volume": self.audio_volume,
            "gps_signal": self.gps_accuracy,
            "iot_coverage": self.iot_coverage
        }
    
    def inject_scenario(self, scenario: str):
        """Inject quality degradation scenario."""
        if scenario == "gps_drift_indoor":
            self.gps_accuracy = 0.3
            logger.warning(f"⚠️ PathSense: GPS drift (indoor) scenario injected")
        
        elif scenario == "low_iot_coverage":
            self.iot_coverage = 0.4
            logger.warning(f"⚠️ PathSense: Low IoT coverage scenario injected")
        
        elif scenario == "obstacle_occlusion":
            self.obstacle_detection = 0.5
            logger.warning(f"⚠️ PathSense: Obstacle occlusion scenario injected")
        
        elif scenario == "normal":
            self.gps_accuracy = 1.0
            self.iot_coverage = 1.0
            self.obstacle_detection = 1.0
            logger.info(f"✅ PathSense: Normal conditions restored")
    
    def apply_action(self, action_id: str) -> bool:
        """Apply optimization action from Execution Agent."""
        if action_id == "wifi_triangulation":
            self.gps_mode = "wifi_triangulation"
            logger.info(f"📡 PathSense: Switched to WiFi triangulation mode")
            return True
        
        elif action_id == "simplify_path":
            self.instruction_complexity = "simple"
            logger.info(f"🗺️ PathSense: Simplified navigation instructions")
            return True
        
        elif action_id == "increase_audio":
            self.audio_volume = min(1.0, self.audio_volume + 0.2)
            logger.info(f"🔊 PathSense: Audio volume increased to {self.audio_volume:.1f}")
            return True
        
        elif action_id == "request_update":
            logger.info(f"🔄 PathSense: Requested map data update")
            return True
        
        else:
            logger.warning(f"❌ PathSense: Unknown action {action_id}")
            return False
