"""
ShipFast Deploy - Cost Estimator Agent
Calculates infrastructure costs based on architecture
"""

from typing import Dict, Any
from agents.base import BaseAgent
from core.state import WorkflowState, Stage
import structlog


class CostEstimatorAgent(BaseAgent):
    """Infrastructure cost estimation agent"""
    
    # AWS pricing (simplified monthly estimates)
    AWS_PRICING = {
        "compute": {
            "ecs_fargate_small": 30,  # 0.25 vCPU, 0.5 GB
            "ecs_fargate_medium": 60,  # 0.5 vCPU, 1 GB
            "ecs_fargate_large": 120,  # 1 vCPU, 2 GB
        },
        "database": {
            "rds_postgres_small": 50,
            "rds_postgres_medium": 150,
            "rds_postgres_large": 300,
        },
        "load_balancer": {
            "alb": 25,
        },
        "storage": {
            "s3_per_gb": 0.023,
            "ebs_per_gb": 0.10,
        },
        "networking": {
            "data_transfer_per_gb": 0.09,
        },
    }
    
    def __init__(self, name: str, ai_client):
        super().__init__(name, ai_client)
        self.logger = structlog.get_logger(name)
    
    async def _execute_internal(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate infrastructure costs"""
        result = {
            "cost_breakdown": {},
            "total_monthly": 0,
            "total_annual": 0,
        }
        
        try:
            # Get architecture from previous stage
            architecture = context.get("architecture", {})
            
            if not architecture:
                result["error"] = "No architecture data available"
                return result
            
            # Calculate costs
            cost_breakdown = self._calculate_costs(architecture)
            result["cost_breakdown"] = cost_breakdown
            
            # Calculate totals
            total_monthly = sum(item.get("monthly_cost", 0) for item in cost_breakdown)
            result["total_monthly"] = round(total_monthly, 2)
            result["total_annual"] = round(total_monthly * 12, 2)
            
            self.logger.info(
                "Cost estimation completed",
                monthly=result["total_monthly"],
                annual=result["total_annual"],
            )
            
        except Exception as e:
            self.logger.error("Cost estimation failed", error=str(e))
            result["error"] = str(e)
        
        return result
    
    def _calculate_costs(self, architecture: Dict[str, Any]) -> list:
        """Calculate costs for each component"""
        
        cost_breakdown = []
        components = architecture.get("components", [])
        
        for component in components:
            comp_type = component.get("type", "")
            service = component.get("service", "")
            
            cost_item = {
                "component": service,
                "type": comp_type,
                "monthly_cost": 0,
            }
            
            # Estimate cost based on component type
            if comp_type == "compute":
                cost_item["monthly_cost"] = self.AWS_PRICING["compute"]["ecs_fargate_medium"]
                cost_item["details"] = "1 Fargate task, medium size"
                
            elif comp_type == "database":
                cost_item["monthly_cost"] = self.AWS_PRICING["database"]["rds_postgres_small"]
                cost_item["details"] = "RDS PostgreSQL db.t3.small"
                
            elif comp_type == "load_balancer":
                cost_item["monthly_cost"] = self.AWS_PRICING["load_balancer"]["alb"]
                cost_item["details"] = "Application Load Balancer"
                
            elif comp_type == "storage":
                # Assume 100 GB storage
                cost_item["monthly_cost"] = self.AWS_PRICING["storage"]["s3_per_gb"] * 100
                cost_item["details"] = "100 GB S3 storage"
            
            cost_breakdown.append(cost_item)
        
        # Add data transfer costs
        cost_breakdown.append({
            "component": "Data Transfer",
            "type": "networking",
            "monthly_cost": 20,
            "details": "Estimated 200 GB outbound",
        })
        
        return cost_breakdown
