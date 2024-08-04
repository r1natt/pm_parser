import json
import time
from datetime import datetime, timedelta
from math import floor
from multiprocessing import Process
from pprint import pprint
from random import random

from db import ChampionshipsDB, LiveDB, MatchesDB, TournamentsDB
from google_sheets import GoogleSheets
from logger import general_log
from reqs import InnerAPI, UnParse


class Actions:
    def __init__(self):
        self.inner_api = InnerAPI()
        self.unparse = UnParse()
        self.cdb = ChampionshipsDB()
        self.tdb = TournamentsDB()
        self.mdb = MatchesDB()
        self.ldb = LiveDB()

    def get_n_update_championships(self):
        # championships = [
        #     {'CL': None,'CLI': '','EC': 2,'EGN': 'FIFA.Volta','Fid': 562890,'Id': 77777777,'N': 'FIFA.Volta','SID': 0},
        #     {'CL': None,'CLI': '','EC': 84,'EGN': 'Europe','Fid': 113,'Id': 88888888,'N': 'Европа','SID': 0},
        #     {'CL': None,'CLI': '','EC': 84,'EGN': 'Brazil','Fid': 113,'Id': 11111111,'N': 'Европа','SID': 0},
        # ]
        #
        # championships = [
        #     {'CL': None,'CLI': '','EC': 2,'EGN': 'FIFA.Volta','Fid': 562890,'Id': 77777777,'N': 'FIFA.Volta','SID': 0},
        #     {'CL': None,'CLI': '','EC': 84,'EGN': 'Europe','Fid': 113,'Id': 33333333,'N': 'Европа','SID': 0},
        #     {'CL': None,'CLI': '','EC': 23,'EGN': 'Spain','Fid': 124,'Id': 99999999,'N': 'Испания','SID': 0}
        # ]
        
        championships = self.inner_api.get_championsips()
        championships_list = self.unparse.championships_response(championships)
        self.cdb.update_championships(championships_list)

    def get_n_update_tournaments(self, c_id: int):
        tournaments = self.inner_api.get_tournaments(c_id)
        tournaments_list = self.unparse.tournaments(tournaments)
        self.tdb.save_new_tournametns(tournaments_list)
        return tournaments_list

    def get_n_update_matches(self, t_id: int):
        matches = self.inner_api.get_mathces(t_id)
        matches_list = self.unparse.matches_response(matches)
        self.mdb.save_n_update_matches(matches_list)
        return matches_list

    def get_n_update_live(self):
        live_matches = self.inner_api.get_live_matches()
        live_list = self.unparse.live(live_matches)
        
        self.ldb.handle_live_matches(live_list)

        # for match in live_list:
        #     if match["status"] == "Перерыв":
        #         pprint(match)
        # update_status
        # check_on_break



class Cycle:
    def __init__(self):
        self.acts = Actions()
        self.gs = GoogleSheets()

        self.manager = Process(target=self.manager)

        self.last_live_update = datetime.now() - timedelta(seconds=10)
        self.gs.update_matches()

    def live(self):
        if not(datetime.now() - timedelta(seconds=1) <= self.last_live_update <= datetime.now() + timedelta(seconds=1)):
            self.last_live_update = datetime.now()
            general_log.info("start parsing live")
            
            self.acts.get_n_update_live()
            time.sleep(random() * 1 + 1)

    def matches(self):
        general_log.info("Start parsing matches")

        self.acts.get_n_update_championships()
        time.sleep(random() * 1 + 1)

        t = time.time()

        c_ids = [1222, 1224, 1292, 2688, 1441, 2276]
        exclude_t_ids = [42317, 42320, 42337, 42322, 46314, 42331, 42324, 42335, 42334, 42327, 42330, 47817, 42318, 46313]

        t_ids = []
        for c_id in c_ids:
            t_list = self.acts.get_n_update_tournaments(c_id)
            for tournament in t_list:
                t_ids.append([tournament["id"], tournament["matches_count"]])
            time.sleep(random() * 1 + 1)
        # Сделать так, чтобы мы не запрашивали нулевые турнаменты

        print(t_ids)
        for t_id, matches_count in t_ids:
            if t_id not in exclude_t_ids:
                if matches_count != 0:
                    tm = time.time()
                    matches_list = self.acts.get_n_update_matches(t_id)
                    general_log.debug(f"Parse match {t_id} | Parsed {len(matches_list)} | Time: {round(time.time() - tm, 2)}c")
                    time.sleep(random() * 1 + 1)

        self.gs.update_matches()
        general_log.info(f"Parsed {len(t_ids)} tournaments | Time: {round(time.time() - t, 2)}c")

    def manager(self):
        while True:
            if 0 <= round(time.time() % 300) <= 2:
                if floor(time.time() % 10) == 0:
                    self.live()
                self.matches()
            elif floor(time.time() % 10) == 0:
                self.live()
            time.sleep(0.5)


if __name__ == "__main__":
    # actions = Actions()
    # actions.get_n_update_championships()
    # actions.get_n_update_tournaments(1295)
    # actions.get_n_update_matches(4535)
    # actions.get_n_update_live()

    cycle = Cycle()
    cycle.manager.start()
