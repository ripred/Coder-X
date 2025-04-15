"""
Entry point for Coder-X (FastAPI backend)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Coder-X")

# CORS for CLI or browser frontend extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Coder-X API is running."}

from .api import router as api_router
from .config_api import router as config_router
from .remote_model_api import router as remote_model_router
from .file_operations_api import router as file_router
from .shell_api import router as shell_router
from .session_history_api import router as history_router
from .user_management_api import router as user_router
from .third_party_integrations_api import router as integrations_router
from .mcp_integration_api import router as mcp_router

app.include_router(api_router)
app.include_router(config_router)
app.include_router(remote_model_router)
app.include_router(file_router)
app.include_router(shell_router)
app.include_router(history_router)
app.include_router(user_router)
app.include_router(integrations_router)
app.include_router(mcp_router)
