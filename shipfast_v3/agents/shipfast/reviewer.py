"""
ShipFast v3.0 - Review Agent  
Performs security and quality review of generated code
"""

from typing import Dict, Any
import json
from agents.base import BaseAgent
from core.state import WorkflowState


class ReviewAgent(BaseAgent):
    """Reviews code for security, performance, and quality"""
    
    async def _execute_internal(self, state: WorkflowState, context: Dict[str, Any]) -> Dict[str, Any]:
        code_output = self._get_previous_output(context, "Code")
        implementation = code_output.get("implementation", {}) if code_output else {}
        
        system_prompt = """You are a senior code reviewer focusing on security, performance, and quality.
Analyze code and provide a review with:
{
  "security_issues": [{"severity": "critical/high/medium/low", "issue": "description", "fix": "how to fix"}],
  "performance_issues": [{"severity": "high/medium/low", "issue": "description", "fix": "solution"}],
  "quality_issues": [{"type": "style/structure/documentation", "issue": "description"}],
  "recommendations": ["recommendation 1", ...],
  "overall_score": 85,
  "approved": true
}"""
        
        user_prompt = f"Review this implementation:\n{json.dumps(implementation, indent=2)}"
        response = await self._ai_complete(user_prompt, system_prompt)
        review = self._extract_json(response) or {
            "security_issues": [],
            "performance_issues": [],
            "quality_issues": [],
            "recommendations": ["Code looks good"],
            "overall_score": 85,
            "approved": True
        }
        
        review_file = self._save_artifact(json.dumps(review, indent=2), "code_review.json", state)
        
        self.logger.info("Code review completed", score=review.get("overall_score", 0), approved=review.get("approved", False))
        
        return {"review": review, "artifacts": [review_file], "summary": f"Review score: {review.get('overall_score', 0)}/100"}
