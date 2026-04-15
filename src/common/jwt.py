from datetime import timedelta
from typing import Any

import jwt

from src.common.utils import utc_now


DEFAULT_EXPIRATION = timedelta(minutes=15)
ALGORITHM = "HS256"

def decode(
    *,
    token: str,
    secret: str,
) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=[ALGORITHM])

def encode(
    *,
    data: dict[str, Any],
    secret: str,
    expires_delta: timedelta | None = DEFAULT_EXPIRATION,
) -> str:
    to_encode = data.copy()

    expires_delta = expires_delta or DEFAULT_EXPIRATION
    expire = utc_now() + expires_delta
    
    to_encode["exp"] = expire
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)
