"""
ShipFast v3.0 - Requirements Agent
Analyzes feature requests and generates detailed specifications
"""

from typing import Dict, Any
import json

from agents.base import BaseAgent
from core.state import WorkflowState


class RequirementsAgent(BaseAgent):
    """
    Analyzes feature requests and creates detailed specifications
    """
    
    async def _execute_internal(
        self,
        state: WorkflowState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze feature request and generate specification
        """
        feature_request = context["request"].get("feature_request", "")
        
        system_prompt = """You are an expert product manager and requirements analyst.
Your job is to analyze feature requests and create comprehensive, actionable specifications.

Think through:
1. What is the user really trying to accomplish?
2. What are the technical implications?
3. What edge cases need to be considered?
4. What security and performance aspects matter?
5. What dependencies are needed?

Respond with a JSON object containing:
{
  "title": "Clear, concise title",
  "description": "Detailed description",
  "user_story": "As a... I want... So that...",
  "acceptance_criteria": ["criterion 1", "criterion 2", ...],
  "technical_requirements": ["requirement 1", ...],
  "dependencies": ["dependency 1", ...],
  "security_considerations": ["consideration 1", ...],
  "performance_requirements": ["requirement 1", ...],
  "clarifying_questions": ["question 1", ...]
}"""
        
        user_prompt = f"""Feature Request: {feature_request}

Analyze this feature request and provide a comprehensive specification."""
        
        # Call AI
        response = await self._ai_complete(user_prompt, system_prompt)
        
        # Extract JSON
        spec = self._extract_json(response)
        
        if not spec:
            # Fallback if JSON extraction fails
            spec = {
                "title": feature_request[:100],
                "description": response[:500],
                "user_story": f"As a user, I want {feature_request}",
                "acceptance_criteria": ["Feature implemented as requested"],
                "technical_requirements": ["Implement the requested feature"],
                "dependencies": [],
                "security_considerations": ["Standard security best practices"],
                "performance_requirements": ["Acceptable performance"],
                "clarifying_questions": [],
            }
        
        # Save specification
        spec_content = json.dumps(spec, indent=2)
        spec_file = self._save_artifact(
            spec_content,
            "requirements_spec.json",
            state,
        )
        
        self.logger.info(
            "Requirements specification generated",
            title=spec.get("title", "Unknown"),
            criteria_count=len(spec.get("acceptance_criteria", [])),
        )
        
        return {
            "specification": spec,
            "artifacts": [spec_file],
            "summary": f"Generated specification: {spec.get('title', 'Unknown')}",
        }
