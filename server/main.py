import os
import importlib
import sys
from fastapi import FastAPI

app = FastAPI()
directory = './apis/' # 无需修改
sys.path.append(os.path.abspath(directory))

for filename in os.listdir(directory):
    if filename.endswith('.py') and filename != "__init__.py":
        module_name = filename[:-3]
        module = importlib.import_module(module_name)
        if hasattr(module, 'register_routes'):
            module.register_routes(app) # 注册
