import logging
import re
from typing import Any, ClassVar

import torch
from pydantic import BaseModel
from typing_extensions import Self

from . import cache

logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.DEBUG)
"""
模型共享区
"""


class SharedModel(BaseModel):
    name: str
    model: Any
    source: str

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any):
        setattr(self, key, value)


class SharedModelRepository:
    shared_models: ClassVar[dict[str, SharedModel]] = {}
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_model(self, name: str, model: Any, source="torch"):
        if name not in self.shared_models:
            self.shared_models[name] = SharedModel(
                name=name, model=model, source=source
            )

    def get_model(self, name: str) -> SharedModel:
        return self.shared_models[name]

    def get_model_or_default(self, name: str, default: Any = None) -> SharedModel | Any:
        return self.shared_models.get(name, default)

    def exist(self, name: str) -> bool:
        return name in self.shared_models


def share_model(name: str, model, source="torch"):
    SharedModelRepository().add_model(name, model, source)


def to_device(name: str, device: str):
    shared_model = SharedModelRepository().get_model(name)
    match shared_model["source"]:
        case "torch":
            try:
                device_obj = torch.device(device)
                shared_model["model"] = shared_model["model"].to(device_obj)
                if next(shared_model["model"].parameters()).device != device_obj:
                    logger.error(f"{name} -> 设备移动后无法验证。")
                    return False
                if cache.get(f"model_{name}_structure") is not None:
                    structure = cache.get(f"model_{name}_structure")  # 获取已有结构
                    assert structure is not None
                    structure["device"] = str(device_obj)  # 更新dtype缓存
                    cache.store(f"model_{name}_structure", structure)  # 更新结构
                logger.info(f"{name} -> 设备已移动至 {device_obj!s}")
                return True
            except Exception as e:
                logger.error(f"{name} -> 设备转换出现问题 : {e}")
                return False


def to_dtype(name: str, dtype: str):
    shared_model = SharedModelRepository().get_model(name)
    match shared_model.source:
        # Torch方式
        case "torch":
            import torch

            try:
                match dtype:
                    case "float16":
                        shared_model.model.to(torch.float16)
                    case "float32":
                        shared_model.model.to(torch.float32)
                    case "float64":
                        shared_model.model.to(torch.float64)
                    case "bfloat16":
                        shared_model.model.to(torch.bfloat16)
                    case _:  # 默认返回 None，代表未转换
                        return None
                if str(next(shared_model.model.parameters()).dtype) == f"torch.{dtype}":
                    if cache.get(f"model_{name}_structure") is not None:
                        structure = cache.get(f"model_{name}_structure")  # 获取已有结构
                        assert structure is not None
                        structure["dtype"] = f"torch.{dtype}"  # 更新dtype缓存
                        cache.store(f"model_{name}_structure", structure)  # 更新结构
                    return True  # dtype更新成功
                else:
                    return False  # dtype未更新
            except Exception as e:
                logger.error(f"{name} -> dtype转换出现问题 : {e}")
                return False  # dtype未更新
        case _:
            return False


def model_exists(name: str):
    return SharedModelRepository().exist(name)


def get_model_list() -> list[str]:
    return list(SharedModelRepository.shared_models.keys())


"""
* name -> 模型名
[+] view_as -> 模型返回格式
"""


def get_model(name: str, view_as=None):
    shared_model = SharedModelRepository().get_model(name)
    # 以结构方式显示
    if view_as == "structure":
        if cache.get(f"model_{name}_structure") is not None:
            return cache.get(f"model_{name}_structure")
        model_pattern = r"(\w+)\s?\((.*)\)"
        layer_pattern = r"\(\w+\):\s?(\w+)\((.*?)\)"
        model_match = re.match(
            model_pattern, str(shared_model["model"]).strip(), re.DOTALL
        )
        """
                这个模块容易出现问题，如果有问题，欢迎PR。
                """
        if not model_match:
            # 模型异常时通常会有这个问题
            return {"model": None, "structure": []}
        else:
            model_name = model_match.group(1)
            structure_str = model_match.group(2)
            layers = []
            for layer in re.finditer(layer_pattern, structure_str):
                layer_type = layer.group(1)
                params = layer.group(2)
                param_dict = {}
                if params:
                    for param in params.split(","):
                        key, value = param.split("=")
                        param_dict[key.strip()] = value.strip()
                layers.append({"layer_type": layer_type, "parameters": param_dict})
            param_size = sum(
                p.numel() * p.element_size() for p in shared_model["model"].parameters()
            )  # 参数获取
            dtype = str(next(shared_model["model"].parameters()).dtype)  # 获取dtype
            device = str(next(shared_model["model"].parameters()).device)  # 获取设备
            data = {
                "model": model_name,
                "structure": layers,
                "param_size": param_size,
                "dtype": dtype,
                "device": device,
                "source": shared_model["source"],
            }
            cache.store(f"model_{name}_structure", data)
            return data
    return shared_model["model"]
