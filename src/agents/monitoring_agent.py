"""
Omni-Sense Monitoring Agent - Service Quality Detection
Monitors accessibility service quality and detects degradation using ML.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import numpy as np
from sklearn.ensemble import IsolationForest
from loguru import logger
from dotenv import load_dotenv

from .base_agent import BaseAgent

load_dotenv()


class MonitoringAgent(BaseAgent):
    """
    Monitoring Agent: Observes accessibility service quality and detects degradation.
    
    Responsibilities:
    - Continuous service quality monitoring (SignLink, GazeControl, PathSense)
    - Degradation detection using Isolation Forest
    - Alert generation when quality drops
    - Event publishing for downstream agents
    """
    
    def __init__(self):
        super().__init__(
            name="Monitoring Agent",
            description="Real-time accessibility service quality monitoring and degradation detection"
        )
        
        # Service quality thresholds
        self.quality_threshold = float(os.getenv('QUALITY_THRESHOLD', 0.8))
        self.window_size = int(os.getenv('MONITORING_WINDOW_SIZE', 50))
        
        # Anomaly detector model
        self.anomaly_detector = IsolationForest(
            contamination=0.15,  # Expect 15% quality issues
            random_state=42,
            n_estimators=100
        )
        
        self.model_trained = False
        self.detected_issues: List[Dict] = []
        self.quality_history: List[Dict] = []
        
        logger.info(f"✅ [{self.name}] Initialized with quality threshold: {self.quality_threshold}")
    
    def perceive(self) -> Dict[str, Any]:
        """
        Monitor current service quality metrics.
        
        Returns:
            Dict containing quality metrics for all active services
        """
        # In real implementation, this would poll actual service metrics
        # For now, we'll use simulated data
        
        current_metrics = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Each service reports its quality metrics
        # These would come from actual service monitors in production
        
        logger.info(f"📊 [{self.name}] Retrieved service metrics")
        
        return current_metrics
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze service quality and detect degradation.
        
        Args:
            perception: Current service metrics
            
        Returns:
            Dict containing analysis results and detected issues
        """
        if not perception.get("services"):
            return {
                "analysis_performed": False,
                "reason": "no_active_services"
            }
        
        # Direct issue detection based on metrics
        issues_detected = []
        
        for service_name, service_data in perception.get("services", {}).items():
            # Check accuracy
            if "accuracy" in service_data:
                if service_data["accuracy"] < self.quality_threshold:
                    issues_detected.append({
                        "service": service_name,
                        "metric": "accuracy",
                        "value": service_data["accuracy"],
                        "threshold": self.quality_threshold,
                        "severity": "CRITICAL" if service_data["accuracy"] < 0.5 else "WARNING",
                        "description": f"Service accuracy below threshold"
                    })
        
        return {
            "analysis_performed": True,
            "issues_detected": len(issues_detected) > 0,
            "issues": issues_detected,
            "timestamp": perception["timestamp"]
        }
    
    def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate alerts for detected quality issues.
        
        Args:
            reasoning: Analysis results from reason()
            
        Returns:
            Dict containing alert information
        """
        if not reasoning.get("issues_detected"):
            return {
                "action": "no_alert",
                "status": "healthy"
            }
        
        issues = reasoning.get("issues", [])
        
        # Generate alert for each issue
        for issue in issues:
            alert = {
                "alert_id": f"QUALITY_{datetime.now().timestamp()}",
                "timestamp": reasoning["timestamp"],
                "service": issue["service"],
                "severity": issue["severity"],
                "metric": issue["metric"],
                "value": issue["value"],
                "threshold": issue["threshold"],
                "description": issue["description"]
            }
            
            self.detected_issues.append(alert)
            
            severity_emoji = "🔴" if issue["severity"] == "CRITICAL" else "🟡"
            logger.warning(
                f"{severity_emoji} [{self.name}] QUALITY ISSUE DETECTED\\n"
                f"   Service: {issue['service']}\\n"
                f"   Problem: {issue['description']}\\n"
                f"   Metric: {issue['metric']} = {issue['value']:.2f} (threshold: {issue['threshold']:.2f})"
            )
        
        return {
            "action": "alert_generated",
            "alerts": issues,
            "count": len(issues)
        }
    
    def _extract_quality_features(self, metrics: Dict[str, Any]) -> List[float]:
        """Extract numerical features for anomaly detection."""
        features = []
        
        for service_name, service_data in metrics.get("services", {}).items():
            # Extract relevant quality metrics
            if "accuracy" in service_data:
                features.append(service_data["accuracy"])
            if "latency_ms" in service_data:
                features.append(service_data["latency_ms"])
            if "confidence" in service_data:
                features.append(service_data["confidence"])
            if "error_rate" in service_data:
                features.append(service_data["error_rate"])
        
        return features if features else []
    
    def _train_anomaly_detector(self):
        """Train the Isolation Forest model on historical data."""
        if len(self.quality_history) < self.window_size:
            return
        
        # Prepare training data
        X = np.array([h["features"] for h in self.quality_history[-self.window_size:]])
        
        if X.shape[0] > 0 and X.shape[1] > 0:
            self.anomaly_detector.fit(X)
            self.model_trained = True
            logger.info(f"✅ [{self.name}] Anomaly detector trained on {X.shape[0]} samples")
    
    def _detect_anomaly(self, features: List[float]) -> bool:
        """Detect if current features indicate an anomaly."""
        if not self.model_trained or not features:
            return False
        
        X = np.array([features])
        prediction = self.anomaly_detector.predict(X)
        
        # Isolation Forest returns -1 for anomalies, 1 for normal
        return prediction[0] == -1
    
    def _identify_specific_issues(self, features: List[float], metrics: Dict[str, Any]) -> List[Dict]:
        """Identify specific quality issues from detected anomaly."""
        issues = []
        
        # Analyze each service
        for service_name, service_data in metrics.get("services", {}).items():
            # Check accuracy
            if "accuracy" in service_data:
                if service_data["accuracy"] < self.quality_threshold:
                    issues.append({
                        "service": service_name,
                        "metric": "accuracy",
                        "value": service_data["accuracy"],
                        "threshold": self.quality_threshold,
                        "severity": "CRITICAL" if service_data["accuracy"] < 0.5 else "WARNING",
                        "description": f"Service accuracy below threshold"
                    })
            
            # Check latency
            if "latency_ms" in service_data:
                if service_data["latency_ms"] > 500:  # 500ms threshold
                    issues.append({
                        "service": service_name,
                        "metric": "latency",
                        "value": service_data["latency_ms"],
                        "threshold": 500,
                        "severity": "WARNING",
                        "description": f"High latency detected"
                    })
            
            # Check error rate
            if "error_rate" in service_data:
                if service_data["error_rate"] > 0.1:  # 10% error threshold
                    issues.append({
                        "service": service_name,
                        "metric": "error_rate",
                        "value": service_data["error_rate"],
                        "threshold": 0.1,
                        "severity": "CRITICAL",
                        "description": f"High error rate detected"
                    })
        
        return issues
    
    def get_latest_alerts(self) -> List[Dict]:
        """Get recent quality alerts."""
        return self.detected_issues[-10:]  # Return last 10 alerts
