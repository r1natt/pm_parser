from datetime import datetime

from enum import Enum
from typing import TypedDict
from sqlalchemy import (
    DateTime,
    Integer,
    String,
    JSON,
    ForeignKey
)
from engine import engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import insert


class ChampionshipsDict(TypedDict):
    CId: int
    championship_name: str
    championship_name_ru: str

class TournamentsDict(TypedDict):
    CId: str
    TId: str
    championship_name: str
    championship_name_ru: str
    tournament_name: str
    tournament_name_ru: str

class MatchStatus(Enum):
    PREMATCH = "Prematch"
    LIVE = "Live"
    ENDED = "Ended"

class MatchDict(TypedDict):
    CId: int
    TId: int
    match_id: int
    match_datetime: datetime
    parse_datetime: datetime
    status: MatchStatus
    first_club: str
    first_club_ru: str
    second_club: str
    second_club_ru: str
    coefficients: dict

class Base(DeclarativeBase):
    pass


class ChampionshipsTable(Base):
    """
    Championships - это страны, которые отображаются слева в стоблце, где еще 
    можно выбирать лиги по странам

    Championships - название во внутреннем апи
    """
    __tablename__ = "championships"

    id: Mapped[int] = mapped_column(primary_key=True)
    CId: Mapped[int] = mapped_column(Integer(), unique=True)
    championship_name = mapped_column(String(50))
    championship_name_ru = mapped_column(String(50))


class TournamentsTable(Base):
    """
    Tournaments - условно названия лиг(?, не уверен что это называется лиги)

    Tournaments - название во внутреннем апи
    """
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    CId: Mapped[int] = mapped_column(ForeignKey("championships.CId"))
    TId: Mapped[int] = mapped_column(Integer(), unique=True)
    championship_name: Mapped[str] = mapped_column(String(30))
    championship_name_ru: Mapped[str] = mapped_column(String(30))
    tournament_name: Mapped[str] = mapped_column(String(50))
    tournament_name_ru: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"League(id={self.id!r}, CId={self.CId!r}, country={self.coutry_ru!r}, league_name={self.league_name_ru!r})"

class MatchesTable(Base):
    __tablename__ = "matches"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    CId: Mapped[int] = mapped_column(ForeignKey("championships.CId"))
    TId: Mapped[int] = mapped_column(ForeignKey("tournaments.TId"))
    match_id: Mapped[int] = mapped_column(Integer(), unique=True)
    match_datetime: Mapped[datetime] = mapped_column(DateTime())
    parse_datetime: Mapped[datetime] = mapped_column(DateTime())
    status: Mapped[str] = mapped_column(String(15))
    first_club: Mapped[str] = mapped_column(String(50))
    first_club_ru: Mapped[str] = mapped_column(String(50))
    second_club: Mapped[str] = mapped_column(String(50))
    second_club_ru: Mapped[str] = mapped_column(String(50))
    coefficients: Mapped[float] = mapped_column(JSON)

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


Base.metadata.create_all(engine)

