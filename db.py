from datetime import datetime
from enum import Enum

from requests import Session
from sqlalchemy import insert, select, update, delete

from engine import engine
from tables import (
    Base, 
    ChampionshipsTable,
    TournamentsTable,
    MatchesTable,

    ChampionshipsDict,
    TournamentsDict,
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



