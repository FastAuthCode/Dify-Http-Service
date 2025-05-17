from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

import logging
from core.config import get_settings
from core.logging import setup_logging
from core.route_scanner import scan_routers
from utils.response import CustomResponse

settings = get_settings()

# 初始化日志系统
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Application starting...")
logger.debug(f"Current settings: {settings.json()}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 设置CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 全局扫描API路由
routers = scan_routers("api")
for router in routers:
    app.include_router(router, prefix=settings.API_V1_STR)


# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return CustomResponse.error(message=exc.detail, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return CustomResponse.error(message=str(exc), status_code=400)


@app.get("/")
async def root():
    return CustomResponse.success(data={"message": "Welcome to Dify HTTP Service"})
