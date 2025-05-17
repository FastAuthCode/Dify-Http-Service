import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.config import get_settings

settings = get_settings()


def setup_logging():
    """配置全局日志设置"""

    # 确保日志目录存在
    log_dir = Path(settings.LOG_PATH).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 创建格式化器
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # 文件处理器 - 带轮转(每个文件10MB，保留5个备份)
    file_handler = RotatingFileHandler(
        settings.LOG_PATH,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器
    if settings.LOG_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 设置第三方库日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


# 应用启动时调用此函数配置日志
setup_logging()
