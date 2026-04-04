from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions import CustomException


def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": type(exc).__name__, "detail": exc.message},
    )

def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        CustomException,
        custom_exception_handler # type: ignore
    )
