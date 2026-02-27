import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Game(Base, TimestampMixin):
    __tablename__ = "games"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    room_code: Mapped[str] = mapped_column(String(10), unique=True)
    scoring_variant: Mapped[str] = mapped_column(String(20), default="standard")
    round_count: Mapped[int] = mapped_column(Integer)
    player_count: Mapped[int] = mapped_column(Integer)
    winner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="lobby")
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    participants: Mapped[list["GameParticipant"]] = relationship(back_populates="game")
    rounds: Mapped[list["GameRound"]] = relationship(back_populates="game")


class GameParticipant(Base):
    __tablename__ = "game_participants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    display_name: Mapped[str] = mapped_column(String(50))
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    seat_index: Mapped[int] = mapped_column(Integer)
    final_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    game: Mapped["Game"] = relationship(back_populates="participants")
    scores: Mapped[list["RoundScore"]] = relationship(back_populates="participant")


class GameRound(Base):
    __tablename__ = "game_rounds"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    game_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("games.id"))
    round_number: Mapped[int] = mapped_column(Integer)
    hand_size: Mapped[int] = mapped_column(Integer)
    trump_suit: Mapped[str | None] = mapped_column(String(10), nullable=True)
    dealer_seat: Mapped[int] = mapped_column(Integer)

    game: Mapped["Game"] = relationship(back_populates="rounds")
    scores: Mapped[list["RoundScore"]] = relationship(back_populates="round")


class RoundScore(Base):
    __tablename__ = "round_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    round_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("game_rounds.id"))
    participant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("game_participants.id"))
    bid: Mapped[int] = mapped_column(Integer)
    tricks_won: Mapped[int] = mapped_column(Integer, default=0)
    round_points: Mapped[int] = mapped_column(Integer, default=0)
    cumulative_score: Mapped[int] = mapped_column(Integer, default=0)

    round: Mapped["GameRound"] = relationship(back_populates="scores")
    participant: Mapped["GameParticipant"] = relationship(back_populates="scores")
