from fastapi import APIRouter, Depends
import os
from typing import Optional
from utils.model.storage import share_model,model_exists,get_model,get_model_list
import torch
router = APIRouter()

@router.get("/view/{name}")
def view_structure(name: str):
    if not model_exists(name):
        return {"status": "error", "msg": "模型不存在"}
    structure = get_model(name=name,view_as="structure")
    return {"status": "success", "msg": structure}
@router.get("/view/")
def view_model_list():
    return {"status": "success", "models": get_model_list()}
def register_routes(app):
    app.include_router(router)
