"""
Omni-Sense Execution Agent - Safe Service Control
Executes approved actions to optimize accessibility services.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, List
from loguru import logger
from dotenv import load_dotenv

from .base_agent import BaseAgent

load_dotenv()


class ExecutionAgent(BaseAgent):
    """
    Execution Agent: Safely executes service optimization actions.
    
    Responsibilities:
    - Receive action plans from Decision Agent
    - Verify safety constraints
    - Execute approved actions
    - Monitor execution results
    - Rollback if needed
    """
    
    def __init__(self):
        super().__init__(
            name="Execution Agent",
            description="Safe execution of service optimization actions"
        )
        
        # Pending action plans
        self.pending_actions: List[Dict] = []
        self.execution_history: List[Dict] = []
        
        # Safety constraints
        self.rate_limit_window = 60  # seconds
        self.max_actions_per_window = 5
        self.recent_actions = []
        
        logger.info(f"✅ [{self.name}] Initialized with safety rate limiting")
    
    def receive_action_plan(self, plan: Dict[str, Any]):
        """Receive action plan from Decision Agent."""
        self.pending_actions.append(plan)
        logger.info(f"📥 [{self.name}] Received action plan for {plan.get('service')}")
    
    def perceive(self) -> Dict[str, Any]:
        """
        Get next action plan to execute.
        
        Returns:
            Dict containing action plan
        """
        if not self.pending_actions:
            return {"has_actions": False}
        
        plan = self.pending_actions[0]
        
        return {
            "has_actions": True,
            "plan": plan,
            "service": plan["service"],
            "actions": plan["actions"],
            "requires_approval": plan.get("requires_approval", False)
        }
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate safety and prepare for execution.
        
        Args:
            perception: Action plan information
            
        Returns:
            Dict containing execution decision
        """
        if not perception.get("has_actions"):
            return {
                "execution_approved": False,
                "reason": "no_pending_actions"
            }
        
        plan = perception.get("plan")
        
        # Check if requires human approval
        if perception.get("requires_approval"):
            logger.warning(f"⚠️ [{self.name}] High-risk plan requires human approval")
            return {
                "execution_approved": False,
                "reason": "requires_human_approval",
                "plan": plan
            }
        
        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning(f"⚠️ [{self.name}] Rate limit exceeded, delaying execution")
            return {
                "execution_approved": False,
                "reason": "rate_limit_exceeded"
            }
        
        # Safety checks passed
        return {
            "execution_approved": True,
            "plan": plan,
            "service": perception["service"],
            "actions": perception["actions"]
        }
    
    def act(self, reasoning: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute approved actions.
        
        Args:
            reasoning: Execution decision from reason()
            
        Returns:
            Dict containing execution results
        """
        if not reasoning.get("execution_approved"):
            return {
                "action": "execution_blocked",
                "reason": reasoning.get("reason")
            }
        
        service = reasoning.get("service")
        actions = reasoning.get("actions", [])
        
        execution_results = []
        
        # Execute each action
        for action in actions:
            result = self._execute_action(service, action)
            execution_results.append(result)
            
            # Record action for rate limiting
            self.recent_actions.append({
                "timestamp": time.time(),
                "service": service,
                "action": action["id"]
            })
        
        # Create execution record
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "actions_executed": len(execution_results),
            "results": execution_results,
            "overall_status": "SUCCESS" if all(r["success"] for r in execution_results) else "PARTIAL"
        }
        
        self.execution_history.append(execution_record)
        
        # Remove processed plan
        if self.pending_actions:
            self.pending_actions.pop(0)
        
        logger.success(
            f"⚡ [{self.name}] EXECUTION COMPLETE\\n"
            f"   Service: {service}\\n"
            f"   Actions: {execution_record['actions_executed']}\\n"
            f"   Status: {execution_record['overall_status']}"
        )
        
        return {
            "action": "execution_complete",
            "execution_record": execution_record
        }
    
    def _execute_action(self, service: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single action (simulated for demo).
        
        In production, this would call actual service APIs.
        """
        action_id = action["id"]
        action_name = action["name"]
        
        logger.info(f"   ▶️ Executing: {action_name}")
        
        # Simulate execution time
        time.sleep(0.5)
        
        # Simulate execution (in real system, call service APIs)
        result = {
            "action_id": action_id,
            "action_name": action_name,
            "success": True,
            "message": f"{action_name} applied successfully",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"      ✅ {action_name} completed")
        
        return result
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = time.time()
        window_start = current_time - self.rate_limit_window
        
        # Clean old actions
        self.recent_actions = [
            a for a in self.recent_actions 
            if a["timestamp"] > window_start
        ]
        
        # Check limit
        return len(self.recent_actions) < self.max_actions_per_window
