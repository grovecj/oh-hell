from pydantic import BaseModel


class CardSchema(BaseModel):
    suit: str
    rank: str


class PlayCardRequest(BaseModel):
    card: CardSchema


class PlaceBidRequest(BaseModel):
    bid: int


class CreateGameRequest(BaseModel):
    scoring_variant: str = "standard"
    hook_rule: bool = True
    turn_timer_seconds: int = 30
    max_players: int = 7
