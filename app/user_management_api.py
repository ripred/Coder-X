"""
API endpoints for user management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from .user_management import UserManager

router = APIRouter()
from functools import lru_cache

@lru_cache(maxsize=1)
def get_user_manager():
    return UserManager()

class LoginRequest(BaseModel):
    service: str
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

@router.get("/user/me")
def get_current_user(user_manager: UserManager = Depends(get_user_manager)):
    return user_manager.get_current_user()

@router.post("/user/login")
def login(req: LoginRequest, user_manager: UserManager = Depends(get_user_manager)):
    if not user_manager.login(req.service, token=getattr(req, 'token', None)):
        raise HTTPException(status_code=401, detail="Login failed.")
    return {"success": True}

@router.post("/user/logout")
def logout(req: LoginRequest, user_manager: UserManager = Depends(get_user_manager)):
    if not user_manager.logout(req.service):
        raise HTTPException(status_code=400, detail="Logout failed.")
    return {"success": True}
