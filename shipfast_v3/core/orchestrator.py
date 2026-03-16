"""
ShipFast v3.0 - Unified Orchestrator
Orchestrates both ShipFast Core and Deploy workflows
"""

from typing import Dict, Any, Optional
import structlog
from core.state import WorkflowState, WorkflowType, StageStatus
from services.ai.cerebras import CerebrasClient

# Import ShipFast agents
from agents.shipfast.requirements import RequirementsAgent
from agents.shipfast.architect import ArchitectAgent
from agents.shipfast.coder import CodeAgent
from agents.shipfast.reviewer import ReviewAgent
from agents.shipfast.integrator import IntegrationAgent
from agents.shipfast.deployer import DeploymentAgent

# Import Deploy agents
from agents.deploy.analyzer import AnalyzerAgent as DeployAnalyzerAgent
from agents.deploy.architect import ArchitectAgent as DeployArchitectAgent
from agents.deploy.cost_estimator import CostEstimatorAgent
from agents.deploy.provisioner import ProvisionerAgent


class UnifiedOrchestrator:
    """Unified orchestrator for all ShipFast workflows"""
    
    def __init__(self, ai_client: CerebrasClient):
        """
        Initialize orchestrator with AI client
        
        Args:
            ai_client: Cerebras AI client for agents
        """
        self.ai_client = ai_client
        self.logger = structlog.get_logger("orchestrator")
        
        # Initialize ShipFast agents
        self.shipfast_agents = {
            "Requirements": RequirementsAgent("RequirementsAgent", ai_client),
            "Architecture": ArchitectAgent("ArchitectAgent", ai_client),
            "Code": CodeAgent("CodeAgent", ai_client),
            "Review": ReviewAgent("ReviewAgent", ai_client),
            "Integration": IntegrationAgent("IntegrationAgent", ai_client),
            "Deployment": DeploymentAgent("DeploymentAgent", ai_client),
        }
        
        # Initialize Deploy agents (only AnalyzerAgent exists for now)
        self.deploy_agents = {
            "Analysis": DeployAnalyzerAgent("AnalyzerAgent", ai_client),
            "Architecture": DeployArchitectAgent("DeployArchitectAgent", ai_client),
            "CostEstimate": CostEstimatorAgent("CostEstimatorAgent", ai_client),
            "Provisioning": ProvisionerAgent("ProvisionerAgent", ai_client),
        }
        
        self.logger.info(
            "Orchestrator initialized",
            component="orchestrator",
            shipfast_agents=len(self.shipfast_agents),
            deploy_agents=len(self.deploy_agents),
        )
    
    async def execute(self, state: WorkflowState):
        """
        Execute a workflow
        
        Args:
            state: Workflow state to execute
        """
        self.logger.info(
            "Starting workflow execution",
            component="orchestrator",
            workflow_id=state.id,
            workflow_type=state.workflow_type.value,
        )
        
        try:
            if state.workflow_type == WorkflowType.SHIPFAST:
                await self._execute_shipfast(state)
            elif state.workflow_type == WorkflowType.DEPLOY:
                await self._execute_deploy(state)
            else:
                raise ValueError(f"Unknown workflow type: {state.workflow_type}")
            
            self.logger.info(
                "Workflow completed successfully",
                component="orchestrator",
                workflow_id=state.id,
                artifacts_count=sum(len(stage.artifacts) for stage in state.stages),
            )
            
        except Exception as e:
            self.logger.error(
                "Workflow execution failed",
                component="orchestrator",
                workflow_id=state.id,
                error=str(e),
            )
            # Mark current stage as failed
            current_stage = state.get_current_stage()
            if current_stage:
                current_stage.fail(str(e))
            raise Exception(f"Workflow failed: {str(e)}")
    
    async def _execute_shipfast(self, state: WorkflowState):
        """Execute ShipFast workflow (6 agents)"""
        for stage in state.stages:
            agent = self.shipfast_agents.get(stage.name)
            
            if not agent:
                self.logger.warning(
                    "Agent not found for stage",
                    stage=stage.name,
                )
                stage.skip(f"Agent not found: {stage.name}")
                continue
            
            self.logger.info(
                "Executing stage",
                workflow_id=state.id,
                stage=stage.name,
            )
            
            try:
                await agent.execute(state, stage)
            except Exception as e:
                self.logger.error(
                    "Stage execution failed",
                    stage=stage.name,
                    error=str(e),
                )
                raise
            
            # Check if we should continue
            if not state.advance_stage():
                break
    
    async def _execute_deploy(self, state: WorkflowState):
        """Execute Deploy workflow (4 agents)"""
        for stage in state.stages:
            agent = self.deploy_agents.get(stage.name)
            
            if not agent:
                self.logger.warning(
                    "Agent not found for stage",
                    stage=stage.name,
                )
                stage.skip(f"Agent not found: {stage.name}")
                continue
            
            self.logger.info(
                "Executing stage",
                workflow_id=state.id,
                stage=stage.name,
            )
            
            try:
                await agent.execute(state, stage)
                
                # Check if Analysis stage returned an error (e.g., GitHub access failed)
                if stage.name == "Analysis" and stage.output:
                    analysis_data = stage.output.get("analysis", {})
                    if "error" in analysis_data:
                        # Stop workflow - don't continue with fake data
                        self.logger.error(
                            "Analysis failed with error, stopping workflow",
                            error=analysis_data.get("error"),
                        )
                        # Mark remaining stages as skipped
                        for remaining_stage in state.stages[state.current_stage_index + 1:]:
                            remaining_stage.skip("Skipped due to analysis failure")
                        break
                
            except Exception as e:
                self.logger.error(
                    "Stage execution failed",
                    stage=stage.name,
                    error=str(e),
                )
                raise
            
            # Check if we should continue
            if not state.advance_stage():
                break
    
    def get_agent(self, workflow_type: WorkflowType, stage_name: str) -> Optional[Any]:
        """Get specific agent by workflow type and stage name"""
        if workflow_type == WorkflowType.SHIPFAST:
            return self.shipfast_agents.get(stage_name)
        elif workflow_type == WorkflowType.DEPLOY:
            return self.deploy_agents.get(stage_name)
        return None
