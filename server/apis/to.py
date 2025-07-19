# 注: 请注意库调用模式
from fastapi import APIRouter, Depends
import os
from typing import Optional
import utils.model.storage as storage
import torch
router = APIRouter()

@router.get("/to/dtype/{name}/{dtype}")
def to_dtype(name: str, dtype: str):
    if not storage.model_exists(name):
        return {"status": "error", "msg": "模型不存在"}
    response = storage.to_dtype(name, dtype) # dtype转换结果
    if response == None:
        return {"status": "error", "msg": "不受支持的dtype"}
    elif response == False:
        return {"status": "error", "msg": "转换过程中出现问题"}
    return {"status": "success", "msg": "ok"}
def register_routes(app):
    app.include_router(router)
