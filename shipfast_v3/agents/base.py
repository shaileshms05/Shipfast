"""
ShipFast v3.0 - Base Agent Class
Foundation for all AI agents in the system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import structlog

from core.state import WorkflowState, Stage
from services.ai.cerebras import CerebrasClient, Message

logger = structlog.get_logger()


class BaseAgent(ABC):
    """
    Base class for all ShipFast agents
    Provides common functionality and structure
    """
    
    def __init__(
        self,
        name: str,
        ai_client: CerebrasClient,
        config: Dict[str, Any] = None,
    ):
        self.name = name
        self.ai_client = ai_client
        self.config = config or {}
        self.logger = logger.bind(agent=name)
        
        self.logger.info(f"{name} initialized")
    
    async def execute(
        self,
        state: WorkflowState,
        stage: Stage,
    ) -> Dict[str, Any]:
        """
        Execute the agent's task
        
        Args:
            state: Current workflow state
            stage: Stage to execute
        
        Returns:
            Dictionary with results and artifacts
        """
        self.logger.info(f"Starting {self.name}")
        stage.start()
        
        try:
            # Build context from previous stages
            context = self._build_context(state)
            
            # Execute agent-specific logic
            result = await self._execute_internal(state, context)
            
            # Extract artifacts
            artifacts = result.get("artifacts", [])
            
            # Mark stage as complete
            stage.complete(result, artifacts)
            
            self.logger.info(
                f"Completed {self.name}",
                artifacts_count=len(artifacts),
            )
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(
                f"Failed {self.name}",
                error=error_msg,
            )
            stage.fail(error_msg)
            raise
    
    @abstractmethod
    async def _execute_internal(
        self,
        state: WorkflowState,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Agent-specific execution logic
        Must be implemented by subclasses
        
        Args:
            state: Current workflow state
            context: Context from previous stages
        
        Returns:
            Dictionary with results and artifacts
        """
        pass
    
    def _build_context(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Build context from workflow state
        
        Args:
            state: Current workflow state
        
        Returns:
            Context dictionary for agent execution
        """
        context = {
            "workflow_id": state.id,
            "workflow_type": state.workflow_type.value,
            "request": state.request,
            "config": state.config,
            "previous_outputs": {},
        }
        
        # Add outputs from completed stages
        for stage in state.stages:
            if stage.output:
                context["previous_outputs"][stage.name] = stage.output
        
        return context
    
    def _get_previous_output(
        self,
        context: Dict[str, Any],
        stage_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get output from a specific previous stage"""
        return context.get("previous_outputs", {}).get(stage_name)
    
    async def _ai_complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Call AI for text completion
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
        
        Returns:
            Generated text
        """
        try:
            result = await self.ai_client.acomplete(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
            )
            
            self.logger.debug(
                "AI completion successful",
                prompt_length=len(prompt),
                response_length=len(result),
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "AI completion failed",
                error=str(e),
            )
            raise
    
    async def _ai_chat(
        self,
        messages: list,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Call AI with message history
        
        Args:
            messages: List of Message objects
            temperature: Optional temperature override
        
        Returns:
            Generated text
        """
        try:
            # Convert dict messages to Message objects if needed
            msg_objects = []
            for msg in messages:
                if isinstance(msg, dict):
                    msg_objects.append(Message(msg["role"], msg["content"]))
                else:
                    msg_objects.append(msg)
            
            result = await self.ai_client.achat(
                messages=msg_objects,
                temperature=temperature,
            )
            
            self.logger.debug(
                "AI chat successful",
                messages_count=len(messages),
                response_length=len(result),
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "AI chat failed",
                error=str(e),
            )
            raise
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from AI response
        Handles markdown code blocks and raw JSON
        """
        import json
        import re
        
        # Try to find JSON in markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to parse the whole text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON-like structure in text
        json_pattern2 = r'\{[^{}]*\{[^{}]*\}[^{}]*\}'
        match = re.search(json_pattern2, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        self.logger.warning("Could not extract JSON from response")
        return None
    
    async def _call_ai(self, system_prompt: str, user_prompt: str, temperature: Optional[float] = None) -> str:
        """
        Helper method for calling AI (wraps _ai_complete)
        This is for backward compatibility with Deploy agents
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Optional temperature override
        
        Returns:
            Generated text
        """
        return await self._ai_complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
    
    def _save_artifact(
        self,
        content: str,
        filename: str,
        state: WorkflowState,
    ) -> str:
        """
        Save artifact to disk
        
        Args:
            content: Content to save
            filename: Filename
            state: Workflow state
        
        Returns:
            Path to saved file
        """
        import os
        from pathlib import Path
        
        # Create artifacts directory
        artifacts_dir = Path("shipfast_output") / state.id
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = artifacts_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        
        # Add to state
        state.add_artifact(str(file_path))
        state.add_generated_file(filename)
        
        self.logger.info(
            "Artifact saved",
            filename=filename,
            size=len(content),
        )
        
        return str(file_path)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"
