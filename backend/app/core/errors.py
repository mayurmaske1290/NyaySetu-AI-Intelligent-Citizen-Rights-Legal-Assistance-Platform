from typing import Any, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiError(BaseModel):
    detail: str
    code: str
    retryable: bool = False
    demo_mode: bool = False


class ControlledError(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str, retryable: bool = False):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
        self.retryable = retryable


async def controlled_error_handler(request: Request, exc: ControlledError) -> JSONResponse:
    body = ApiError(
        detail=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        code=exc.code,
        retryable=exc.retryable,
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    body = ApiError(
        detail="Something went wrong. You can retry, continue offline, or cancel.",
        code="INTERNAL_ERROR",
        retryable=True,
    )
    return JSONResponse(status_code=500, content=body.model_dump())
