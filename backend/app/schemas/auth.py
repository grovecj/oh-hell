from pydantic import BaseModel


class AnonymousResponse(BaseModel):
    token: str
    user_id: str
    display_name: str


class TokenResponse(BaseModel):
    token: str
