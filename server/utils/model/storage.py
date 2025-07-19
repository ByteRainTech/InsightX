import re
from fastapi import APIRouter, Depends
from . import cache
"""
模型共享区
"""
def share_model(name: str, model, source="torch"):
    global shared_models
    if 'shared_models' not in globals():
        shared_models = [{
            "name": name,
            "model": model,
            "source": source}]
        return True
    shared_models.append({
        "name": name,
        "model": model,
        "source": source
        })
def to_dtype(name: str, dtype: str):
    global shared_models
    for shared_model in shared_models:
        if shared_model["name"] == name:
            if shared_model["source"] == "torch":
                import torch
                try:
                    match dtype:
                        case "float16":
                            shared_model["model"].to(torch.float16)
                        case "float32":
                            shared_model["model"].to(torch.float32)
                        case "float64":
                            shared_model["model"].to(torch.float64)
                        case "bfloat16":
                            shared_model["model"].to(torch.bfloat16)
                        case _: # 默认返回 None，代表未转换
                            return None
                    if str(next(shared_model["model"].parameters()).dtype) == f"torch.{dtype}":
                        if cache.get(f"model_{name}_structure")!=None:
                            structure = cache.get(f"model_{name}_structure") # 获取已有结构
                            structure["dtype"] = f"torch.{dtype}" # 更新dtype缓存
                            cache.store(f"model_{name}_structure", structure) # 更新结构
                        return True # dtype更新成功
                    else:
                        return False # dtype未更新
                except Exception as e:
                    print(f"{name}::dtype转换出现问题 : {e}")
                    return False # dtype未更新
def model_exists(name: str):
    global shared_models
    if 'shared_models' not in globals():
        return False
    for shared_model in shared_models:
        if shared_model["name"] == name:
            return True
    return False
def get_model_list():
    global shared_models
    if 'shared_models' not in globals():
        return []
    model_list = []
    for shared_model in shared_models:
        model_list.append(shared_model["name"])
    return model_list
"""
* name -> 模型名
[+] view_as -> 模型返回格式
"""
def get_model(name: str, view_as=None):
    global shared_models
    if 'shared_models' not in globals():
        return None
    for shared_model in shared_models:
        if shared_model["name"] == name:
            # 以结构方式显示
            if view_as=="structure":
                if cache.get(f"model_{name}_structure")!=None:
                    return cache.get(f"model_{name}_structure")
                model_pattern = r"(\w+)\s?\((.*)\)"
                layer_pattern = r"\(\w+\):\s?(\w+)\((.*?)\)"
                model_match = re.match(model_pattern, str(shared_model["model"]).strip(), re.DOTALL)
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
                        layers.append({
                            "layer_type": layer_type,
                            "parameters": param_dict
                        })
                    param_size = sum(p.numel() * p.element_size() for p in shared_model["model"].parameters()) # 参数获取
                    dtype = str(next(shared_model["model"].parameters()).dtype) # 获取dtype
                    device = str(next(shared_model["model"].parameters()).device) # 获取设备
                    data = {
                        "model": model_name,
                        "structure": layers,
                        "param_size": param_size,
                        "dtype": dtype,
                        "device": device,
                        "source": shared_model["source"]
                    }
                    cache.store(f"model_{name}_structure", data)
                    return data
            return shared_model["model"]
