from typing import ClassVar, Literal

from pydantic import BaseModel, Field, create_model


class CustomException(Exception):
    
    _schema: ClassVar[type[BaseModel] | None] = None
    
    def __init__(
            self,
            message: str,
            status_code: int = 500,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

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


class ResourceNotFound(CustomException):
    def __init__(self, message: str = "Not found", status_code = 404) -> None:
        super().__init__(message, status_code)
