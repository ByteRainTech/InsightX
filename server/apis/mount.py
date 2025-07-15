from fastapi import APIRouter, Depends
import os
from typing import Optional
from utils.model.storage import share_model,model_exists
import torch
router = APIRouter()

@router.get("/mount/{source}")
def mount(source: str, name: str, path: str = None, model_path: str = None, model_class: str = None, args: dict = {}):
    match source: # 挂载方法
        case "torch": # TorchLoad
            if model_exists(name):
                return {"status": "error", "msg": "模型名已被占用，请取消挂载/修改名。"}
            if model_path==None:
                return {"status": "error", "msg": "请指定一个模型网络路径: model_path"}
            if model_class==None:
                return {"status": "error", "msg": "请指定一个模型入口: model_class"}
            if path==None:
                return {"status": "error", "msg": "目标文件不存在，请设置参数 path。"}
            if not os.path.exists(path):
                return {"status": "error", "msg": "模型文件不存在。"}
            model = globals()[model_class](**args)
            model.load_state_dict(torch.load(model_path))
            share_model(name=name,model=model)
            return {"status": "success", "msg": "ok!"}
    return {"message": f""}
def register_routes(app):
    app.include_router(router)
