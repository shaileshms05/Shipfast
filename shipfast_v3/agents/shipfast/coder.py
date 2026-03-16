"""
ShipFast v3.0 - Code Agent
Generates implementation code based on architecture
"""

from typing import Dict, Any
import json

from agents.base import BaseAgent
from core.state import WorkflowState


class CodeAgent(BaseAgent):
    """
    Generates implementation code based on architecture design
    """
    
    async def _execute_internal(
        self,
        state: WorkflowState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate implementation code
        """
        # Get previous outputs
        requirements = self._get_previous_output(context, "Requirements")
        architecture = self._get_previous_output(context, "Architecture")
        
        spec = requirements.get("specification", {}) if requirements else {}
        design = architecture.get("design", {}) if architecture else {}
        
        feature_request = context["request"].get("feature_request", "")
        
        system_prompt = """You are an expert software engineer.
Generate clean, production-ready code following best practices.

Include:
1. Well-structured, modular code
2. Proper error handling
3. Input validation
4. Type hints (for Python)
5. Docstrings and comments
6. Security best practices

Respond with a JSON object containing:
{
  "files": [
    {
      "path": "path/to/file.py",
      "content": "file content here",
      "description": "what this file does"
    }
  ],
  "setup_instructions": "How to set up and run",
  "dependencies": ["package1==1.0.0", "package2==2.0.0"]
}"""
        
        user_prompt = f"""Feature Request: {feature_request}

Requirements:
{json.dumps(spec, indent=2)}

Architecture:
{json.dumps(design, indent=2)}

Generate production-ready implementation code."""
        
        # Call AI
        response = await self._ai_complete(user_prompt, system_prompt, temperature=0.3)
        
        # Extract JSON
        implementation = self._extract_json(response)
        
        if not implementation:
            # Fallback
            implementation = {
                "files": [
                    {
                        "path": "main.py",
                        "content": f"# Implementation for: {feature_request}\n\ndef main():\n    # TODO: Implement feature\n    pass",
                        "description": "Main implementation file"
                    }
                ],
                "setup_instructions": "pip install -r requirements.txt",
                "dependencies": []
            }
        
        # Save each file
        artifacts = []
        for file_info in implementation.get("files", []):
            file_path = self._save_artifact(
                file_info.get("content", ""),
                file_info.get("path", "generated_code.py"),
                state,
            )
            artifacts.append(file_path)
        
        # Save dependencies
        if implementation.get("dependencies"):
            deps_content = "\n".join(implementation["dependencies"])
            deps_file = self._save_artifact(
                deps_content,
                "requirements.txt",
                state,
            )
            artifacts.append(deps_file)
        
        self.logger.info(
            "Code implementation generated",
            files_count=len(implementation.get("files", [])),
        )
        
        return {
            "implementation": implementation,
            "artifacts": artifacts,
            "summary": f"Generated {len(implementation.get('files', []))} code files",
        }
