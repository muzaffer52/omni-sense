"""
Turkcell 5G Network Layer
Simulates 5G network slicing: eMBB, URLLC, mMTC
"""

from typing import Dict, Any, Optional
from loguru import logger
from enum import Enum


class NetworkSliceType(Enum):
    """5G Network Slice Types"""
    EMBB = "eMBB"  # Enhanced Mobile Broadband
    URLLC = "URLLC"  # Ultra-Reliable Low Latency Communications
    MMTC = "mMTC"  # Massive Machine-Type Communications


class NetworkSlice:
    """Represents a 5G network slice with QoS guarantees"""
    
    def __init__(self, slice_type: NetworkSliceType, config: Dict[str, Any]):
        self.type = slice_type
        self.config = config
        
    def __repr__(self):
        return f"<NetworkSlice {self.type.value}: {self.config}>"


class TurkcellNetwork:
    """
    Turkcell 5G Network Infrastructure
    
    Provides network slicing for different service requirements:
    - eMBB: High bandwidth for AR/VR (BiP-AR sign language)
    - URLLC: Ultra-low latency for safety-critical (eye-tracking IoT)
    - mMTC: Massive IoT connections (V2X city sensors)
    """
    
    def __init__(self):
        self.operator_name = "Turkcell"
        self.technology = "5G SA (Standalone)"
        self.coverage_cities = ["Istanbul", "Ankara", "Izmir", "Antalya"]
        
        # Define network slices
        self.slices = {
            NetworkSliceType.EMBB: NetworkSlice(
                NetworkSliceType.EMBB,
                {
                    "bandwidth_gbps": 1.0,
                    "latency_ms": 10,
                    "jitter_ms": 2,
                    "packet_loss_rate": 0.001,
                    "use_cases": ["BiP-AR Video Calls", "HD Avatar Rendering", "360° Video"],
                    "frequency_band": "3.5 GHz (C-Band)",
                    "modulation": "256-QAM"
                }
            ),
            NetworkSliceType.URLLC: NetworkSlice(
                NetworkSliceType.URLLC,
                {
                    "bandwidth_mbps": 100,
                    "latency_ms": 1,
                    "jitter_ms": 0.1,
                    "reliability": 0.99999,  # Five 9s
                    "packet_loss_rate": 0.00001,
                    "use_cases": ["Eye-Tracking IoT Control", "Wheelchair Control", "Emergency Response"],
                    "frequency_band": "28 GHz (mmWave)",
                    "priority": "CRITICAL"
                }
            ),
            NetworkSliceType.MMTC: NetworkSlice(
                NetworkSliceType.MMTC,
                {
                    "max_devices_per_km2": 1000000,
                    "bandwidth_kbps_per_device": 10,
                    "latency_ms": 100,
                    "battery_life_years": 10,
                    "use_cases": ["V2X City Sensors", "Traffic Lights", "Bus Fleet Management", "Smart Stores"],
                    "frequency_band": "700 MHz (Sub-6)",
                    "connection_density": "Ultra-high"
                }
            )
        }
        
        logger.info(f"📡 {self.operator_name} 5G Network initialized")
        logger.info(f"   Technology: {self.technology}")
        logger.info(f"   Available Slices: {len(self.slices)}")
    
    def allocate_slice(self, service_type: str) -> NetworkSlice:
        """
        Allocate appropriate network slice for service
        
        Args:
            service_type: "BiP-AR", "GazeControl", or "PathSense"
            
        Returns:
            NetworkSlice with QoS guarantees
        """
        slice_mapping = {
            "BiP-AR": NetworkSliceType.EMBB,
            "GazeControl": NetworkSliceType.URLLC,
            "PathSense": NetworkSliceType.MMTC
        }
        
        slice_type = slice_mapping.get(service_type)
        if not slice_type:
            raise ValueError(f"Unknown service type: {service_type}")
        
        allocated_slice = self.slices[slice_type]
        
        logger.info(f"✅ Network slice allocated: {slice_type.value} for {service_type}")
        logger.info(f"   Bandwidth: {allocated_slice.config.get('bandwidth_gbps', allocated_slice.config.get('bandwidth_mbps', 'N/A'))}")
        logger.info(f"   Latency: {allocated_slice.config['latency_ms']}ms")
        
        return allocated_slice
    
    def get_slice_info(self, slice_type: NetworkSliceType) -> Dict[str, Any]:
        """Get detailed information about a network slice"""
        slice_obj = self.slices.get(slice_type)
        if not slice_obj:
            return {}
        
        return {
            "type": slice_type.value,
            "config": slice_obj.config,
            "operator": self.operator_name
        }
    
    def measure_qos(self, slice_type: NetworkSliceType) -> Dict[str, float]:
        """
        Measure Quality of Service metrics for a slice
        
        Returns:
            Real-time QoS measurements
        """
        import random
        
        slice_config = self.slices[slice_type].config
        
        # Simulate real-time measurements (slight variance from guaranteed QoS)
        if slice_type == NetworkSliceType.EMBB:
            return {
                "bandwidth_gbps": slice_config["bandwidth_gbps"] * random.uniform(0.95, 1.0),
                "latency_ms": slice_config["latency_ms"] * random.uniform(0.9, 1.1),
                "packet_loss_rate": slice_config["packet_loss_rate"] * random.uniform(0.5, 1.5)
            }
        elif slice_type == NetworkSliceType.URLLC:
            return {
                "latency_ms": slice_config["latency_ms"] * random.uniform(0.8, 1.0),  # Always under guarantee
                "reliability": slice_config["reliability"],
                "jitter_ms": slice_config["jitter_ms"] * random.uniform(0.5, 1.0)
            }
        else:  # mMTC
            return {
                "active_connections": random.randint(50000, 100000),
                "latency_ms": slice_config["latency_ms"] * random.uniform(0.9, 1.2),
                "connection_success_rate": 0.999
            }
