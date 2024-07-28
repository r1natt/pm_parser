import json
from typing import Dict, List
import requests
from datetime import datetime, timedelta
from db import DB

from logger import reqs_log
from pprint import pprint

from tables import (
    ChampionshipsDict,
    TournamentsDict,
    MatchDict,
)

db = DB()


class UnParse:
    def championships_response(self, response: dict):
        return_list = []
        
        for championship in response:
            return_list.append(
                ChampionshipsDict(
                    CId=championship["Id"],
                    championship_name=championship["EGN"],
                    championship_name_ru=championship["N"]
                )
            )
        return return_list

    def unparse(self, matches_dict: dict):
        return_list = []

        for match in matches_dict["CNT"][0]["CL"][0]["E"]:
            league_id = match["CId"]  # id лиги
            match_id = match["Id"]  # айди матча (скорее всего)
            first_club = match["EHT"]  # первая команда
            first_club_ru = match["HT"]  # первая команда
            second_club = match["EAT"]  # вторая команда
            second_club_ru = match["AT"]  # вторая команда
            match_datetime = datetime.strptime(
                    match["D"], "%Y-%m-%dT%H:%M:%SZ"
            ) + timedelta(hours=3) # Дата и время матча
            try:
                stake_types = list(
                        filter(lambda x: x["Id"] == 3, match["StakeTypes"])
                )[0]["Stakes"]
                """
                for strake_type in match["StakeTypes"]:
                    if strake_type["Id"] == 3:
                        stakes = strake_type["Stakes"]

                Строка с фильтрацией словаря является альтернативой строки с for
                """
            except IndexError:
                logger.debug(f"IndexError {first_club} {second_club}")
                """
                Ошибка выдается в моменте, когда словарь отфильтровался по 
                id == 3 (данные о коэффиуиенте на тотал), но ставок на тотал нет
                Это данные об итогах, их не считываем
                """
                break

            total = stake_types[0]["A"]  # тотал 
            is_more = True if stake_types[0]["N"] == "Больше" else False  # больше или меньше
            coefficient = stake_types[0]["F"]  # коэф

            match_bets_dict = MatchBetsDict(
                league_id=league_id,
                match_id=match_id,
                match_datetime=match_datetime,
                parse_datetime=datetime.now(),
                status=MatchStatus.PREMATCH,
                first_club=first_club,
                first_club_ru=first_club_ru,
                second_club=second_club,
                second_club_ru=second_club_ru,
                total_coef=total,
                is_more=is_more,
                coefficient=coefficient
            )

            return_list.append(match_bets_dict)

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

        r = requests.get("https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/prematch/championships", 
                         params=params, 
                         headers=self.headers)
        return json.loads(r.text)
    
    def get_tournaments(self, CId: int):
        params = {
                'period': 0,
                'championshipId': CId,
                'isTournament': False,
                'langId': 1,
                'partnerId': 3000091,
        }
        r = requests.get('https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/prematch/tournaments',
                         params=params,
                         headers=self.headers)
        return json.loads(r.text)

    def get_mathces(self, tournament_id: int):
        params = {
                'period': 0,
                'tournamentId': tournament_id,
                'isTournament': False,
                'stakeTypes': ['1', '702', '2', '3', '37'],
                'langId': 1,
                'partnerId': 3000091,
        }

        r = requests.get("https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/prematch/matches", 
                         params=params, 
                         headers=self.headers)
        return json.loads(r.text)

