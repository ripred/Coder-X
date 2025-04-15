"""
API endpoints for session/history management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .session_history import SessionHistory

router = APIRouter()
history = SessionHistory()

class HistoryEntryRequest(BaseModel):
    entry: dict

@router.get("/history")
def get_history():
    return {"history": history.load()}

@router.post("/history/append")
def append_history(req: HistoryEntryRequest):
    history.append(req.entry)
    return {"success": True}

@router.post("/history/clear")
def clear_history():
    history.clear()
    return {"success": True}

@router.post("/history/export")
def export_history(export_path: str):
    if not history.export(export_path):
        raise HTTPException(status_code=500, detail="Export failed.")
    return {"success": True}
