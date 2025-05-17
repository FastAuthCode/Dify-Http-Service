import uvicorn
import os
from dotenv import load_dotenv


def main():
    # 加载环境变量
    load_dotenv()

    # 设置调试环境变量
    os.environ["DEBUG"] = "True"

    # 配置uvicorn服务器
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 启用热重载
        reload_delay=0.25,  # 重载延迟
        log_level="debug",  # 设置日志级别为debug
        workers=1,  # debug模式使用单个worker
    )


if __name__ == "__main__":
    main()
