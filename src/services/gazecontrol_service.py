"""
Omni-Sense - GazeControl Service Simulator
Simulates eye-tracking IoT control service for motor-impaired users.
"""

import random
import time
from typing import Dict, Any
from loguru import logger


class GazeControlService:
    """
    GazeControl Service: Eye-Tracking IoT Control
    
    Simulates an eye-tracking system that allows motor-impaired users
    to control IoT devices (lights, wheelchair, phone) using only eye movements.
    """
    
    def __init__(self):
        self.service_name = "GazeControl"
        self.is_running = True
        
        # Current state
        self.current_accuracy = 0.92
        self.current_latency = 30  # ms
        self.current_error_rate = 0.08
        
        # Eye-tracking settings (controllable by Execution Agent)
        self.calibrated = True
        self.dwell_time_ms = 800  # Time to confirm selection
        self.tracking_sensitivity = 0.8  # 0.0 (low) to 1.0 (high)
        
        # User state (can drift for scenarios)
        self.head_position_drift = 0.0  # 0.0 (perfect) to 1.0 (completely off)
        self.eye_fatigue_level = 0.0  # 0.0 (fresh) to 1.0 (exhausted)
        
        logger.info(f"✅ GazeControl service initialized")
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current service quality metrics."""
        # Calculate accuracy based on calibration and user state
        base_accuracy = 0.95 if self.calibrated else 0.6
        
        # Head position drift impact
        drift_penalty = self.head_position_drift * 0.4  # Max 40% penalty
        
        # Fatigue impact
        fatigue_penalty = self.eye_fatigue_level * 0.3  # Max 30% penalty
        
        # Sensitivity compensation (higher = more reactive but less stable)
        sensitivity_bonus = (self.tracking_sensitivity - 0.5) * 0.1
        
        # Calculate final accuracy
        self.current_accuracy = max(0.1, min(1.0,
            base_accuracy - drift_penalty - fatigue_penalty + sensitivity_bonus
        ))
        
        # Latency increases with lower dwell time
        self.current_latency = 800 - self.dwell_time_ms + 30
        
        # Error rate inversely related to accuracy
        self.current_error_rate = 1.0 - self.current_accuracy
        
        return {
            "service": self.service_name,
            "accuracy": self.current_accuracy,
            "latency_ms": self.current_latency,
            "error_rate": self.current_error_rate,
            "confidence": self.current_accuracy,
            "calibrated": self.calibrated,
            "dwell_time_ms": self.dwell_time_ms,
            "head_drift": self.head_position_drift,
            "fatigue": self.eye_fatigue_level
        }
    
    def inject_scenario(self, scenario: str):
        """Inject quality degradation scenario."""
        if scenario == "position_drift":
            self.head_position_drift = 0.7
            logger.warning(f"⚠️ GazeControl: Head position drift scenario injected")
        
        elif scenario == "eye_fatigue":
            self.eye_fatigue_level = 0.6
            logger.warning(f"⚠️ GazeControl: Eye fatigue scenario injected")
        
        elif scenario == "calibration_lost":
            self.calibrated = False
            logger.warning(f"⚠️ GazeControl: Calibration lost scenario injected")
        
        elif scenario == "normal":
            self.head_position_drift = 0.0
            self.eye_fatigue_level = 0.0
            self.calibrated = True
            logger.info(f"✅ GazeControl: Normal conditions restored")
    
    def apply_action(self, action_id: str) -> bool:
        """Apply optimization action from Execution Agent."""
        if action_id == "recalibrate":
            self.calibrated = True
            self.head_position_drift = 0.0  # Reset drift after recalibration
            logger.info(f"🎯 GazeControl: Recalibration completed")
            return True
        
        elif action_id == "increase_dwell":
            self.dwell_time_ms = min(1500, self.dwell_time_ms + 200)
            logger.info(f"⏱️ GazeControl: Dwell time increased to {self.dwell_time_ms}ms")
            return True
        
        elif action_id == "adjust_sensitivity":
            self.tracking_sensitivity = max(0.3, self.tracking_sensitivity - 0.2)
            logger.info(f"🎚️ GazeControl: Sensitivity reduced to {self.tracking_sensitivity:.1f}")
            return True
        
        elif action_id == "simplify_ui":
            logger.info(f"🔲 GazeControl: UI simplified (larger targets)")
            return True
        
        else:
            logger.warning(f"❌ GazeControl: Unknown action {action_id}")
            return False
