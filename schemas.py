from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel

class ModelConfig(BaseModel):
    provider: Literal['gemini', 'claude', 'openai', 'azure','groq']
    model_id: str
    api_key: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    azure_endpoint: Optional[str] = None
    api_version: Optional[str] = None

class AgentNodeConfig(BaseModel):
    model: ModelConfig
    tools: List[str] = []
    system_prompt: Optional[str] = None
    markdown: bool = True
    stream: bool = False

class AgentRunRequest(BaseModel):
    """Unified request with all agent configuration"""
    prompt: str
    model: ModelConfig
    previous_node_output: Optional[str] = None
    mcp_config: Optional[Dict[str, Any]] = None
    native_tools: Optional[List[str]] = []
    system_prompt: Optional[str] = None
    markdown: bool = True
