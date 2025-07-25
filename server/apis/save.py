from fastapi import APIRouter, Depends
import os
from typing import Optional # 摆设
from utils.model.storage import save_model,model_exists
import torch
router = APIRouter()

@router.get("/save/{name}")
def save(name: str, path: str = None):
    if not model_exists(name):
        return {"status": "error", "msg": "模型不存在"}
    res = save_model(name=name,path=path)
    if res:
        return {"status": "success", "msg": "ok!"}
    return {"status": "error", "msg": "模型保存发生未知问题，请检查日志。"}

def register_routes(app):
    app.include_router(router)
