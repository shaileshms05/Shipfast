"""
ShipFast v3.0 - Architect Agent
Designs system architecture based on requirements
"""

from typing import Dict, Any
import json

from agents.base import BaseAgent
from core.state import WorkflowState


class ArchitectAgent(BaseAgent):
    """
    Designs system architecture based on requirements specification
    """
    
    async def _execute_internal(
        self,
        state: WorkflowState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Design system architecture
        """
        # Get requirements from previous stage
        requirements = self._get_previous_output(context, "Requirements")
        spec = requirements.get("specification", {}) if requirements else {}
        
        feature_request = context["request"].get("feature_request", "")
        
        system_prompt = """You are an expert software architect.
Your job is to design clean, scalable system architectures.

Consider:
1. System components and their responsibilities
2. Data flow and API design
3. Database schema if needed
4. Technology stack recommendations
5. Security architecture
6. Scalability considerations

Respond with a JSON object containing:
{
  "overview": "High-level architecture description",
  "components": [
    {
      "name": "Component Name",
      "type": "API/Service/Database/Frontend",
      "purpose": "What it does",
      "technologies": ["tech1", "tech2"]
    }
  ],
  "data_flow": "Description of how data flows through the system",
  "api_design": {
    "endpoints": [
      {
        "method": "GET/POST/etc",
        "path": "/api/path",
        "purpose": "What it does"
      }
    ]
  },
  "database_schema": {
    "tables": [
      {
        "name": "table_name",
        "fields": ["field1", "field2"]
      }
    ]
  },
  "security": ["security measure 1", ...],
  "scalability": ["scalability consideration 1", ...]
}"""
        
        user_prompt = f"""Feature Request: {feature_request}

Requirements Specification:
{json.dumps(spec, indent=2)}

Design a comprehensive system architecture for this feature."""
        
        # Call AI
        response = await self._ai_complete(user_prompt, system_prompt)
        
        # Extract JSON
        architecture = self._extract_json(response)
        
        if not architecture:
            # Fallback
            architecture = {
                "overview": f"Architecture for {feature_request}",
                "components": [
                    {
                        "name": "Main Service",
                        "type": "API",
                        "purpose": "Handle the feature implementation",
                        "technologies": ["Python", "FastAPI"]
                    }
                ],
                "data_flow": "Standard request-response flow",
                "api_design": {
                    "endpoints": []
                },
                "database_schema": {
                    "tables": []
                },
                "security": ["Input validation", "Authentication"],
                "scalability": ["Horizontal scaling", "Caching"]
            }
        
        # Save architecture
        arch_content = json.dumps(architecture, indent=2)
        arch_file = self._save_artifact(
            arch_content,
            "architecture_design.json",
            state,
        )
        
        self.logger.info(
            "Architecture design generated",
            components_count=len(architecture.get("components", [])),
        )
        
        return {
            "design": architecture,
            "artifacts": [arch_file],
            "summary": f"Designed architecture with {len(architecture.get('components', []))} components",
        }
