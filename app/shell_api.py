"""
API endpoints for shell integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from .shell_integration import ShellIntegration
from fastapi import Request

router = APIRouter()
shell = ShellIntegration()

class ShellCommandRequest(BaseModel):
    command: List[str]
    override: bool = False

@router.post("/shell/run")
def run_shell_command(req: ShellCommandRequest):
    # If override is True, allow any command (user has explicitly approved)
    if req.override:
        result = shell.run_command(req.command, override=True)
    else:
        result = shell.run_command(req.command)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
