from datetime import datetime, timedelta
from enum import Enum

from requests import Session
from pprint import pprint
from sqlalchemy import insert, select, update, delete

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
    def __init__(self):
        pass

    def get_saved_championships(self):
        return_list = []

        with engine.connect() as conn:
            stmt = select(ChampionshipsTable)
            championships = conn.execute(stmt).all()

            for championship in championships:
                return_list.append(
                    ChampionshipsDict(
                        CId=championship[1],
                        championship_name=championship[2],
                        championship_name_ru=championship[3]
                    )
                )
            return return_list

    def championship_difference_new(self, saved_championships_names, championships_response_names):
        # new_championships - если появились новые чемпионаты, я получаю их список
        new_championships = list(championships_response_names.difference(saved_championships_names))
        return new_championships

    def championship_difference_updated(self, 
                                        saved_championships,
                                        saved_championships_names,
                                        championships_response,
                                        championships_response_names):
        updated_id_championships = []
        championships_intersection = list(saved_championships_names.intersection(championships_response_names))

        saved_championships = {
                championship["championship_name"]: championship["CId"] 
                for championship in saved_championships
        }

        championships_response = {
                championship["championship_name"]: championship["CId"]
                for championship in championships_response
        }

        for championship_name in championships_intersection:
            id_saved_championships = saved_championships[championship_name]
            id_championships_response = championships_response[championship_name]
            if id_saved_championships != id_championships_response:
                updated_id_championships.append(championship_name)

        return updated_id_championships

    def championship_difference_deleted(self, saved_championships_names, championships_response_names):
        # new_championships - если появились новые чемпионаты, я получаю их список
        deleted_championships = list(saved_championships_names.difference(championships_response_names))
        return deleted_championships

    def championships_difference(self, 
                                 saved_championships: list[ChampionshipsDict],
                                 championships_response: list[ChampionshipsDict]):
        saved_championships_names = set(
                [championship["championship_name"] for championship in saved_championships]
        )

        championships_response_names = set(
                [championship["championship_name"] for championship in championships_response]
        )

        new_championships_names = self.championship_difference_new(
                saved_championships_names, 
                championships_response_names)
        
        updated_id_championships = self.championship_difference_updated(
                saved_championships,
                saved_championships_names,
                championships_response,
                championships_response_names)

        deleted_championships_names = self.championship_difference_deleted(
                saved_championships_names, 
                championships_response_names)

        return {"new": new_championships_names,
                "updated": updated_id_championships,
                "deleted": deleted_championships_names}

    def insert(self, championship_dict: ChampionshipsDict):
        with engine.connect() as conn:
            stmt = insert(ChampionshipsTable).values(
                CId=championship_dict["CId"],
                championship_name=championship_dict["championship_name"],
                championship_name_ru=championship_dict["championship_name_ru"]
            )
            conn.execute(stmt)
            conn.commit()

    def save_new_championships(self, new_names_list, championships_response):
        for championship in championships_response:
            if championship["championship_name"] in new_names_list:
                self.insert(championship)

    def update_championships_ids(self, update_names_list, championships_response):
        championships_response = {
                championship["championship_name"]: championship["CId"]
                for championship in championships_response
        }

        for update_name in update_names_list:
            with engine.connect() as conn:
                stmt = (
                    update(ChampionshipsTable).
                    where(ChampionshipsTable.championship_name == update_name).
                    values(CId=championships_response[update_name])
                )
                conn.execute(stmt)
                conn.commit()

    def delete_championships(self, delete_names_list):
        for championship in delete_names_list:
            with engine.connect() as conn:
                stmt = (
                    delete(ChampionshipsTable).
                    where(ChampionshipsTable.championship_name==championship)
                )
                conn.execute(stmt)
                conn.commit()

    def update_championships(self, championships_response: list[ChampionshipsDict]):
        saved_championships = self.get_saved_championships()

        championships_difference = self.championships_difference(
                saved_championships,
                championships_response)

        print(championships_difference)
        
        self.save_new_championships(
                championships_difference["new"], 
                championships_response
        )
        self.update_championships_ids(
                championships_difference["updated"],
                championships_response
        )
        self.delete_championships(championships_difference["deleted"])

        # with engine.connect() as conn:
        #     stmt = insert(ChampionshipsTable).values(
        #         CId=
        #     )
        

        # with engine.connect() as conn:
        #     for championship in championships_response:
        #         stmt = insert(ChampionshipsTable).values(
        #             CId=championship["CId"],
        #             championship_name=championship["championship_name"],
        #             championship_name_ru=championship["championship_name_ru"]
        #         )
        #         conn.execute(stmt)
        #         conn.commit()


class TournamentsDB:
    def _is_tournament_in_db(self, tournament_name, TId, CId):
        with engine.connect() as conn:
            stmt = (select(TournamentsTable).
                    where(TournamentsTable.tournament_name == tournament_name)
                    )
            result = conn.execute(stmt).all()
            return True if len(result) != 0 else False

    def save_new_tournametns(self, tournaments_response: list[TournamentsDict]):
        for tournament in tournaments_response:
            with engine.connect() as conn:
                if not self._is_tournament_in_db(tournament["tournament_name"],
                                                 tournament["TId"],
                                                 tournament["CId"]):

                    stmt = insert(TournamentsTable).values(
                        CId=tournament["CId"],
                        TId=tournament["TId"],
                        championship_name=tournament["championship_name"],
                        championship_name_ru=tournament["championship_name_ru"],
                        tournament_name=tournament["tournament_name"],
                        tournament_name_ru=tournament["tournament_name_ru"]
                    )
                    conn.execute(stmt)
                    conn.commit()


