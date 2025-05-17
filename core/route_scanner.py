import importlib
import os

from fastapi import APIRouter


def scan_routers(directory: str):
    routers = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                # 构建模块路径
                module_path = os.path.join(root, file).replace(os.path.sep, ".")[:-3]
                try:
                    # 导入模块
                    module = importlib.import_module(module_path)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        # 检查是否为 APIRouter 实例
                        if isinstance(attr, APIRouter):
                            routers.append(attr)
                except ImportError:
                    continue
    return routers
