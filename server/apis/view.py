from fastapi import APIRouter, Depends
import os
from typing import Optional
from utils.model.storage import share_model,model_exists,get_model
import torch
router = APIRouter()

@router.get("/view/{name}")
def view(name: str):
    if not model_exists(name):
        return {"status": "error", "msg": "模型不存在"}
    structure = get_model(name=name,view_as="structure")
    return {"status": "success", "msg": structure}
def register_routes(app):
    app.include_router(router)
