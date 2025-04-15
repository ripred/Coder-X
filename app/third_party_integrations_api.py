"""
API endpoints for third-party integrations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .third_party_integrations import ThirdPartyIntegration

router = APIRouter()
tpi = ThirdPartyIntegration()

class IntegrationRequest(BaseModel):
    service: str
    config: Optional[dict] = None

@router.post("/integration/connect")
def connect(req: IntegrationRequest):
    if not tpi.connect(req.service, req.config):
        raise HTTPException(status_code=400, detail="Connect failed.")
    return {"success": True}

@router.post("/integration/disconnect")
def disconnect(req: IntegrationRequest):
    if not tpi.disconnect(req.service):
        raise HTTPException(status_code=400, detail="Disconnect failed.")
    return {"success": True}

@router.get("/integration/list")
def list_integrations():
    return {"integrations": tpi.list_integrations()}
