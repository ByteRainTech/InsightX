"""
当你怀疑这个项目是拿Ai写的时候
你就已经输了
作者手写的
True -> Success
False -> Failed
"""
import logging
import re
from typing import Any, ClassVar

import torch
from pydantic import BaseModel
from typing_extensions import Self

#   2025/7/25 致敬被弃用的Cache    #
# // // Depreciated WARNING // //  #
# from . import cache 被弃用力（悲 #
# // // Depreciated WARNING // //  #
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.DEBUG)
"""
模型共享区
"""

class MountedModel(BaseModel):
    name: str
    model: Any
    path: str
    structure: dict
    source: str

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any):
        setattr(self, key, value)

class MountedModelRepository:
    mounted_models: ClassVar[dict[str, MountedModel]] = {}
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def add_model(self, name: str, model: Any, path: str, structure: dict, source="torch"):
        if name not in self.mounted_models:
            self.mounted_models[name] = MountedModel(
                name=name, model=model, path=path, structure=structure, source=source
            )

    def get_model(self, name: str) -> MountedModel:
        return self.mounted_models[name]

    def get_model_or_default(self, name: str, default: Any = None) -> MountedModel | Any:
        return self.mounted_models.get(name, default)

    def exist(self, name: str) -> bool:
        return name in self.mounted_models

def modify_model_attr(name: str, key: str, value: Any) -> bool:
    repo = MountedModelRepository()
    try:
        setattr(repo.mounted_models[name], key, value)
        return True
    except AttributeError as e:
        return False

def save_model(name: str, path: str = None):
    # 不想在这里，我也不想在这里。
    # 但天黑的太快想走早就来不及。
    # 奥我爱你，可惜关系变成没关系。
    # 问题是没问题，于是我们继续。
    mounted_model = MountedModelRepository().get_model(name)
    match mounted_model["source"]:
        case "torch":
            # 如果你没指定，默认覆盖，这里注意。
            # 出现问题别找作者 QAQ
            path = mounted_model.path if path is None else path
            try:
                torch.save(mounted_model.model.state_dict(), path)
                if not modify_model_attr(name, "path", path):
                    logger.warning(f"{name} -> 模型保存后无法更新配置")
                logger.info(f"{name} -> 模型保存成功。")
                return True
            except Exception as e:
                logger.error(f"{name} -> 模型保存出现问题:\n{e}")
                return False
            

def mount_model(name: str, model: Any, path: str, source="torch"):
    model_pattern = r"(\w+)\s?\((.*)\)"
    layer_pattern = r"\(\w+\):\s?(\w+)\((.*?)\)"
    model_match = re.match(
        model_pattern, str(model).strip(), re.DOTALL
    )
    """
    这个模块容易出现问题，如果有问题，欢迎PR。
    """
    if not model_match:
        # 模型异常时通常会有这个问题
        structure = {"model": None, "structure": []}
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
            p.numel() * p.element_size() for p in model.parameters()
        )  # 参数获取
        dtype = str(next(model.parameters()).dtype)  # 获取dtype
        device = str(next(model.parameters()).device)  # 获取设备
        structure = {
            "model": model_name,
            "structure": layers,
            "param_size": param_size,
            "dtype": dtype,
            "device": device,
            "source": source,
        }
    MountedModelRepository().add_model(name=name, model=model, path=path, structure=structure, source=source)

def to_device(name: str, device: str):
    mounted_model = MountedModelRepository().get_model(name)
    match mounted_model["source"]:
        case "torch":
            try:
                device_obj = torch.device(device)
                mounted_model["model"] = mounted_model["model"].to(device_obj)
                if next(mounted_model["model"].parameters()).device != device_obj:
                    logger.error(f"{name} -> 设备移动后无法验证。")
                    return False
                structure = mounted_model["structure"].copy()
                structure["device"] = str(device_obj)
                if not modify_model_attr(name, "structure", structure):
                    logger.warning(f"{name} -> 模型转移设备后无法更新配置")
                logger.info(f"{name} -> 设备已移动至 {device_obj!s}")
                return True
            except Exception as e:
                logger.error(f"{name} -> 设备转换出现问题 : {e}")
                return False


def to_dtype(name: str, dtype: str):
    mounted_model = MountedModelRepository().get_model(name)
    match mounted_model.source:
        # Torch方式
        case "torch":
            import torch
            try:
                match dtype:
                    case "float16":
                        mounted_model.model.to(torch.float16)
                    case "float32":
                        mounted_model.model.to(torch.float32)
                    case "float64":
                        mounted_model.model.to(torch.float64)
                    case "bfloat16":
                        mounted_model.model.to(torch.bfloat16)
                    case _:  # 默认返回 None，代表未转换
                        return None
                if str(next(mounted_model.model.parameters()).dtype) == f"torch.{dtype}":
                    structure = mounted_model["structure"].copy()
                    structure["dtype"] = f"torch.{dtype}"
                    if not modify_model_attr(name, "structure", structure):
                        logger.warning(f"{name} -> 模型转换dtype后无法更新配置")
                    return True  # dtype更新成功
                else:
                    return False  # dtype未更新
            except Exception as e:
                logger.error(f"{name} -> dtype转换出现问题 : {e}")
                return False  # dtype未更新
        case _:
            return False


def model_exists(name: str):
    return MountedModelRepository().exist(name)

def get_model_list() -> list[str]:
    return list(MountedModelRepository.mounted_models.keys())

"""
* name -> 模型名
[+] view_as -> 模型返回格式
"""

def get_model(name: str, view_as=None):
    mounted_model = MountedModelRepository().get_model(name)
    # 以结构方式显示
    if view_as == "structure":
        return mounted_model["structure"]
    return mounted_model["model"]
