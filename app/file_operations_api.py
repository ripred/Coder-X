"""
API endpoints for file operations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from .file_operations import FileOps

router = APIRouter()
file_ops = FileOps()

class FilePathRequest(BaseModel):
    filepath: str

class FileWriteRequest(BaseModel):
    filepath: str
    content: str

@router.get("/file/read")
def read_file(filepath: str):
    content = file_ops.read_file(filepath)
    if content is None:
        raise HTTPException(status_code=404, detail="File not found.")
    return {"content": content}

@router.post("/file/write")
def write_file(req: FileWriteRequest):
    if not file_ops.write_file(req.filepath, req.content):
        raise HTTPException(status_code=500, detail="Write failed.")
    return {"success": True}

@router.post("/file/append")
def append_file(req: FileWriteRequest):
    if not file_ops.append_file(req.filepath, req.content):
        raise HTTPException(status_code=500, detail="Append failed.")
    return {"success": True}

@router.get("/file/exists")
def file_exists(filepath: str):
    return {"exists": file_ops.file_exists(filepath)}

@router.get("/file/explain")
def explain_code(filepath: str):
    explanation = file_ops.explain_code(filepath)
    if explanation is None:
        raise HTTPException(status_code=404, detail="File not found.")
    return {"explanation": explanation}

@router.get("/file/test")
def run_tests(test_path: str):
    output = file_ops.run_tests(test_path)
    return {"output": output}

@router.get("/file/lint")
def lint_code(filepath: str):
    output = file_ops.lint_code(filepath)
    return {"output": output}
