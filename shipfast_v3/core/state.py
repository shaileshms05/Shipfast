"""
ShipFast v3.0 - Workflow State Management
Manages workflow states for both ShipFast Core and Deploy workflows
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class WorkflowType(str, Enum):
    """Types of workflows supported"""
    SHIPFAST = "shipfast"
    DEPLOY = "deploy"


class StageStatus(str, Enum):
    """Status of a workflow stage"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class Stage(BaseModel):
    """Represents a single stage in a workflow"""
    name: str
    status: StageStatus = StageStatus.PENDING
    output: Optional[Dict[str, Any]] = None
    artifacts: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    skipped_reason: Optional[str] = None
    
    def start(self):
        """Mark stage as started"""
        self.status = StageStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self, output: Dict[str, Any], artifacts: List[str] = None):
        """Mark stage as completed"""
        self.status = StageStatus.COMPLETED
        self.output = output
        self.artifacts = artifacts or []
        self.completed_at = datetime.now()
    
    def fail(self, error: str):
        """Mark stage as failed"""
        self.status = StageStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()
    
    def skip(self, reason: str):
        """Mark stage as skipped"""
        self.status = StageStatus.SKIPPED
        self.skipped_reason = reason
        self.completed_at = datetime.now()


class WorkflowState(BaseModel):
    """State of a workflow execution"""
    id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:8]}")
    workflow_type: WorkflowType
    request: Dict[str, Any]
    config: Dict[str, Any] = Field(default_factory=dict)
    stages: List[Stage]
    current_stage_index: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
    
    def advance_stage(self) -> bool:
        """Move to next stage. Returns False if no more stages."""
        self.current_stage_index += 1
        self.updated_at = datetime.now()
        return self.current_stage_index < len(self.stages)
    
    def get_current_stage(self) -> Optional[Stage]:
        """Get current stage"""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None
    
    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        return all(
            stage.status in [StageStatus.COMPLETED, StageStatus.SKIPPED] 
            for stage in self.stages
        )
    
    def has_failures(self) -> bool:
        """Check if workflow has any failures"""
        return any(stage.status == StageStatus.FAILED for stage in self.stages)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "workflow_type": self.workflow_type.value,
            "status": self._get_overall_status(),
            "stages": [
                {
                    "name": stage.name,
                    "status": stage.status.value,
                    "output": stage.output,
                    "artifacts": stage.artifacts,
                    "error": stage.error,
                    "started_at": stage.started_at.isoformat() if stage.started_at else None,
                    "completed_at": stage.completed_at.isoformat() if stage.completed_at else None,
                    "skipped_reason": stage.skipped_reason,
                }
                for stage in self.stages
            ],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    def _get_overall_status(self) -> str:
        """Determine overall workflow status"""
        if self.has_failures():
            return "failed"
        elif self.is_complete():
            return "completed"
        elif any(stage.status == StageStatus.IN_PROGRESS for stage in self.stages):
            return "in_progress"
        else:
            return "pending"


# Factory functions for creating workflows

def create_shipfast_workflow(feature_description: str, config: Dict[str, Any] = None) -> WorkflowState:
    """Create a new ShipFast workflow
    
    Stages:
    1. Requirements - Analyze and structure requirements
    2. Architecture - Design system architecture  
    3. Code - Generate code implementation
    4. Review - Review and optimize code
    5. Integration - Integrate and test
    6. Deployment - Deploy the feature
    """
    stages = [
        Stage(name="Requirements"),
        Stage(name="Architecture"),
        Stage(name="Code"),
        Stage(name="Review"),
        Stage(name="Integration"),
        Stage(name="Deployment"),
    ]
    
    return WorkflowState(
        workflow_type=WorkflowType.SHIPFAST,
        request={"feature_description": feature_description},
        config=config or {},
        stages=stages,
    )


def create_deploy_workflow(source: Dict[str, Any], config: Dict[str, Any] = None) -> WorkflowState:
    """Create a new Deploy workflow
    
    Stages:
    1. Analysis - Analyze code structure and requirements
    2. Architecture - Design cloud architecture with AI
    3. CostEstimate - Calculate infrastructure costs
    4. Provisioning - Generate IaC and deployment configs
    """
    stages = [
        Stage(name="Analysis"),
        Stage(name="Architecture"),
        Stage(name="CostEstimate"),
        Stage(name="Provisioning"),
    ]
    
    return WorkflowState(
        workflow_type=WorkflowType.DEPLOY,
        request=source,
        config=config or {},
        stages=stages,
    )
