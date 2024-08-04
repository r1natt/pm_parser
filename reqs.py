import json
from typing import Dict, List
import requests
from datetime import datetime, timedelta
from db import DB
import traceback
from logger import reqs_log
from pprint import pprint
from random import random
import time

from tables import (
    ChampionshipsDict,
    TournamentsDict,
    MatchStatus,
    MatchDict,
    LiveMatchDict
)

db = DB()


class UnParse:
    def championships_response(self, response: dict):
        return_list = []
        
        for championship in response:
            return_list.append(
                ChampionshipsDict(
                    id=championship["Id"],
                    name=championship["EGN"],
                    name_ru=championship["N"]
                )
            )
        return return_list

    def tournaments(self, response: dict):
        return_list = []

        for tournament in response:
            return_list.append(
                TournamentsDict(
                    id=tournament["Id"],
                    c_id=tournament["CtID"],
                    name=tournament["EGN"],
                    name_ru=tournament["N"],

                    matches_count=tournament["EC"]
                )
            )
        return return_list

    def get_formatted_match_stakes(self, match_stakes):
        stakes = []
        for stake in match_stakes:
            stake_list = [
                stake["A"],  # тотал 
                True if stake["N"] == "Больше" else False,  # больше или меньше
                stake["F"]  # коэф
            ]
            stakes.append(stake_list)
        return stakes

    def matches_response(self, response: dict):
        return_list = []

        for match in response["CNT"][0]["CL"][0]["E"]:

            try:
                third_stake_type = list(
                        filter(lambda x: x["Id"] == 3, match["StakeTypes"])
                )[0]["Stakes"]
            except IndexError:
                # Эта ошибка значит, что коэффициентов ставок нет и это скорее 
                # всего запись об итогах "Бразилия. Серия B. Итоги"
                break

            match_stakes = []

            total = third_stake_type[0]["A"]  # тотал 
            is_more = True if third_stake_type[0]["N"] == "Больше" else False  # больше или меньше
            coefficient = third_stake_type[0]["F"]  # коэф
            coefficients = [total, is_more, coefficient]
            coefficients = self.get_formatted_match_stakes(third_stake_type)

            return_list.append(
                MatchDict(
                    id = match["Id"],  # айди матча (скорее всего)
                    t_id=match["CId"],
                    match_datetime = datetime.strptime(
                                match["D"], "%Y-%m-%dT%H:%M:%SZ"
                        ) + timedelta(hours=3),  # Дата и время матча
                    parse_datetime = datetime.now(),
                    status=MatchStatus.PREMATCH.value,
                    first_club=match["EHT"],  # первая команда
                    first_club_ru=match["HT"],   # первая команда
                    second_club=match["EAT"],   # вторая команда
                    second_club_ru=match["AT"],  # вторая команда
                    # coefficients=[total, is_more, coefficient]
                    coefficients=coefficients
                )
            )
        return return_list

    def get_formatted_match_stakes(self, match_stakes):
        stakes = []
        for stake in match_stakes:
            stake_list = [
                stake["A"],  # тотал 
                True if "Больше" in stake["N"] else False,  # больше или меньше
                stake["F"]  # коэф
            ]
            stakes.append(stake_list)
        return stakes

    def live(self, live_response):
        return_list = []

        for match in live_response:

            try:
                third_stake_type = list(
                        filter(lambda x: x["Id"] == 3, match["StakeTypes"])
                )[0]["Stakes"]
                coefficients = self.get_formatted_match_stakes(third_stake_type)
            except IndexError:
                # Эта ошибка значит, что коэффициентов ставок нет и скорее 
                # всего ставки закрыты
                coefficients = []

            return_list.append(
                LiveMatchDict(
                    id=match["Id"],
                    status=match["ShortStatus"],
                    coefficients=coefficients,
                    match_datetime = datetime.strptime(
                                match["D"], "%Y-%m-%dT%H:%M:%SZ"
                        ) + timedelta(hours=3),
                    first_club=match["EHT"],  # первая команда
                    first_club_ru=match["HT"],   # первая команда
                    second_club=match["EAT"],   # вторая команда
                    second_club_ru=match["AT"],  # вторая команда
                )
            )

        return return_list


