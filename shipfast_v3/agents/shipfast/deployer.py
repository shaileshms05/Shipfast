"""
ShipFast v3.0 - Deployment Agent
Generates infrastructure and deployment configurations
"""

from typing import Dict, Any
import json
from agents.base import BaseAgent
from core.state import WorkflowState


class DeploymentAgent(BaseAgent):
    """Generates infrastructure as code and deployment configs"""
    
    async def _execute_internal(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        architecture = self._get_previous_output(context, "Architecture")
        design = architecture.get("design", {}) if architecture else {}
        
        system_prompt = """You are a cloud infrastructure expert.
Generate deployment configurations:
{
  "terraform": {"main.tf": "terraform config"},
  "docker": {"Dockerfile": "docker config", "docker-compose.yml": "compose config"},
  "kubernetes": {"deployment.yaml": "k8s config"},
  "cloud_provider": "aws",
  "estimated_cost": "$50/month",
  "deployment_steps": ["step 1", "step 2"]
}"""
        
        user_prompt = f"Generate infrastructure for:\n{json.dumps(design, indent=2)}"
        response = await self._ai_complete(user_prompt, system_prompt)
        deployment = self._extract_json(response) or {
            "terraform": {"main.tf": "# Terraform config\n"},
            "docker": {"Dockerfile": "FROM python:3.11\n"},
            "cloud_provider": "aws",
            "estimated_cost": "$50/month",
            "deployment_steps": ["Build Docker image", "Deploy to cloud"]
        }
        
        artifacts = []
        
        # Save Terraform
        for filename, content in deployment.get("terraform", {}).items():
            tf_file = self._save_artifact(content, filename, state)
            artifacts.append(tf_file)
        
        # Save Docker
        for filename, content in deployment.get("docker", {}).items():
            docker_file = self._save_artifact(content, filename, state)
            artifacts.append(docker_file)
        
        self.logger.info("Deployment configs generated", provider=deployment.get("cloud_provider"), cost=deployment.get("estimated_cost"))
        
        return {"deployment": deployment, "artifacts": artifacts, "summary": f"Generated {len(artifacts)} deployment files for {deployment.get('cloud_provider')}"}
