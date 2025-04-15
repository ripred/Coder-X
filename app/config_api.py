"""
API endpoints for configuration management
"""
from fastapi import APIRouter, HTTPException
from .config import load_config, save_config

router = APIRouter()

@router.get("/config")
def get_config():
    return load_config()

@router.post("/config")
def update_config(config: dict):
    try:
        save_config(config)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
