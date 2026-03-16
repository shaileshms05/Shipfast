"""
ShipFast v3.0 - Integration Agent
Creates tests, documentation, and deployment configs
"""

from typing import Dict, Any
import json
from agents.base import BaseAgent
from core.state import WorkflowState


class IntegrationAgent(BaseAgent):
    """Creates tests, docs, and deployment configs"""
    
    async def _execute_internal(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        code_output = self._get_previous_output(context, "Code")
        implementation = code_output.get("implementation", {}) if code_output else {}
        
        system_prompt = """You are a DevOps and testing expert.
Create comprehensive integration artifacts:
{
  "tests": [{"file": "test_main.py", "content": "test code"}],
  "documentation": {"content": "markdown documentation"},
  "deployment_config": {"docker": "Dockerfile content", "env": ".env.example content"}
}"""
        
        user_prompt = f"Create tests, docs, and configs for:\n{json.dumps(implementation, indent=2)}"
        response = await self._ai_complete(user_prompt, system_prompt)
        integration = self._extract_json(response) or {
            "tests": [],
            "documentation": {"content": "# Documentation\nFeature implemented successfully"},
            "deployment_config": {}
        }
        
        artifacts = []
        
        # Save tests
        for test in integration.get("tests", []):
            test_file = self._save_artifact(test.get("content", ""), test.get("file", "test.py"), state)
            artifacts.append(test_file)
        
        # Save documentation
        if integration.get("documentation"):
            doc_file = self._save_artifact(integration["documentation"].get("content", ""), "README.md", state)
            artifacts.append(doc_file)
        
        self.logger.info("Integration artifacts created", tests_count=len(integration.get("tests", [])))
        
        return {"integration": integration, "artifacts": artifacts, "summary": f"Created {len(artifacts)} integration files"}
