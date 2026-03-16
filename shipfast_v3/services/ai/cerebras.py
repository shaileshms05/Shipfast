"""
ShipFast v3.0 - Cerebras AI Client
Direct integration with Cerebras Cloud SDK - no LangChain dependencies
"""

from typing import List, Dict, Any, Optional
from cerebras.cloud.sdk import Cerebras
import os
import structlog

logger = structlog.get_logger()


class Message:
    """Simple message class"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class CerebrasClient:
    """
    Simple, direct Cerebras AI client
    No LangChain - just clean, direct API calls
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3.1-8b",
        temperature: float = 0.7,
        max_tokens: int = 8000,
    ):
        self.api_key = api_key or os.getenv("CEREBRAS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CEREBRAS_API_KEY not found. "
                "Get your free key at https://cloud.cerebras.ai/"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize Cerebras client with robust error handling
        # The Cerebras SDK has issues with proxies parameter from httpx
        import httpx
        original_init = httpx.Client.__init__
        
        def patched_init(self, *args, **kwargs):
            # Remove proxies if present
            kwargs.pop('proxies', None)
            return original_init(self, *args, **kwargs)
        
        # Temporarily patch httpx.Client to filter proxies
        httpx.Client.__init__ = patched_init
        
        try:
            self.client = Cerebras(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"Failed to initialize with api_key directly: {e}, trying alternative method")
            try:
                self.client = Cerebras()
                self.client.api_key = self.api_key
            except Exception as e2:
                logger.error(f"Failed to initialize Cerebras client (fallback): {e2}")
                raise
        finally:
            # Restore original
            httpx.Client.__init__ = original_init
        
        logger.info(
            "Cerebras client initialized",
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
    
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send chat completion request
        
        Args:
            messages: List of Message objects
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            Generated text response
        """
        try:
            # Convert messages to dict format
            formatted_messages = [m.to_dict() for m in messages]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=False,
            )
            
            content = response.choices[0].message.content
            
            logger.debug(
                "Chat completion successful",
                model=self.model,
                messages_count=len(messages),
                response_length=len(content),
            )
            
            return content
            
        except Exception as e:
            logger.error(
                "Chat completion failed",
                error=str(e),
                model=self.model,
            )
            raise
    
    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Simple text completion
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            Generated text response
        """
        messages = []
        
        if system_prompt:
            messages.append(Message("system", system_prompt))
        
        messages.append(Message("user", prompt))
        
        return self.chat(messages, temperature, max_tokens)
    
    async def achat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Async chat completion
        Note: Cerebras SDK doesn't have native async yet, so we use sync
        """
        return self.chat(messages, temperature, max_tokens)
    
    async def acomplete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Async text completion"""
        return self.complete(prompt, system_prompt, temperature, max_tokens)


def create_client(
    api_key: Optional[str] = None,
    model: str = "llama3.1-8b",
    temperature: float = 0.7,
    max_tokens: int = 8000,
) -> CerebrasClient:
    """Factory function to create Cerebras client"""
    return CerebrasClient(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


# Helper functions for common patterns
def system_user(system: str, user: str) -> List[Message]:
    """Create system + user message pair"""
    return [Message("system", system), Message("user", user)]


def user_only(content: str) -> List[Message]:
    """Create single user message"""
    return [Message("user", content)]
