from datetime import datetime

from enum import Enum
from typing import TypedDict
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    ARRAY,
    JSON
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
    country: str
    country_ru: str
    championship_name: str
    championship_name_ru: str

class MatchStatus(Enum):
    PREMATCH = "Prematch"
    LIVE = "Live"
    ENDED = "Ended"

class MatchDict(TypedDict):
    league_id: int
    match_id: int
    match_datetime: datetime
    parse_datetime: datetime
    status: MatchStatus
    first_club: str
    first_club_ru: str
    second_club: str
    second_club_ru: str
    total_coef: float
    is_more: bool
    coefficient: float

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
    CId: Mapped[int] = mapped_column(Integer())
    TId: Mapped[int] = mapped_column(Integer())
    championships_name: Mapped[str] = mapped_column(String(30))
    championships_name_ru: Mapped[str] = mapped_column(String(30))
    tournament_name: Mapped[str] = mapped_column(String(50))
    tournament_name_ru: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"League(id={self.id!r}, CId={self.CId!r}, country={self.coutry_ru!r}, league_name={self.league_name_ru!r})"

class MatchesTable(Base):
    __tablename__ = "matches"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    CId: Mapped[int] = mapped_column(Integer())
    TId: Mapped[int] = mapped_column(Integer())
    match_id: Mapped[int] = mapped_column(Integer())
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



with engine.connect() as conn:
    stmt = insert(MatchesTable).values(
        CId=1,
        TId=1,
        match_id=1,
        status="PREMATCH",
        first_club="asd",
        first_club_ru="asd",
        second_club="asd",
        second_club_ru="asd",
        coefficients={"asd":["asd"]}
    )
    conn.execute(stmt)
    conn.commit()
