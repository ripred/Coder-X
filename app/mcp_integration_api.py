"""
API endpoints for MCP (Model Context Protocol) integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .mcp_integration import MCPClient

router = APIRouter()
mcp = MCPClient()

class ContextRequest(BaseModel):
    context_id: str
    data: Optional[dict] = None

@router.get("/mcp/context/{context_id}")
def get_context(context_id: str):
    ctx = mcp.get_context(context_id)
    if ctx is None:
        raise HTTPException(status_code=404, detail="Context not found or MCP server not configured.")
    return ctx

@router.post("/mcp/context/{context_id}")
def save_context(context_id: str, req: ContextRequest):
    if not mcp.save_context(context_id, req.data):
        raise HTTPException(status_code=500, detail="Failed to save context.")
    return {"success": True}

@router.post("/mcp/server")
def set_server_url(url: str):
    mcp.set_server_url(url)
    return {"success": True, "server_url": url}

@router.get("/mcp/server")
def get_server_url():
    return {"server_url": mcp.server_url}
