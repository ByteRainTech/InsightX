# 注: 请注意库调用模式
from fastapi import APIRouter

import utils.model.storage as storage

router = APIRouter()


@router.get("/to/dtype/{name}/{dtype}")
def to_dtype(name: str, dtype: str):
    if not storage.model_exists(name):
        return {"status": "error", "msg": "模型不存在"}
    response = storage.to_dtype(name, dtype)  # dtype转换结果
    if response is None:
        return {"status": "error", "msg": "不受支持的dtype"}
    elif not response:
        return {"status": "error", "msg": "转换过程中出现问题"}
    return {"status": "success", "msg": "ok"}


@router.get("/to/device/{name}/{device}")
def to_device(name: str, device: str):
    if not storage.model_exists(name):
        return {"status": "error", "msg": "模型不存在"}
    response = storage.to_device(name, device)
    if response:
        return {"status": "success", "msg": "ok"}
    return {"status": "error", "msg": f"设备 {device} 不受支持。"}


def register_routes(app):
    app.include_router(router)
