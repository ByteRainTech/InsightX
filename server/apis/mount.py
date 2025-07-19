"""
这个项目作者是PHP全栈，不是Python开发，如果项目风格和你的不同，见谅，能用就行。
"""
from fastapi import APIRouter, Depends
import os
from typing import Optional
from utils.model.storage import share_model,model_exists
import torch
import importlib.util
import json
import sys
router = APIRouter()

"""
* name -> 模型名
[+] path -> 模型目录
[+] model_path -> 模型文件目录(.py)
[+] model_class -> 模型调用的类
[+] 模型调用初始化的参数
"""
@router.get("/mount/{source}")
def mount(source: str, name: str, path: str = None, model_path: str = None, model_class: str = None, args: str = "{}"):
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
            preloaded = torch.load(path)
            args = json.loads(args)
            spec = importlib.util.spec_from_file_location("module_name", model_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            model_class = getattr(module, model_class)
            model = model_class(**args)
            model.load_state_dict(preloaded)
            share_model(name=name,model=model)
            return {"status": "success", "msg": "ok!"}
    return {"message": f""}
def register_routes(app):
    app.include_router(router)
