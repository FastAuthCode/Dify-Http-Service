from typing import Any, Optional, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse


class CustomResponse:
    @staticmethod
    def _convert_data(data: Any) -> Any:
        """递归转换BaseModel为可序列化格式"""
        if isinstance(data, BaseModel):
            return data.dict()
        elif isinstance(data, list):
            return [CustomResponse._convert_data(item) for item in data]
        elif isinstance(data, dict):
            return {k: CustomResponse._convert_data(v) for k, v in data.items()}
        return data

    @staticmethod
    def success(
            data: Any = None,
            message: str = "Success",
            status_code: int = 200
    ) -> JSONResponse:
        data = CustomResponse._convert_data(data) if data is not None else None
        return JSONResponse(
            content={
                "success": True,
                "message": message,
                "data": data
            },
            status_code=status_code
        )

    @staticmethod
    def error(
            message: str = "Error",
            status_code: int = 500,
            data: Optional[Any] = None
    ) -> JSONResponse:
        data = CustomResponse._convert_data(data) if data is not None else None
        return JSONResponse(
            content={
                "success": False,
                "message": message,
                "data": data
            },
            status_code=status_code
        )
