from datetime import datetime

from enum import Enum
from typing import TypedDict
from sqlalchemy import (
    DateTime,
    Integer,
    Boolean,
    String,
    JSON,
    ForeignKey
)
from engine import engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import insert


class ChampionshipsDict(TypedDict):
    id: int
    name: str
    name_ru: str

class TournamentsDict(TypedDict):
    id: str
    c_id: str
    name: str
    name_ru: str

    matches_count: int

class MatchStatus(Enum):
    PREMATCH = "Prematch"
    LIVE = "Live"
    PASSED = "Passed"

class MatchDict(TypedDict):
    id: int
    c_id: int
    t_id: int
    match_datetime: datetime
    parse_datetime: datetime
    status: MatchStatus
    first_club: str
    first_club_ru: str
    second_club: str
    second_club_ru: str
    coefficients: dict

class LiveMatchDict(TypedDict):
    id: int
    status: str
    match_datetime: datetime
    first_club: str
    first_club_ru: str
    second_club: str
    second_club_ru: str
    coefficients: dict

class Base(DeclarativeBase):
    pass


"""
В sql таблицах championships и tournaments есть столбец is_active
Он обозначает есть ли тот или иной чемпионат или турнир в последнем ответе апи
Если есть - True, по этому чемпионату или турниру нужно будет дальше делать 
    запросы
Если нет - False, матчей в турнире, которого нет в ответе апи, точно нет, апи 
    ничего не выдаст на этот запрос
"""


class ChampionshipsTable(Base):
    """
    Championships - это страны, которые отображаются слева в стоблце, где еще 
    можно выбирать лиги по странам

    Championships - название во внутреннем апи
    """
    __tablename__ = "championships"

    id: Mapped[int] = mapped_column(primary_key=True)

    tournaments: Mapped[list["TournamentsTable"]] = relationship("TournamentsTable", back_populates="championship")
    matches: Mapped[list["MatchesTable"]] = relationship("MatchesTable", back_populates="championship")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    name = mapped_column(String(100))
    name_ru = mapped_column(String(100))


class TournamentsTable(Base):
    """
    Tournaments - условно названия лиг(?, не уверен что это называется лиги)

    Tournaments - название во внутреннем апи
    """
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    c_id: Mapped[int] = mapped_column(ForeignKey("championships.id"))

    championship: Mapped["ChampionshipsTable"] = relationship("ChampionshipsTable", back_populates="tournaments")
    matches: Mapped[list["MatchesTable"]] = relationship("MatchesTable", back_populates="tournament")

    name: Mapped[str] = mapped_column(String(100))
    name_ru: Mapped[str] = mapped_column(String(100))

class MatchesTable(Base):
    __tablename__ = "matches"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    c_id: Mapped[int] = mapped_column(ForeignKey("championships.id"))
    t_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"))

    championship: Mapped[ChampionshipsTable] = relationship(ChampionshipsTable, back_populates="matches")
    tournament: Mapped[TournamentsTable] = relationship(TournamentsTable, back_populates="matches")

    match_datetime: Mapped[datetime] = mapped_column(DateTime())
    parse_datetime: Mapped[datetime] = mapped_column(DateTime())
    status: Mapped[str] = mapped_column(String(15))
    first_club: Mapped[str] = mapped_column(String(100))
    first_club_ru: Mapped[str] = mapped_column(String(100))
    second_club: Mapped[str] = mapped_column(String(100))
    second_club_ru: Mapped[str] = mapped_column(String(100))
    coefficients: Mapped[float] = mapped_column(JSON)


Base.metadata.create_all(engine)

