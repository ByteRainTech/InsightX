import logging
import sys
import argparse

def env_check(log=False):
    if log!=False:
        logging.basicConfig(filename="env-report.log",level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.info("日志将会保存至 env-report.log")
    else:
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("正在验证必备环境...")
    try:
        import torch
        logger.info("Torch库已安装，版本："+torch.__version__)
    except ImportError:
        logging.error("未安装 Torch 库，InsightX的模型处理并不能正常运行。", exc_info=True)
    try:
        import fastapi
        logger.info("FastAPI 已安装，API应已被允许正常启动。")
    except ImportError:
        logger.error("未安装 FastAPI 库，InsightX的API并不能正常允许。", exc_info=True)
    logger.info("完成。")
if __name__ == '__main__':
    parser = argparse.ArgumentParser("环境检测工具")
    parser.add_argument("--save", action='store_true', help="将日志保存到文件")
    args = parser.parse_args()
    env_check(log=args.save)
