"""
Omni-Sense Root Cause Agent - AI-Powered Diagnosis
Uses Gemini LLM to diagnose accessibility service quality issues.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
import google.generativeai as genai
from loguru import logger
from dotenv import load_dotenv

from .base_agent import BaseAgent

load_dotenv()


class RootCauseAgent(BaseAgent):
    """
    Root Cause Agent: Diagnoses why accessibility services are degrading.
    
    Responsibilities:
    - Receive quality alerts from Monitoring Agent
    - Analyze service context (user environment, device state)
    - Use Gemini LLM for intelligent diagnosis
    - Generate actionable recommendations
    """
    
    def __init__(self):
        super().__init__(
            name="Root Cause Agent",
            description="AI-powered accessibility service quality diagnosis"
        )
        
        # Gemini LLM configuration
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.llm = genai.GenerativeModel('gemini-2.5-flash')
            logger.info(f"✅ [{self.name}] Gemini LLM initialized")
        else:
            self.llm = None
            logger.warning(f"⚠️ [{self.name}] No GOOGLE_API_KEY - using rule-based analysis")
        
        # Pending alerts to analyze
        self.pending_alerts: List[Dict] = []
        self.diagnosis_history: List[Dict] = []
    
    def receive_alert(self, alert: Dict[str, Any]):
        """Receive quality alert from Monitoring Agent."""
        self.pending_alerts.append(alert)
        logger.info(f"📥 [{self.name}] Received alert for {alert.get('service')}")
    
    def perceive(self) -> Dict[str, Any]:
        """
        Gather context about the quality issue.
        
        Returns:
            Dict containing alert and contextual information
        """
        if not self.pending_alerts:
            return {"has_alerts": False}
        
        # Get the most recent alert
        alert = self.pending_alerts[0]
        
        # Gather contextual information
        # In real implementation, this would query service logs, user device state, etc.
        context = {
            "has_alerts": True,
            "current_alert": alert,
            "service": alert["service"],
            "metric": alert["metric"],
            "value": alert["value"],
            "threshold": alert["threshold"],
            "severity": alert["severity"],
            "description": alert["description"]
        }
        
        logger.info(f"🔍 [{self.name}] Analyzing {alert['service']} - {alert['description']}")
        
        return context
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose root cause using AI or rule-based analysis.
        
        Args:
            perception: Context from perceive()
            
        Returns:
            Dict containing diagnosis and recommendations
        """
        if not perception.get("has_alerts"):
            return {
                "diagnosis_performed": False,
                "reason": "no_alerts"
            }
        
        alert = perception.get("current_alert", {})
        service = perception.get("service")
        
        # Prepare analysis context
        context_text = self._prepare_analysis_context(perception)
        
        # Use LLM if available, otherwise use rule-based
        if self.llm:
            diagnosis = self._llm_diagnosis(context_text, perception)
        else:
            diagnosis = self._rule_based_diagnosis(perception)
        
        logger.info(f"🧠 [{self.name}] Diagnosis: {diagnosis['root_cause']}")
        
        return {
            "diagnosis_performed": True,
            "service": service,
            "diagnosis": diagnosis,
            "timestamp": datetime.now().isoformat()
        }
    
    def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and publish diagnosis report.
        
        Args:
            reasoning: Diagnosis from reason()
            
        Returns:
            Dict containing incident report
        """
        if not reasoning.get("diagnosis_performed"):
            return {"action": "none"}
        
        diagnosis = reasoning.get("diagnosis", {})
        
        # Create incident report
        incident_report = {
            "incident_id": f"INC_{datetime.now().timestamp()}",
            "timestamp": reasoning["timestamp"],
            "service": reasoning["service"],
            "root_cause": diagnosis["root_cause"],
            "confidence": diagnosis["confidence"],
            "explanation": diagnosis["explanation"],
            "recommendations": diagnosis["recommendations"]
        }
        
        self.diagnosis_history.append(incident_report)
        
        # Remove processed alert
        if self.pending_alerts:
            self.pending_alerts.pop(0)
        
        logger.success(
            f"📋 [{self.name}] INCIDENT REPORT\\n"
            f"   Service: {incident_report['service']}\\n"
            f"   Root Cause: {incident_report['root_cause']}\\n"
            f"   Confidence: {incident_report['confidence']}\\n"
            f"   Recommendations: {len(incident_report['recommendations'])} actions"
        )
        
        return {
            "action": "incident_report_generated",
            "report": incident_report
        }
    
    def _prepare_analysis_context(self, perception: Dict[str, Any]) -> str:
        """Prepare contextual information for analysis."""
        alert = perception.get("current_alert", {})
        
        context = f"""
