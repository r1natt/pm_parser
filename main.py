from reqs import UnParse, InnerAPI
from db import DB, ChampionshipsDB
from reqs import InnerAPI, UnParse


class Actions:
    def __init__(self):
        self.inner_api = InnerAPI()
        self.unparse = UnParse()
        self.cdb = ChampionshipsDB()

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


if __name__ == "__main__":
    actions = Actions()
    # actions.get_n_update_championships()
    # db = DB()
    # page = InnerAPI.get_page(5567)
    # parse_list = UnParse().unparse(page)
    # db.save_few_matches(parse_list)
