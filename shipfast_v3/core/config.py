"""
ShipFast v3.0 - Configuration Management
Loads and validates configuration from YAML and environment variables
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import structlog

logger = structlog.get_logger()


class Config:
    """Centralized configuration management"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config()
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._load_env_overrides()
        self._validate()
    
    def _find_config(self) -> str:
        """Find config.yaml in standard locations"""
        search_paths = [
            Path(__file__).parent / "config.yaml",
            Path.cwd() / "config" / "config.yaml",
            Path.cwd() / "shipfast_v3" / "config" / "config.yaml",
            Path.cwd() / "config.yaml",
        ]
        
        for path in search_paths:
            if path.exists():
                logger.info("Found config file", path=str(path))
                return str(path)
        
        raise FileNotFoundError("config.yaml not found in standard locations")
    
    def _load_config(self):
        """Load configuration from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info("Configuration loaded", file=self.config_path)
        except Exception as e:
            logger.error("Failed to load config", error=str(e))
            raise
    
    def _load_env_overrides(self):
        """Override config with environment variables"""
        # API key from environment
        api_key_env = self._config.get("ai", {}).get("api_key_env", "CEREBRAS_API_KEY")
        api_key = os.getenv(api_key_env)
        
        if api_key:
            if "ai" not in self._config:
                self._config["ai"] = {}
            self._config["ai"]["api_key"] = api_key
            logger.info("API key loaded from environment")
        
        # Port override
        port = os.getenv("PORT")
        if port:
            self._config["api"]["port"] = int(port)
    
    def _validate(self):
        """Validate required configuration"""
        required = [
            ("api", "host"),
            ("api", "port"),
            ("ai", "provider"),
            ("ai", "model"),
        ]
        
        for *path, key in required:
            current = self._config
            for p in path:
                current = current.get(p, {})
            
            if key not in current:
                raise ValueError(f"Missing required config: {'.'.join(path + [key])}")
        
        # Validate API key
        if not self._config.get("ai", {}).get("api_key"):
            logger.warning(
                "API key not found",
                env_var=self._config.get("ai", {}).get("api_key_env", "CEREBRAS_API_KEY")
            )
        
        logger.info("Configuration validated")
    
    def get(self, *path, default=None) -> Any:
        """Get configuration value by path"""
        current = self._config
        for key in path:
            if isinstance(current, dict):
                current = current.get(key, default)
            else:
                return default
        return current if current is not None else default
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.get("api", default={})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return self.get("ai", default={})
    
    def get_agent_config(self, agent_type: str, agent_name: str) -> Dict[str, Any]:
        """Get specific agent configuration"""
        return self.get("agents", agent_type, agent_name, default={})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.get("security", default={})
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration"""
        return self.get("storage", default={})
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """Get workflow configuration"""
        return self.get("workflow", default={})
    
    def is_agent_enabled(self, agent_type: str, agent_name: str) -> bool:
        """Check if an agent is enabled"""
        return self.get("agents", agent_type, agent_name, "enabled", default=True)
    
    def __repr__(self) -> str:
        return f"<Config loaded from {self.config_path}>"


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get or create global configuration instance"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reload_config(config_path: Optional[str] = None):
    """Reload configuration"""
    global _config
    _config = Config(config_path)
    logger.info("Configuration reloaded")
    return _config
