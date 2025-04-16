from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
import os

class APIKeys(BaseModel):
    openai: Optional[str] = None
    anthropic: Optional[str] = None
    ollama: Optional[str] = None
    
    model_config = {"extra": "allow"}

class CoderXConfig(BaseModel):
    model: Optional[str] = None
    model_storage_path: str = Field(default_factory=lambda: os.path.expanduser("~/.coder_x_models"))
    api_keys: APIKeys = Field(default_factory=APIKeys)
    mcp_server: Optional[str] = None
    history_path: str = Field(default_factory=lambda: os.path.expanduser("~/.coder_x_history.json"))

    @field_validator("model_storage_path", mode="before")
    @classmethod
    def ensure_model_storage_path(cls, v):
        return v or os.path.expanduser("~/.coder_x_models")

    @field_validator("history_path", mode="before")
    @classmethod
    def ensure_history_path(cls, v):
        return v or os.path.expanduser("~/.coder_x_history.json")
