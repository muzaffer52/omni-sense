"""
NEXA Base Agent - Abstract base class for all AI agents.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger
from enum import Enum


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"


class BaseAgent(ABC):
    """Abstract base class for all NEXA agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self.last_execution_time: Optional[datetime] = None
        self.execution_count = 0
        self.error_count = 0
        
        logger.info(f"✅ Initialized {self.name}")
    
    @abstractmethod
    def perceive(self) -> Dict[str, Any]:
        """
        Gather information from the environment.
        
        Returns:
            Dict containing perceived data/state
        """
        pass
    
    @abstractmethod
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process perceived information and make decisions.
        
        Args:
            perception: Data gathered from perceive()
            
        Returns:
            Dict containing reasoning results and decisions
        """
        pass
    
    @abstractmethod
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take action based on reasoning.
        
        Args:
            decision: Output from reason()
            
        Returns:
            Dict containing action results
        """
        pass
    
    def execute(self) -> Dict[str, Any]:
        """
        Main execution loop: perceive -> reason -> act.
        
        Returns:
            Dict containing execution results
        """
        self.status = AgentStatus.RUNNING
        self.execution_count += 1
        
        try:
            logger.info(f"🤖 [{self.name}] Starting execution #{self.execution_count}")
            
            # 1. Perceive
            perception = self.perceive()
            logger.debug(f"   Perception: {perception}")
            
            # 2. Reason
            decision = self.reason(perception)
            logger.debug(f"   Decision: {decision}")
            
            # 3. Act
            result = self.act(decision)
            logger.debug(f"   Result: {result}")
            
            self.last_execution_time = datetime.now()
            self.status = AgentStatus.IDLE
            
            logger.success(f"✅ [{self.name}] Execution completed")
            
            return {
                "agent": self.name,
                "status": "success",
                "execution_count": self.execution_count,
                "timestamp": self.last_execution_time.isoformat(),
                "perception": perception,
                "decision": decision,
                "result": result
            }
            
        except Exception as e:
            self.error_count += 1
            self.status = AgentStatus.ERROR
            logger.error(f"❌ [{self.name}] Execution failed: {e}")
            
            return {
                "agent": self.name,
                "status": "error",
                "error": str(e),
                "error_count": self.error_count,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "last_execution": self.last_execution_time.isoformat() if self.last_execution_time else None
        }
    
    def reset(self):
        """Reset agent state."""
        self.status = AgentStatus.IDLE
        self.execution_count = 0
        self.error_count = 0
        self.last_execution_time = None
        logger.info(f"🔄 [{self.name}] Agent reset")
