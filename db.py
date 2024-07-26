from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from engine import engine


class Base(DeclarativeBase):
    pass


class Leagues(Base):
    __tablename__ = "leages"

    id: Mapped[int] = mapped_column(primary_key=True)
    CId: Mapped[int] = mapped_column(Integer())
    country: Mapped[str] = mapped_column(String(30))
    country_ru: Mapped[str] = mapped_column(String(30))
    league_name: Mapped[str] = mapped_column(String(50))
    league_name_ru: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"League(id={self.id!r}, CId={self.CId!r}, country={self.coutry_ru!r}, league_name={self.league_name_ru!r})"

class MatchBets(Base):
    __tablename__ = "match_bets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    CId: Mapped[int] = 
    match_datetime: Mapped[datetime] = mapped_column(DateTime())
    parse_datetime: Mapped[datetime] = mapped_column(DateTime())
    status: Mapped[str] = mapped_column(String(15))
    first_club: Mapped[str] = mapped_column(String(30))
    first_club_ru: Mapped[str] = mapped_column(String(30))
    second_club: Mapped[str] = mapped_column(String(30))
    second_club_ru: Mapped[str] = mapped_column(String(30))
    total_coef: Mapped[float] = mapped_column(Float())
    is_more: Mapped[bool] = mapped_column(Boolean())
    coefficient: Mapped[float] = mapped_column(Float())

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


Base.metadata.create_all(engine)

