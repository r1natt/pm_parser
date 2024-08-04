from datetime import datetime, timedelta
from enum import Enum

from requests import Session
from pprint import pprint
from logger import general_log, reqs_log
from sqlalchemy import insert, select, update, delete, or_
import traceback
from engine import engine
from tables import (
    Base, 
    ChampionshipsTable,
    TournamentsTable,
    MatchesTable,

    ChampionshipsDict,
    TournamentsDict,
    MatchStatus,
    MatchDict, 
)
Base.metadata.create_all(engine)


class DB:
    def __init__(self):
        pass

    def insert(self, stmt):
        with engine.connect() as conn:
            conn.execute(stmt)
            conn.commit()

    def update(self, stmt):
        pass

    def delete(self, stmt):
        pass

    def save_few_matches(self, matches_list):
        for match in matches_list:
            self.save_matches(match)

    def save_matches(self, match_bets_dict: MatchDict):
        with engine.connect() as conn:
            stmt = insert(MatchesTable).values(
                league_id=match_bets_dict["league_id"],
                match_id=match_bets_dict["match_id"],
                match_datetime=match_bets_dict["match_datetime"],
                parse_datetime=match_bets_dict["parse_datetime"],
                status=match_bets_dict["status"].value,
                first_club=match_bets_dict["first_club"],
                first_club_ru=match_bets_dict["first_club_ru"],
                second_club=match_bets_dict["second_club"],
                second_club_ru=match_bets_dict["second_club_ru"],
                total_coef=match_bets_dict["total_coef"],
                is_more=match_bets_dict["is_more"],
                coefficient=match_bets_dict["coefficient"]
            )
            conn.execute(stmt)
            conn.commit()


class ChampionshipsDB:
    def is_championship_in_db(self, c_id, name):
        with engine.connect() as conn:
            stmt = (select(ChampionshipsTable).
                    where(ChampionshipsTable.id == c_id)
                    )
            result = conn.execute(stmt).all()
            if len(result) != 0:
                result = result[0]
                if result[1] == name:
                    return True if len(result) != 0 else False
                else:
                    return "updated"
            else:
                return False

    def update_championships(self, championships_response):
        for championship in championships_response:
            _id = championship["id"]
            name = championship["name"]
            name_ru = championship["name_ru"]
            is_championship_in_db = self.is_championship_in_db(_id, name)
            if is_championship_in_db == "updated":
                with engine.connect() as conn:
                    stmt = (update(ChampionshipsTable).
                            where(ChampionshipsTable.id == _id).
                            values(name=name, name_ru=name_ru)
                            )
                    conn.execute(stmt)
                    conn.commit()
            elif not(is_championship_in_db):
                with engine.connect() as conn:
                    stmt = (insert(ChampionshipsTable).
                            values(
                                id=championship["id"],
                                name=championship["name"],
                                name_ru=championship["name_ru"]
                                )
                            )
                    conn.execute(stmt)
                    conn.commit()
            else:
                pass


class TournamentsDB:
    def _is_tournament_in_db(self, name):
        with engine.connect() as conn:
            stmt = (select(TournamentsTable).
                    where(TournamentsTable.name == name)
                    )
            result = conn.execute(stmt).all()
            return True if len(result) != 0 else False

    def get_t_ids_by_c_ids(self, c_ids: list):
        with engine.connect() as conn:
            stmt = (select(TournamentsTable.id).
                    where(TournamentsTable.c_id.in_(c_ids))
                    )
            result = [_id[0] for _id in conn.execute(stmt).all()]
            return result

    def save_new_tournametns(self, tournaments_response: list[TournamentsDict]):
        for tournament in tournaments_response:
            with engine.connect() as conn:
                if not self._is_tournament_in_db(tournament["name"]):

                    stmt = insert(TournamentsTable).values(
                        id=tournament["id"],
                        c_id=tournament["c_id"],
                        name=tournament["name"],
                        name_ru=tournament["name_ru"]
                    )
                    conn.execute(stmt)
                    conn.commit()


