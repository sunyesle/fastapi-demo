from src.common.schemas import Schema

class Token(Schema):
    access_token: str
    token_type: str

class TokenData(Schema):
    username: str
