import json
import time
from datetime import datetime, timedelta
from math import floor
from multiprocessing import Process, Lock
from pprint import pprint
import random

from db import ChampionshipsDB, LiveDB, MatchesDB, TournamentsDB
from google_sheets import GoogleSheets
from logger import general_log
from reqs import InnerAPI, UnParse
import schedule


class Actions:
    def __init__(self):
        self.inner_api = InnerAPI()
        self.unparse = UnParse()
        self.cdb = ChampionshipsDB()
        self.tdb = TournamentsDB()
        self.mdb = MatchesDB()
        self.ldb = LiveDB()

    def get_championship_ids(self):
        return self.cdb.get_championship_ids_from_db()

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

    def get_n_update_one_match(self, match_id):
        match = self.inner_api.get_one_match_info(match_id)
        stakes = self.unparse.one_match(match)
        return stakes

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

        # m = Manager()
        # self.queue = m.PriorityQueue()
        self.lock = Lock()

        self.matches_proc = Process(target=self.matches_schedule)
        self.live_proc = Process(target=self.live_schedule)

        self.last_live_update = datetime.now() - timedelta(seconds=10)
        self.gs.update_active()
        self.gs.update_passed()

    def live(self):
        # while True:
        #     if floor(time.time() % 10) == 0:
        general_log.info("parsing live executed")
        t = time.time()
        with self.lock:
            self.last_live_update = datetime.now()
            general_log.debug("start parsing live")
            self.acts.get_n_update_live()
            # self.queue.put((1, self.acts.get_n_update_live, []))
            time.sleep(random.uniform(0.5, 1))
            general_log.info(f"live parsed | Time: {round(time.time() - t, 2)}")

    def matches(self):
        general_log.info("Start parsing matches")

        with self.lock:
            self.acts.get_n_update_championships()
            time.sleep(random.uniform(0.5, 1))

        t = time.time()

        c_ids = self.acts.get_championship_ids()
        exclude_t_ids = [42317, 42320, 42337, 42322, 46314, 42331, 42324, 42335, 42334, 42327, 42330, 47817, 42318, 46313, 46310]

        t_ids = []
        for c_id in c_ids:
            with self.lock:
                t_list = self.acts.get_n_update_tournaments(c_id)
                for tournament in t_list:
                    t_ids.append([tournament["id"], tournament["matches_count"]])
                time.sleep(random.uniform(0.5, 1))

        for t_id, matches_count in t_ids:
            if t_id not in exclude_t_ids:
                if matches_count != 0:
                    tm = time.time()
                    with self.lock:
                        matches_list = self.acts.get_n_update_matches(t_id)
                        general_log.debug(f"Parse tournament {t_id} | Parsed {len(matches_list)} | Time: {round(time.time() - tm, 2)}c")
                        time.sleep(random.uniform(0.5, 1))

        self.gs.update_active()
        self.gs.update_passed()
        general_log.info(f"Parsed {len(t_ids)} tournaments | Time: {round(time.time() - t, 2)}c")

    def live_schedule(self):
        while True:
            if floor(time.time()) % 10 == 0:
                self.live()
            time.sleep(0.5)

    def matches_schedule(self):
        while True:
            if floor(time.time()) % 300 == 0:
                self.matches()
            time.sleep(0.5)

if __name__ == "__main__":
    actions = Actions()
    # actions.get_n_update_championships()
    # actions.get_n_update_tournaments(1295)
    # actions.get_n_update_matches(4535)
    # pprint(actions.get_n_update_one_match(20652645))
    # actions.get_n_update_live()

    cycle = Cycle()
    # cycle.matches()
    # cycle.live_proc.start()
    # cycle.matches_proc.start()