Accessibility Service Quality Issue:

Service: {perception.get('service')}
Problem: {perception.get('description')}
Metric: {perception.get('metric')} = {perception.get('value'):.2f} (threshold: {perception.get('threshold'):.2f})
Severity: {perception.get('severity')}

Analyze the root cause and suggest solutions.
"""
        return context
    
    def _llm_diagnosis(self, context: str, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini LLM for intelligent diagnosis."""
        service = perception.get('service')
        metric = perception.get('metric')
        
        # Create specialized prompt based on service type
        prompt = f"""{context}

You are an AI expert in accessibility technology. Based on the service quality issue above, provide:

1. **Root Cause:** The most likely reason for this quality degradation (one phrase)
2. **Confidence:** Your confidence level (HIGH/MEDIUM/LOW)
3. **Explanation:** Brief technical explanation (2-3 sentences)
4. **Recommendations:** 3 specific actions to fix this issue

Service Context:
- SignLink: AR sign language translation (depends on: camera quality, lighting, hand visibility)
- GazeControl: Eye-tracking IoT control (depends on: calibration, head position, eye visibility)
- PathSense: Spatial navigation (depends on: GPS accuracy, sensor data, map freshness)

Format your response as:
ROOT_CAUSE: [one-line diagnosis]
CONFIDENCE: [HIGH/MEDIUM/LOW]
EXPLANATION: [technical explanation]
RECOMMENDATIONS:
1. [action 1]
2. [action 2]
3. [action 3]
"""
        
        try:
            response = self.llm.generate_content(prompt)
            diagnosis_text = response.text
            
            # Parse LLM response
            diagnosis = self._parse_llm_response(diagnosis_text)
            
            return diagnosis
            
        except Exception as e:
            logger.error(f"❌ [{self.name}] Gemini API error: {e}")
            return self._rule_based_diagnosis(perception)
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's structured response."""
        lines = response_text.strip().split('\\n')
        
        root_cause = "Unknown issue"
        confidence = "MEDIUM"
        explanation = ""
        recommendations = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("ROOT_CAUSE:"):
                root_cause = line.replace("ROOT_CAUSE:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                confidence = line.replace("CONFIDENCE:", "").strip()
            elif line.startswith("EXPLANATION:"):
                explanation = line.replace("EXPLANATION:", "").strip()
                current_section = "explanation"
            elif line.startswith("RECOMMENDATIONS:"):
                current_section = "recommendations"
            elif current_section == "explanation" and line:
                explanation += " " + line
            elif current_section == "recommendations" and line:
                # Remove numbering
                rec = line.lstrip("1234567890.- ")
                if rec:
                    recommendations.append(rec)
        
        return {
            "root_cause": root_cause,
            "confidence": confidence,
            "explanation": explanation.strip(),
            "recommendations": recommendations[:3]  # Top 3
        }
    
    def _rule_based_diagnosis(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based diagnosis when LLM unavailable."""
        service = perception.get('service')
        metric = perception.get('metric')
        value = perception.get('value')
        
        # Simple rule-based logic
        if service == "SignLink":
            if metric == "accuracy" and value < 0.5:
                return {
                    "root_cause": "Poor camera visibility or lighting",
                    "confidence": "MEDIUM",
                    "explanation": "Sign language recognition accuracy very low, likely due to inadequate lighting or hand occlusion.",
                    "recommendations": [
                        "Increase camera ISO setting",
                        "Switch to night mode",
                        "Request user to improve lighting"
                    ]
                }
        
        elif service == "GazeControl":
            if metric == "accuracy" and value < 0.7:
                return {
                    "root_cause": "Eye-tracking calibration drift",
                    "confidence": "HIGH",
                    "explanation": "Gaze detection accuracy dropped, usually caused by user position change or head movement.",
                    "recommendations": [
                        "Perform automatic recalibration",
                        "Adjust camera angle",
                        "Increase dwell time threshold"
                    ]
                }
        
        # Generic fallback
        return {
            "root_cause": f"{metric} degradation in {service}",
            "confidence": "LOW",
            "explanation": f"Unable to determine specific cause. {metric} value {value:.2f} below threshold.",
            "recommendations": [
                "Restart service",
                "Check device resources",
                "Review recent changes"
            ]
        }
