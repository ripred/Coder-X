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
    from app.config_schema import CoderXConfig
    import logging
    try:
        # Validate and convert dict to CoderXConfig before saving
        validated = CoderXConfig.model_validate(config)
        save_config(validated)
        logging.info(f"Config updated and saved: {validated}")
        return {"success": True}
    except Exception as e:
        logging.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=400, detail=str(e))