class MatchesDB:
    def get_existing_match(self, match_id):
        with engine.connect() as conn:
            stmt = (select(MatchesTable).
                    where(MatchesTable.match_id==match_id).
                    where(MatchesTable.status==MatchStatus.PREMATCH.value)
                    )
            return conn.execute(stmt).all()

    def get_cid_by_tid(self, TId):
        with engine.connect() as conn:
            stmt = (select(TournamentsTable.CId).
                    where(TournamentsTable.TId == TId)
                    )
            return conn.execute(stmt).first()[0]

    def _is_match_in_db(self, match_id, ):
        return True if len(self.get_existing_match(match_id,)) != 0 else False

    def save_new_coefficient(self, match_id, coefs):
        with engine.connect() as conn:
            stmt = (update(MatchesTable).
                    where(MatchesTable.match_id == match_id).
                    values(coefficients = coefs)
                    )
            conn.execute(stmt)
            conn.commit()

    def update_existing_match(self, match):
        td15m = timedelta(minutes=15)

        td2d = timedelta(days=2)
        td1d = timedelta(days=1)
        td3h = timedelta(hours=3)
        td50m = timedelta(minutes=50)
        td5m = timedelta(minutes=5)

        mdt = match["match_datetime"]
    
        existing_match_coefs = self.get_existing_match(match["match_id"])[0][-1]
        parsing_coefs = {
                "total": match["coefficients"][0],
                "is_more": match["coefficients"][1],
                "coefficient": match["coefficients"][2]
        }
        if mdt - td2d > datetime.now():
            if "open" not in existing_match_coefs.keys():
                coef_key = "open"
                print("Меньше 2х дней")
            else:
                coef_key = -1
        elif (mdt - td2d - td15m) <= datetime.now() <= (mdt - td2d - td15m):
            coef_key = "2d"
            print("2 дня")
        elif (mdt - td1d - td15m) <= datetime.now() <= (mdt - td1d - td15m):
            coef_key = "1d"
            print("1 день")
        elif (mdt - td3h - td15m) <= datetime.now() <= (mdt - td3h - td15m):
            coef_key = "3h"
            print("3 часа")
        elif (mdt - td50m - td15m) <= datetime.now() <= (mdt - td50m - td15m):
            coef_key = "50m"
            print("50 минут")
        elif (mdt - td5m - td15m) <= datetime.now() <= (mdt - td5m - td15m):
            coef_key = "5m"
            print("5 минут")
        else:
            coef_key = -1
            print('не попало в интервалы')

        if coef_key != -1:
            existing_match_coefs[coef_key] = parsing_coefs
            self.save_new_coefficient(match["match_id"], existing_match_coefs)
    
    def save_n_update_matches(self, matches_response):
        for match in matches_response:
            with engine.connect() as conn:
                if not self._is_match_in_db(match["match_id"]):
                    CId = self.get_cid_by_tid(match["TId"])
                    print(CId)
                    stmt = insert(MatchesTable).values(
                        CId=CId,
                        TId=match["TId"],
                        match_id=match["match_id"],
                        match_datetime=match["match_datetime"],
                        parse_datetime=match["parse_datetime"],
                        status=match["status"],
                        first_club=match["first_club"],
                        first_club_ru=match["first_club_ru"],
                        second_club=match["second_club"],
                        second_club_ru=match["second_club_ru"],
                        coefficients={}
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
                else:
                    self.update_existing_match(match)


class GSDB:
    def get_saved_championships(self):
        return_dict = {}

        with engine.connect() as conn:
            stmt = select(ChampionshipsTable)
            championships_in_db = conn.execute(stmt).all()
            for championship in championships_in_db:
                return_dict[championship[1]] = championship[3]
        return return_dict

    def get_saved_tournaments(self):
        return_dict = {}

    def format_data(self, matches):
        championships = self.get_saved_championships()
        print(championships)

        for match in matches:
            id = match[0]
            CId = match[1]
            TId = match[2]
            match_id = match[3]
            match_datetime = match[4]
            parse_datetime = match[5]
            status = match[6]
            first_club = match[7]
            first_club_ru = match[8]
            second_club = match[9]
            second_club_ru = match[10]
            coefficients = match[11]





    def select_matches(self):
        with engine.connect() as conn:
            stmt = (select(MatchesTable).
                    join(ChampionshipsTable.championship_name_ru))
            print(stmt)

            # stmt = (select(MatchesTable.).
            #         where(MatchesTable.status == MatchStatus.PREMATCH.value))
            return conn.execute(stmt).all()

    def get_matches(self):
        matches = self.select_matches()

gsdb = GSDB()
pprint(gsdb.select_matches())
