from typing import Any, ClassVar, Literal, LiteralString, Sequence, TypedDict

from pydantic import BaseModel, Field, create_model
from pydantic_core import ErrorDetails, InitErrorDetails, PydanticCustomError
from pydantic_core import ValidationError as PydanticValidationError


class CustomException(Exception):
    
    _schema: ClassVar[type[BaseModel] | None] = None
    
    def __init__(
            self,
            message: str,
            status_code: int = 500,
            headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.headers = headers

    @classmethod
    def schema(cls) -> type[BaseModel]:
        if cls._schema is not None:
            return cls._schema
        
        error_literal = Literal[cls.__name__]

        model = create_model(
            cls.__name__,
            error = (error_literal, Field(examples=[cls.__name__])),
            detail=(str, ...),
        )
        cls._schema = model
        return cls._schema

class BadRequest(CustomException):
    def __init__(self, message: str = "Bad request", status_code = 400) -> None:
        super().__init__(message, status_code)

class ResourceNotFound(CustomException):
    def __init__(self, message: str = "Not found", status_code = 404) -> None:
        super().__init__(message, status_code)

class Unauthorized(CustomException):
    def __init__(self, message: str = "Unauthorized", status_code = 401) -> None:
        super().__init__(
            message,
            status_code,
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

class Forbidden(CustomException):
    def __init__(self, message: str = "Forbidden", status_code = 403) -> None:
        super().__init__(message, status_code)


class ValidationError(TypedDict):
    loc: tuple[int | str, ...]
    msg: LiteralString
    type: LiteralString
    input: Any

class CustomRequestValidationError(CustomException):
    def __init__(self, errors: Sequence[ValidationError]) -> None:
        self._errors = errors

    def errors(self) -> list[ErrorDetails]:
        pydantic_errors: list[InitErrorDetails] = []
        for error in self._errors:
            pydantic_errors.append(
                {
                    "type": PydanticCustomError(error["type"], error["msg"]),
                    "loc": error["loc"],
                    "input": error["input"],
                }
            )
        pydantic_error = PydanticValidationError.from_exception_data(
            self.__class__.__name__, pydantic_errors
        )
        return pydantic_error.errors()
