"""
Omni-Sense - SignLink Service Simulator
Simulates sign language translation service with quality metrics.
"""

import random
import time
from typing import Dict, Any
from loguru import logger


class SignLinkService:
    """
    SignLink Service: AR Sign Language Translation
    
    Simulates a sign language translation service that can degrade
    based on environmental conditions (lighting, occlusion, etc.)
    """
    
    def __init__(self):
        self.service_name = "SignLink"
        self.is_running = True
        
        # Current state
        self.current_accuracy = 0.95
        self.current_latency = 50  # ms
        self.current_error_rate = 0.02
        
        # Camera settings (controllable by Execution Agent)
        self.camera_iso = 400
        self.camera_mode = "auto"  # auto, night, manual
        self.camera_source = "back"  # back, front
        
        # Environment (can be degraded for scenarios)
        self.lighting_level = 1.0  # 0.0 (dark) to 1.0 (bright)
        self.occlusion_level = 0.0  # 0.0 (clear) to 1.0 (fully occluded)
        
        logger.info(f"✅ SignLink service initialized")
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current service quality metrics."""
        # Calculate accuracy based on environment and settings
        base_accuracy = 0.95
        
        # Lighting impact
        lighting_penalty = (1.0 - self.lighting_level) * 0.4  # Max 40% penalty
        
        # Occlusion impact  
        occlusion_penalty = self.occlusion_level * 0.5  # Max 50% penalty
        
        # ISO compensation (higher ISO helps in low light)
        iso_bonus = min((self.camera_iso - 400) / 1600, 0.2)  # Max 20% bonus
        
        # Night mode bonus
        mode_bonus = 0.15 if self.camera_mode == "night" else 0.0
        
        # Calculate final accuracy
        self.current_accuracy = max(0.1, min(1.0,
            base_accuracy - lighting_penalty - occlusion_penalty + iso_bonus + mode_bonus
        ))
        
        # Latency increases with higher ISO
        self.current_latency = 50 + (self.camera_iso - 400) / 10
        
        # Error rate inversely related to accuracy
        self.current_error_rate = 1.0 - self.current_accuracy
        
        return {
            "service": self.service_name,
            "accuracy": self.current_accuracy,
            "latency_ms": self.current_latency,
            "error_rate": self.current_error_rate,
            "confidence": self.current_accuracy,
            "camera_iso": self.camera_iso,
            "camera_mode": self.camera_mode,
            "lighting": self.lighting_level,
            "occlusion": self.occlusion_level
        }
    
    def inject_scenario(self, scenario: str):
        """Inject quality degradation scenario."""
        if scenario == "poor_lighting":
            self.lighting_level = 0.3
            logger.warning(f"⚠️ SignLink: Poor lighting scenario injected")
        
        elif scenario == "hand_occlusion":
            self.occlusion_level = 0.6
            logger.warning(f"⚠️ SignLink: Hand occlusion scenario injected")
        
        elif scenario == "normal":
            self.lighting_level = 1.0
            self.occlusion_level = 0.0
            logger.info(f"✅ SignLink: Normal conditions restored")
    
    def apply_action(self, action_id: str) -> bool:
        """Apply optimization action from Execution Agent."""
        if action_id == "adjust_iso":
            self.camera_iso = min(3200, self.camera_iso + 800)
            logger.info(f"📸 SignLink: ISO increased to {self.camera_iso}")
            return True
        
        elif action_id == "night_mode":
            self.camera_mode = "night"
            logger.info(f"🌙 SignLink: Night mode activated")
            return True
        
        elif action_id == "switch_camera":
            self.camera_source = "front" if self.camera_source == "back" else "back"
            logger.info(f"🔄 SignLink: Switched to {self.camera_source} camera")
            return True
        
        elif action_id == "reduce_resolution":
            logger.info(f"📉 SignLink: Resolution reduced for performance")
            return True
        
        else:
            logger.warning(f"❌ SignLink: Unknown action {action_id}")
            return False
