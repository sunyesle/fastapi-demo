from fastapi import Request, Response


CART_SESSION_COOKIE = "cart_session"
MAX_AGE = 60 * 60 * 24 * 7 # 7일


def get_cart_session_id(request: Request) -> str | None:
    return request.cookies.get(CART_SESSION_COOKIE)

def set_cart_session_cookie(
    response: Response,
    session_id: str
) -> None:
    response.set_cookie(
        key=CART_SESSION_COOKIE,
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=MAX_AGE
    )
