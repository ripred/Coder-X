"""
API endpoints for using remote/free/no-API-key models
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class RemoteModelRequest(BaseModel):
    prompt: str
    model_name: Optional[str] = None

@router.post("/remote-model/generate")
def generate_with_remote_model(req: RemoteModelRequest):
    prompt = req.prompt
    model_name = req.model_name
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required.")
    return {
        "model": model_name or "dummy-free-model",
        "prompt": prompt,
        "output": f"[SIMULATED OUTPUT for '{prompt}' using model '{model_name or 'dummy-free-model'}']"
    }
