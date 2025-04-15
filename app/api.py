"""
API endpoints for Claude Code Python Assistant
"""
from fastapi import APIRouter, HTTPException
from .model_management import ModelManager

router = APIRouter()

model_manager = ModelManager()

@router.get("/models")
def list_all_models():
    """List all available models (local + Ollama)."""
    models = set(model_manager.list_local_models())
    try:
        models.update(model_manager.list_ollama_models())
    except Exception:
        pass
    return {"models": sorted(models)}

@router.get("/models/local")
def list_local_models():
    """List local models in the configured storage path."""
    return {"models": model_manager.list_local_models()}

@router.get("/models/ollama")
def list_ollama_models():
    """List Ollama models, if Ollama is installed."""
    return {"models": model_manager.list_ollama_models()}

@router.post("/models/storage-path")
def set_model_storage_path(path: str):
    """Set the local model storage path."""
    try:
        model_manager.set_model_storage_path(path)
        return {"success": True, "storage_path": path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/models/storage-path")
def get_model_storage_path():
    """Get the current local model storage path."""
    return {"storage_path": model_manager.storage_path}

@router.get("/models/active")
def get_active_model():
    return {"active_model": model_manager.get_active_model()}

@router.post("/models/active")
def set_active_model(model_name: str):
    try:
        model_manager.set_active_model(model_name)
        return {"success": True, "active_model": model_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
