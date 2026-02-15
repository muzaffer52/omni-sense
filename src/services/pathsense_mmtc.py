"""
PathSense - mMTC V2X Spatial Navigation Service
Vision-impaired users navigate cities using IoT sensor network
"""

from typing import Dict, Any, List, Tuple
import random
import math
from loguru import logger

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.network.turkcell_5g import TurkcellNetwork, NetworkSliceType


class CityIoTDevice:
    """Represents a city IoT device broadcasting location data"""
    
    def __init__(self, device_id: str, device_type: str, location: Tuple[float, float]):
        self.device_id = device_id
        self.device_type = device_type  # bus, traffic_light, store, etc.
        self.location = location  # (latitude, longitude)
        self.broadcasting = True
    
    def get_broadcast_data(self) -> Dict[str, Any]:
        """Get V2X broadcast data"""
        return {
            "device_id": self.device_id,
            "type": self.device_type,
            "location": self.location,
            "timestamp": "2026-02-15T17:30:00",
            "network": "Turkcell 5G mMTC"
        }


class PathSenseService:
    """
    mMTC 5G Slice - V2X Spatial Navigation
    
    Enables vision-impaired users to navigate cities using:
    - City IoT network (buses, traffic lights, stores broadcasting)
    - GPS + WiFi triangulation
    - Spatial audio (3D sound guides user)
    
    Uses Turkcell 5G mMTC slice for massive device connectivity (1M devices/km²)
    """
    
    def __init__(self):
        self.service_name = "PathSense"
        
        # Allocate mMTC network slice
        self.network = TurkcellNetwork()
        self.network_slice = self.network.allocate_slice("PathSense")
        
        # mMTC capacity check
        assert self.network_slice.config["max_devices_per_km2"] >= 1000000, "mMTC capacity too low!"
        
        # Deploy city IoT infrastructure
        self.city_devices = self._deploy_city_iot()
        
        # Navigation state
        self.gps_mode = "standard"  # standard, wifi_triangulation, beacon
        self.gps_accuracy = 1.0  # 0.0 (no signal) to 1.0 (perfect)
        self.audio_volume = 0.7
        
        # Metrics
        self.accuracy = 0.90
        self.latency_ms = 100
        
        logger.info(f"✅ {self.service_name} initialized (mMTC)")
        logger.info(f"   City IoT devices: {len(self.city_devices)}")
        logger.info(f"   Network capacity: {self.network_slice.config['max_devices_per_km2']:,} devices/km²")
    
    def _deploy_city_iot(self) -> List[CityIoTDevice]:
        """Deploy city-wide IoT sensor network"""
        devices = []
        
        # Istanbul city center simulation
        base_lat, base_lon = 41.0082, 28.9784  # Istanbul
        
        # 500 buses
        for i in range(500):
            lat = base_lat + random.uniform(-0.1, 0.1)
            lon = base_lon + random.uniform(-0.1, 0.1)
            devices.append(CityIoTDevice(f"BUS-{i:03d}", "bus", (lat, lon)))
        
        # 2000 traffic lights
        for i in range(2000):
            lat = base_lat + random.uniform(-0.15, 0.15)
            lon = base_lon + random.uniform(-0.15, 0.15)
            devices.append(CityIoTDevice(f"TL-{i:04d}", "traffic_light", (lat, lon)))
        
        # 1000 smart stores
        for i in range(1000):
            lat = base_lat + random.uniform(-0.08, 0.08)
            lon = base_lon + random.uniform(-0.08, 0.08)
            devices.append(CityIoTDevice(f"STORE-{i:03d}", "store", (lat, lon)))
        
        logger.info(f"   📍 Deployed: {len(devices)} IoT devices")
        return devices
    
    def get_spatial_audio_guidance(self, user_location: Tuple[float, float]) -> List[Dict[str, Any]]:
        """
        Get 3D spatial audio navigation cues
        
        Args:
            user_location: (latitude, longitude)
            
        Returns:
            List of audio cues with direction and distance
        """
        nearby_devices = self._query_nearby_iot(user_location, radius_m=50)
        
        audio_cues = []
        for device in nearby_devices:
            direction = self._calculate_direction(user_location, device.location)
            distance = self._calculate_distance(user_location, device.location)
            
            # Generate spatial audio cue
            audio_cue = {
                "device_type": device.device_type,
                "text": self._generate_text_cue(device.device_type, distance, direction),
                "audio_channel": direction,  # "left", "right", "front", "back"
                "volume": min(1.0, self.audio_volume / (distance + 1)),
                "distance_m": distance,
                "direction": direction
            }
            audio_cues.append(audio_cue)
        
        logger.debug(f"   🎧 Spatial audio: {len(audio_cues)} cues generated")
        return audio_cues
    
    def _query_nearby_iot(self, user_location: Tuple[float, float], radius_m: int) -> List[CityIoTDevice]:
        """Query nearby IoT devices using mMTC network"""
        nearby = []
        for device in self.city_devices:
            distance = self._calculate_distance(user_location, device.location)
            if distance <= radius_m:
                nearby.append(device)
        
        return nearby[:10]  # Limit to 10 nearest
    
    def _calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate distance in meters (simplified)"""
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        # Simplified distance calculation
        dlat = abs(lat2 - lat1)
        dlon = abs(lon2 - lon1)
        distance_km = math.sqrt(dlat**2 + dlon**2) * 111  # 1 degree ≈ 111km
        return distance_km * 1000  # Convert to meters
    
    def _calculate_direction(self, from_loc: Tuple[float, float], to_loc: Tuple[float, float]) -> str:
        """Calculate cardinal direction"""
        lat1, lon1 = from_loc
        lat2, lon2 = to_loc
        
        if lon2 > lon1:
            return "right" if abs(lon2 - lon1) > abs(lat2 - lat1) else "front"
        else:
            return "left" if abs(lon2 - lon1) > abs(lat2 - lat1) else "back"
    
    def _generate_text_cue(self, device_type: str, distance: float, direction: str) -> str:
        """Generate spoken navigation cue"""
        type_names = {
            "bus": "Otobüs",
            "traffic_light": "Trafik lambası",
            "store": "Mağaza"
        }
        
        direction_names = {
            "left": "solunuzda",
            "right": "sağınızda",
            "front": "önünüzde",
            "back": "arkanızda"
        }
        
        return f"{type_names.get(device_type, device_type)} {distance:.0f} metre {direction_names.get(direction, direction)}"
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get service quality metrics"""
        # Calculate accuracy based on GPS quality
        gps_penalty = (1.0 - self.gps_accuracy) * 0.5
        self.accuracy = max(0.1, min(1.0, 0.95 - gps_penalty))
        
        return {
            "service": self.service_name,
            "accuracy": self.accuracy,
            "latency_ms": self.latency_ms,
            "error_rate": 1.0 - self.accuracy,
            "confidence": self.accuracy,
            "gps_mode": self.gps_mode,
            "gps_signal": self.gps_accuracy,
            "network_slice": "mMTC",
            "active_devices": len(self.city_devices)
        }
    
    def inject_scenario(self, scenario: str):
        """Inject quality degradation scenario"""
        if scenario == "gps_drift_indoor":
            self.gps_accuracy = 0.3
            logger.warning(f"⚠️ {self.service_name}: GPS drift (indoor) injected")
        elif scenario == "network_congestion":
            self.latency_ms = 250
            logger.warning(f"⚠️ {self.service_name}: Network congestion")
        elif scenario == "normal":
            self.gps_accuracy = 1.0
            self.latency_ms = 100
            logger.info(f"✅ {self.service_name}: Normal conditions restored")
    
    def apply_action(self, action_id: str) -> bool:
        """Apply optimization action"""
        if action_id == "wifi_triangulation":
            self.gps_mode = "wifi_triangulation"
            self.gps_accuracy = min(1.0, self.gps_accuracy + 0.4)
            logger.info(f"📡 {self.service_name}: WiFi triangulation enabled")
            return True
        elif action_id == "increase_audio":
            self.audio_volume = min(1.0, self.audio_volume + 0.2)
            logger.info(f"🔊 {self.service_name}: Audio volume → {self.audio_volume:.1f}")
            return True
        else:
            return False
