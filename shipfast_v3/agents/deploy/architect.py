"""
ShipFast Deploy - Architecture Agent
Designs cloud architecture using AI based on code analysis
"""

from typing import Dict, Any
from agents.base import BaseAgent
from core.state import WorkflowState, Stage
import structlog


class ArchitectAgent(BaseAgent):
    """AI-powered cloud architecture design agent"""
    
    def __init__(self, name: str, ai_client):
        super().__init__(name, ai_client)
        self.logger = structlog.get_logger(name)
    
    async def _execute_internal(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design cloud architecture based on analysis"""
        result = {
            "architecture": {},
            "recommendations": [],
        }
        
        try:
            # Get analysis from previous stage
            analysis = context.get("analysis", {})
            
            if not analysis:
                result["error"] = "No analysis data available"
                return result
            
            # Design architecture using AI
            architecture = await self._design_architecture(analysis)
            result["architecture"] = architecture
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis, architecture)
            result["recommendations"] = recommendations
            
            self.logger.info(
                "Architecture designed",
                components=len(architecture.get("components", [])),
                recommendations=len(recommendations),
            )
            
        except Exception as e:
            self.logger.error("Architecture design failed", error=str(e))
            result["error"] = str(e)
        
        return result
    
    async def _design_architecture(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to design cloud architecture"""
        
        # Build AI prompt
        prompt = self._build_architecture_prompt(analysis)
        
        # Get AI recommendation
        try:
            response = await self.ai_client.generate(
                prompt=prompt,
                max_tokens=2000,
            )
            
            # Parse AI response into structured architecture
            architecture = self._parse_architecture_response(response, analysis)
            return architecture
            
        except Exception as e:
            self.logger.error("AI architecture generation failed", error=str(e))
            # Fallback to rule-based architecture
            return self._fallback_architecture(analysis)
    
    def _build_architecture_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build prompt for AI architecture design"""
        
        tech_stack = analysis.get("tech_stack", {})
        dependencies = analysis.get("dependencies", {})
        
        prompt = f"""Design a cloud architecture for this application:

Technology Stack:
- Languages: {', '.join(tech_stack.get('languages', []))}
- Frameworks: {', '.join(tech_stack.get('frameworks', []))}
- Databases: {', '.join(tech_stack.get('databases', []))}

Dependencies: {len(dependencies)}

Provide architecture recommendations for:
1. Compute resources (containers, serverless, VMs)
2. Database and storage
3. Networking and load balancing
4. Caching strategy
5. CI/CD pipeline

Keep it production-ready and cost-effective."""
        
        return prompt
    
    def _parse_architecture_response(self, response: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured architecture"""
        
        # For now, return a basic structure
        # In production, parse the AI response properly
        return self._fallback_architecture(analysis)
    
    def _fallback_architecture(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based architecture design fallback"""
        
        tech_stack = analysis.get("tech_stack", {})
        
        architecture = {
            "components": [],
            "services": [],
            "infrastructure": {},
        }
        
        # Compute
        if any(lang in tech_stack.get("languages", []) for lang in ["Python", "JavaScript", "TypeScript"]):
            architecture["components"].append({
                "type": "compute",
                "service": "AWS ECS / Fargate",
                "reason": "Container-based deployment for flexibility",
            })
        
        # Database
        if "postgres" in str(tech_stack.get("databases", [])).lower():
            architecture["components"].append({
                "type": "database",
                "service": "AWS RDS PostgreSQL",
                "reason": "Managed PostgreSQL with backups",
            })
        
        # Load Balancer
        architecture["components"].append({
            "type": "load_balancer",
            "service": "AWS ALB",
            "reason": "Application load balancing",
        })
        
        # Storage
        architecture["components"].append({
            "type": "storage",
            "service": "AWS S3",
            "reason": "Static assets and file storage",
        })
        
        return architecture
    
    def _generate_recommendations(self, analysis: Dict[str, Any], architecture: Dict[str, Any]) -> list:
        """Generate deployment recommendations"""
        
        recommendations = [
            "Use Docker containers for consistent deployments",
            "Implement auto-scaling based on CPU/memory metrics",
            "Set up CloudWatch logging and monitoring",
            "Use managed services to reduce operational overhead",
            "Implement blue-green deployment strategy",
        ]
        
        return recommendations