class MatchesDB:
    def get_existing_match(self, _id):
        with engine.connect() as conn:
            stmt = (select(MatchesTable).
                    where(MatchesTable.id==_id)
                    )
            return conn.execute(stmt).all()

    def get_cid_by_tid(self, t_id):
        with engine.connect() as conn:
            stmt = (select(TournamentsTable.c_id).
                    where(TournamentsTable.id == t_id)
                    )
            return conn.execute(stmt).first()[0]

    def _is_match_in_db(self, _id):
        return True if len(self.get_existing_match(_id)) != 0 else False

    def save_new_coefficient(self, _id, coefs):
        with engine.connect() as conn:
            stmt = (update(MatchesTable).
                    where(MatchesTable.id == _id).
                    values(coefficients = coefs)
                    )
            conn.execute(stmt)
            conn.commit()

    def update_existing_match(self, match):
        approach = timedelta(minutes=3)

        td2d = timedelta(days=2)
        td1d = timedelta(days=1)
        td3h = timedelta(hours=3)
        td50m = timedelta(minutes=50)
        td5m = timedelta(minutes=5)

        mdt = match["match_datetime"]
    
        existing_match_coefs = self.get_existing_match(match["id"])[0][-1]
        # parsing_coefs = {
        #         "total": match["coefficients"][0],
        #         "is_more": match["coefficients"][1],
        #         "coefficient": match["coefficients"][2],
        #         "timestamp": datetime.timestamp(datetime.now())
        # }
        coefficients = {
            "coefficients": match["coefficients"],
            "timestamp": datetime.timestamp(datetime.now())
        }

        if mdt - td2d > datetime.now():
            if "open" not in existing_match_coefs.keys():
                coef_key = "open"
            else:
                coef_key = -1
        elif (mdt - td2d - approach) <= datetime.now() <= (mdt - td2d + approach):
            coef_key = "2d"
        elif (mdt - td1d - approach) <= datetime.now() <= (mdt - td1d + approach):
            coef_key = "1d"
        elif (mdt - td3h - approach) <= datetime.now() <= (mdt - td3h + approach):
            coef_key = "3h"
        elif (mdt - td50m - approach) <= datetime.now() <= (mdt - td50m + approach):
            coef_key = "50m"
        elif (mdt - td5m - approach) <= datetime.now() <= (mdt - td5m + approach):
            coef_key = "5m"
        else:
            coef_key = -1

        if coef_key != -1:
            if coef_key not in existing_match_coefs.keys():
                existing_match_coefs["prematch"][coef_key] = coefficients

                general_log.debug(f"Update coefs: {match["id"]} {existing_match_coefs}")
                self.save_new_coefficient(match["id"], existing_match_coefs)

    def save_n_update_matches(self, matches_response):
        for match in matches_response:
            with engine.connect() as conn:
                if not self._is_match_in_db(match["id"]):

                    c_id = self.get_cid_by_tid(match["t_id"])
                    stmt = insert(MatchesTable).values(
                        id=match["id"],
                        c_id=c_id,
                        t_id=match["t_id"],
                        match_datetime=match["match_datetime"],
                        parse_datetime=match["parse_datetime"],
                        status=match["status"],
                        first_club=match["first_club"],
                        first_club_ru=match["first_club_ru"],
                        second_club=match["second_club"],
                        second_club_ru=match["second_club_ru"],
                        coefficients={"prematch": {}, "live": {}}
                    )
                    """
                    В самом объекте MatchDict есть коэффициенты в coefficients,
                    Но они пока не соответствуют формату, 
                    
                    при первом добавлении матча в бд coefficients передается 
                    как пустой словарь, а потом я вызываю функцию 
                    update_existing_match которая знает как управлятсья с 
                    коэффициентами
                    """
                    conn.execute(stmt)
                    conn.commit()

                self.update_existing_match(match)
                # self.change_status_passed_matches()


