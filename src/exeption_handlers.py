from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions import CustomException, CustomRequestValidationError


def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": type(exc).__name__, "detail": exc.message},
    )

async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError | CustomRequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": type(exc).__name__, "detail": jsonable_encoder(exc.errors())},
    )


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler # type: ignore
    )
    app.add_exception_handler(
        CustomRequestValidationError,
        request_validation_exception_handler # type: ignore
    )

    app.add_exception_handler(
        CustomException,
        custom_exception_handler # type: ignore
    )