class InnerAPI:
    """
    Этот класс отправляет запросы по внутренному апи, который я нашел вручную
    через просмотр сети

    Порядок запросов на странице:
        1) Получение id стран букмекеров
        2) Получение лиг по id страны
        3) получение матчей по id лиги
    """

    headers = {'accept': '*/*',
               'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
               'cache-control': 'no-cache',
               'cookie': '_ga=GA1.1.292150090.1721743104; CookieScriptConsent={"action":"reject","categories":"[]"}; _cfuvid=z8z5UzOQtnM1Jb6dS3eUIYSGo5Rx3QxTNp8aKsyNrOQ-1721853010995-0.0.1.1-604800000; FECW=c9d2f88326ceca994903af0ad06689d8794620c5093c0a89f91dc2a8f39d27d3873b58011dade7618ca59b07f27618c255abd1923cb3022d2eca678e1b083004506d780764d74d07b98cde9431f1a95fb2; __cf_bm=2mVfsVsJi_hAZ56US.LsmvSzMyrv.iycNaAGfV_Dw0A-1721986051-1.0.1.1-IpU_ApI9CzOWeVodNRYBpFM3_L7v__2.E7oN6wbHJ69dXRKUP04lkmSzSwamUcdQR1y0BJpGQUTvJJ6vYDjqCg; _ga_5L5H5QQKCV=GS1.1.1721984558.2.1.1721986053.0.0.0; _ga_Z56G05E57D=GS1.1.1721984572.9.1.1721986059.0.0.0; FECA=aso5rJy5K9g9kor27Au70dGe/rPyGd6ld8Gzo9xnwN+DvQ/XCZP5QqWg9lwt+9BXCJeMfbqvy+MO1JBizm2/0ZR10ESWs50GbYXmhPP3LBDS8znWV2mhu8ZCIC5vjOi2bIXtcZoT+uEyUPhZq11zzuTAlFO6wJFVTNpgwMEH0eNr8SArpnBIrNMb7sy+Kv0l93',
               'pragma': 'no-cache',
               'priority': 'u=1, i',
               'referer': 'https://sport.pm.by/',
               'sec-ch-ua': 'Not/A)Brand;v=8,Chromium;v=126',
               'sec-ch-ua-mobile': '?0',
               'sec-ch-ua-platform': 'Linux',
               'sec-fetch-dest': 'empty',
               'sec-fetch-mode': 'cors',
               'sec-fetch-site': 'same-origin',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }
    unparse = UnParse()

    def get_championsips(self) -> Dict:
        params = {
                'period': 0,
                'isTournament': False,
                'sportId': 1,
                'langId': 1,
                'partnerId': 3000091,
        }

        for _ in range(3):
            try:
                r = requests.get("https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/prematch/championships", 
                                 params=params, 
                                 headers=self.headers, 
                                 timeout=5)
                reqs_log.debug(f'get_championsips ({r.status_code})')
                return json.loads(r.text)
            except Exception as e:
                reqs_log.error(traceback.format_exc())
            time.sleep(random() * 1 + 1)
                
    
    def get_tournaments(self, c_id: int):
        params = {
                'period': 0,
                'championshipId': c_id,
                'isTournament': False,
                'langId': 1,
                'partnerId': 3000091,
        }

        for _ in range(3):
            try:
                r = requests.get('https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/prematch/tournaments',
                                 params=params,
                                 headers=self.headers,
                                 timeout=5)
                reqs_log.debug(f'get_tournaments c_id: {c_id} ({r.status_code})')
                return json.loads(r.text)
            except Exception as e:
                reqs_log.error(traceback.format_exc())
            time.sleep(random() * 1 + 1)

    def get_mathces(self, t_id: int):
        params = {
                'period': 0,
                'tournamentId': t_id,
                'isTournament': False,
                'stakeTypes': ['1', '702', '2', '3', '37'],
                'langId': 1,
                'partnerId': 3000091,
        }

        for _ in range(3):
            try:
                r = requests.get("https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/prematch/matches", 
                                 params=params, 
                                 headers=self.headers,
                                 timeout=5)
                reqs_log.debug(f'get_mathces t_id: {t_id} ({r.status_code})')
                return json.loads(r.text)
            except json.JSONDecodeError:
                reqs_log.error(traceback.format_exc())
            except Exception:
                reqs_log.error(traceback.format_exc())
                
            time.sleep(random() * 1 + 1)

    def get_live_matches(self):
        params = {
            'sportId': 1,
            'stTypes': [1, 702, 2, 3, 37, 1],
            'langId': 1,
            'partnerId': 3000091,
            'FECU': 'aso5rJy5K9g9kor27Au70dGe%2FrPyGd6ld8Gzo9xnwN%2BDvQ%2FXCZP5QqWg9lwt%2B9BXCJeMfbqvy%2BMO1JBizm2%2F0ZScYXM5EmWSt94AODeLkd42wtlz794mN03u4Sgyb8rbeqEHls1YmYofK71ogVbT9GD%2FMK42XI9o6D9eN4%2Bn7%2BdzOlID7XZGPvj%2BuUkeAhyQL3'
        }
        headers = {'accept': '*/*',
                   'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                   'cache-control': 'no-cache',
                   'cookie': 'CookieScriptConsent={"action":"reject","categories":"[]"}; FECW=c9d2f88326ceca994903af0ad06689d8794620c5093c0a89f91dc2a8f39d27d3873b58011dade7618ca59b07f27618c255abd1923cb3022d2eca678e1b083004506d780764d74d07b98cde9431f1a95fb2; _cfuvid=0IZwbDpipJ8LeHg8mKLPsuo57dBuiT2EC9WKaFhBwgM-1722160190128-0.0.1.1-604800000; _ga=GA1.1.760437363.1722244406; _ga_LYB6EQTLPV=GS1.1.1722342731.1.0.1722342739.0.0.0; __cf_bm=vc15_IOD_lK0exeS4nSBXcvmTuEh8Z_nWxE3KQESojM-1722348047-1.0.1.1-egXsRzOS66TIFet5nDbA_0IZs6alQREiYc0bgYwdnpV86GDJG2SEdzow_vTrqmNCWg4IELSAva7dg7sksty26w; _ga_5L5H5QQKCV=GS1.1.1722348048.5.1.1722348094.0.0.0; _ga_Z56G05E57D=GS1.1.1722348055.18.1.1722348100.0.0.0; FECA=aso5rJy5K9g9kor27Au70dGe/rPyGd6ld8Gzo9xnwN+DvQ/XCZP5QqWg9lwt+9BXCJeMfbqvy+MO1JBizm2/0ZScYXM5EmWSt94AODeLkd42wtlz794mN03u4Sgyb8rbeqEHls1YmYofK71ogVbT9GHqyinjWaEJdBml4VRoZmwlmt+KFurDOejAqdqqlbukC3',
                   'pragma': 'no-cache',
                   'priority': 'u=1, i',
                   'referer': 'https://sport.pm.by/',
                   'sec-ch-ua': 'Not/A)Brand;v=9,Chromium;v=127',
                   'sec-ch-ua-mobile': '?0',
                   'sec-ch-ua-platform': 'Linux',
                   'sec-fetch-dest': 'empty',
                   'sec-fetch-mode': 'cors',
                   'sec-fetch-site': 'same-origin',
                   'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

        for _ in range(3):
            try:
                r = requests.get("https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/live/geteventslist", 
                                 params=params, 
                                 headers=headers,
                                 timeout=5)
                reqs_log.debug(f'get_live_matches ({r.status_code})')
                return json.loads(r.text)
            except Exception:
                reqs_log.error(traceback.format_exc())
            time.sleep(random() * 1 + 1)


# pprint(InnerAPI().get_live_matches())