class LiveDB:
    def get_match_status_by_id(self, _id):
        try:
            with engine.connect() as conn:
                stmt = (select(MatchesTable.status).
                        where(MatchesTable.id == _id)
                        )
                return conn.execute(stmt).first()
        except Exception:
            general_log.error(traceback.format_exc())

    def is_match_in_db(self, _id):
        with engine.connect() as conn:
            stmt = (select(MatchesTable).
                    where(MatchesTable.id == _id))
            return True if len(conn.execute(stmt).all()) != 0 else False

    def update_status_to_live(self, _id):
        try:
            with engine.connect() as conn:
                stmt = (update(MatchesTable).
                        where(MatchesTable.id == _id).
                        values(status = MatchStatus.LIVE.value)
                        )
                conn.execute(stmt)
                conn.commit()
        except Exception:
            general_log.error(traceback.format_exc())

    def update_statuses_to_passed(self, _ids):
        with engine.connect() as conn:
            stmt = (update(MatchesTable).
                    where(MatchesTable.id.not_in(_ids)).
                    where(MatchesTable.match_datetime < datetime.now()).
                    values(status = MatchStatus.PASSED.value))
            conn.execute(stmt)
            conn.commit()

    def get_last_parse_datetime_n_coefs(self, _id):
        with engine.connect() as conn:
            stmt = (select(MatchesTable.last_live_parse_datetime, MatchesTable.coefficients).
                    where(MatchesTable.id == _id))
            return conn.execute(stmt).first()

    def save_live_coefs(self, coefs, _id):
        with engine.connect() as conn:
            stmt = (update(MatchesTable).
                    where(MatchesTable.id == _id).
                    values(last_live_parse_datetime = datetime.now(),
                           coefficients=coefs)
                    )
            conn.execute(stmt)
            conn.commit()
        
    def check_for_break(self, match):
        try:
            if match["status"] == "Перерыв":
                tdelta5m = timedelta(minutes=5)
                tdelta10m = timedelta(minutes=10)
                tdelta15m = timedelta(minutes=15)
                tdelta10s = timedelta(seconds=10)

                coefficients = {
                    "coefficients": match["coefficients"],
                    "timestamp": datetime.timestamp(datetime.now())
                }

                last_update_datetime, coefs = self.get_last_parse_datetime_n_coefs(match["id"])
                coef_key = ''
                if "open" not in coefs["live"]:
                    coef_key = "open"
                elif "5m" not in coefs["live"]:
                    if last_update_datetime + tdelta5m - tdelta10s <= datetime.now(): # <= last_update_datetime + tdelta5m - tdelta10s:
                        coef_key = "5m"
                elif "10m" not in coefs["live"]:
                    if last_update_datetime + tdelta10m - tdelta10s <= datetime.now(): # <= last_update_datetime + tdelta10m - tdelta10s:
                        coef_key = "10m"
                elif "15m" not in coefs["live"]:
                    if last_update_datetime + tdelta15m - tdelta10s <= datetime.now(): # <= last_update_datetime + tdelta15m - tdelta10s:
                        coef_key = "15m"

                if coef_key != '':
                    coefs["live"][coef_key] = coefficients
                    self.save_live_coefs(coefs, match["id"])
                    reqs_log.debug(f"Коэффициенты {match["id"]} в перерыве {coef_key}: {coefs["live"]}")
        except Exception:
            reqs_log.error(traceback.format_exc())

    def handle_live_matches(self, live_list):
        for live_match in live_list:
            _id = live_match["id"]

            status_in_db = self.get_match_status_by_id(_id)
            if status_in_db is not None:
                print(_id, live_match["status"], status_in_db[0])
            else:
                pass
                # print(_id, -1)
            if self.is_match_in_db(_id):
                self.check_for_break(live_match)

            if live_match["status"] != "Событие не началось":
                self.update_status_to_live(_id)

        _ids = [live_match["id"] for live_match in live_list]
        self.update_statuses_to_passed(_ids)


class GSDB:
    def get_matches(self):
        with engine.connect() as conn:
            stmt = (
                select(
                    MatchesTable.id,
                    MatchesTable.t_id,
                    MatchesTable.c_id,
                    ChampionshipsTable.name_ru,
                    TournamentsTable.name_ru,
                    MatchesTable.first_club_ru,
                    MatchesTable.second_club_ru,
                    MatchesTable.match_datetime,
                    MatchesTable.coefficients,
                    MatchesTable.status
                ).
                where(
                    or_(
                        MatchesTable.status == MatchStatus.PREMATCH.value, 
                        MatchesTable.status == MatchStatus.LIVE.value
                        )
                    ).
                join(
                    TournamentsTable,
                    MatchesTable.t_id == TournamentsTable.id
                ).
                join(
                    ChampionshipsTable, 
                    MatchesTable.c_id == ChampionshipsTable.id
                ).
                order_by(
                    MatchesTable.match_datetime.asc(),
                    MatchesTable.status.asc()         
                )
            )
            return conn.execute(stmt).all()

