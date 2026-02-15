"""
Omni-Sense Decision Agent - Intelligent Action Selection
Decides optimal actions to restore accessibility service quality.
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger
from dotenv import load_dotenv

from .base_agent import BaseAgent

load_dotenv()


class DecisionAgent(BaseAgent):
    """
    Decision Agent: Selects optimal actions to fix accessibility service issues.
    
    Responsibilities:
    - Receive incident reports from Root Cause Agent
    - Evaluate possible actions
    - Assess risks and trade-offs
    - Generate safe action plans
    """
    
    def __init__(self):
        super().__init__(
            name="Decision Agent",
            description="Intelligent decision-making for service optimization"
        )
        
        # Service action catalog
        self.action_catalog = self._build_action_catalog()
        
        # Pending incidents to decide on
        self.pending_incidents: List[Dict] = []
        self.decision_history: List[Dict] = []
        
        logger.info(f"✅ [{self.name}] Initialized with {len(self.action_catalog)} action types")
    
    def receive_incident(self, incident_report: Dict[str, Any]):
        """Receive incident report from Root Cause Agent."""
        self.pending_incidents.append(incident_report)
        logger.info(f"📥 [{self.name}] Received incident for {incident_report.get('service')}")
    
    def perceive(self) -> Dict[str, Any]:
        """
        Get current incident to decide on.
        
        Returns:
            Dict containing incident information
        """
        if not self.pending_incidents:
            return {"has_incidents": False}
        
        incident = self.pending_incidents[0]
        
        return {
            "has_incidents": True,
            "incident": incident,
            "service": incident["service"],
            "root_cause": incident["root_cause"],
            "recommendations": incident["recommendations"]
        }
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select optimal actions based on diagnosis.
        
        Args:
            perception: Incident information
            
        Returns:
            Dict containing action plan with risk assessment
        """
        if not perception.get("has_incidents"):
            return {
                "decision_made": False,
                "reason": "no_pending_incidents"
            }
        
        incident = perception.get("incident", {})
        service = perception.get("service")
        recommendations = perception.get("recommendations", [])
        
        # Map recommendations to specific actions
        actions = self._select_actions(service, recommendations)
        
        # Assess risk for each action
        risk_score = self._assess_risk(actions)
        
        # Build action plan
        action_plan = {
            "service": service,
            "actions": actions,
            "risk_score": risk_score,
            "risk_level": "LOW" if risk_score < 0.3 else "MEDIUM" if risk_score < 0.7 else "HIGH",
            "requires_approval": risk_score > 0.7,
            "estimated_impact": "Restore service quality to normal levels"
        }
        
        logger.info(
            f"🎯 [{self.name}] DECISION MADE\\n"
            f"   Service: {service}\\n"
            f"   Actions: {len(actions)}\\n"
            f"   Risk: {action_plan['risk_level']}"
        )
        
        return {
            "decision_made": True,
            "action_plan": action_plan,
            "timestamp": datetime.now().isoformat()
        }
    
    def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish action plan for execution.
        
        Args:
            reasoning: Action plan from reason()
            
        Returns:
            Dict containing published plan
        """
        if not reasoning.get("decision_made"):
            return {"action": "none"}
        
        action_plan = reasoning.get("action_plan")
        
        # Store in history
        self.decision_history.append({
            "timestamp": reasoning["timestamp"],
            "plan": action_plan
        })
        
        # Remove processed incident
        if self.pending_incidents:
            self.pending_incidents.pop(0)
        
        return {
            "action": "action_plan_published",
            "plan": action_plan,
            "requires_approval": action_plan["requires_approval"]
        }
    
    def _build_action_catalog(self) -> Dict[str, List[Dict]]:
        """Build catalog of available actions per service."""
        return {
            "SignLink": [
                {"id": "adjust_iso", "name": "Increase camera ISO", "risk": 0.1},
                {"id": "night_mode", "name": "Switch to night mode", "risk": 0.1},
                {"id": "switch_camera", "name": "Switch to front/back camera", "risk": 0.2},
                {"id": "reduce_resolution", "name": "Reduce video resolution", "risk": 0.3},
                {"id": "offline_mode", "name": "Switch to offline processing", "risk": 0.5},
                {"id": "text_fallback", "name": "Fallback to text mode", "risk": 0.2}
            ],
            "GazeControl": [
                {"id": "recalibrate", "name": "Auto-recalibrate eye tracking", "risk": 0.1},
                {"id": "increase_dwell", "name": "Increase dwell time", "risk": 0.1},
                {"id": "adjust_sensitivity", "name": "Adjust tracking sensitivity", "risk": 0.2},
                {"id": "simplify_ui", "name": "Simplify control interface", "risk": 0.3}
            ],
            "PathSense": [
                {"id": "wifi_triangulation", "name": "Switch to WiFi triangulation", "risk": 0.2},
                {"id": "simplify_path", "name": "Simplify navigation instructions", "risk": 0.1},
                {"id": "increase_audio", "name": "Increase audio guidance volume", "risk": 0.1},
                {"id": "request_update", "name": "Request map data update", "risk": 0.2}
            ]
        }
    
    def _select_actions(self, service: str, recommendations: List[str]) -> List[Dict]:
        """Select specific actions based on recommendations."""
        available_actions = self.action_catalog.get(service, [])
        selected_actions = []
        
        # Match recommendations to catalog actions
        for rec in recommendations[:3]:  # Top 3 recommendations
            rec_lower = rec.lower()
            
            for action in available_actions:
                if any(keyword in rec_lower for keyword in action["name"].lower().split()):
                    if action not in selected_actions:
                        selected_actions.append(action)
                        break
        
        # If no matches, use default safe action
        if not selected_actions and available_actions:
            selected_actions = [available_actions[0]]  # Most conservative action
        
        return selected_actions
    
    def _assess_risk(self, actions: List[Dict]) -> float:
        """Calculate overall risk score for action plan."""
        if not actions:
            return 0.0
        
        # Average risk of all actions
        total_risk = sum(action.get("risk", 0.5) for action in actions)
        return total_risk / len(actions)
