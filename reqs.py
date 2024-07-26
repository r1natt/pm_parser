import requests
import json


def get_page():
    headers = {'accept': '*/*',
               'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
               'cache-control': 'no-cache',
               'cookie': '_cfuvid=Dw7CX.Bp.b20IOuQSauPYDOIkw_qzncgE74iZ2xdXGc-1721743103350-0.0.1.1-604800000; _ga=GA1.1.292150090.1721743104; CookieScriptConsent={"action":"reject","categories":"[]"}; __cf_bm=.8QVNz7a5nMKGtfqLyXneEom8itqj4go1B9.aS9ePrg-1721851656-1.0.1.1-dxY1ilPmvr004hk.kdI3hrKbSz90UbzokJQCo9vIHCJvz9ARCIP.MVIuiSpaIKJKFu0W2TiOJ34D.k00iVY9fA; _ga_5L5H5QQKCV=GS1.1.1721851658.1.1.1721852340.0.0.0; _ga_Z56G05E57D=GS1.1.1721851662.4.1.1721852347.0.0.0',
               'pragma': 'no-cache',
               'priority': 'u=1, i',
               'referer': 'https://sport.pm.by/',
               'sec-ch-ua': 'Not/A)Brand;v=8,Chromium;v=126',
               'sec-ch-ua-mobile': '?0',
               'sec-ch-ua-platform': 'Linux',
               'sec-fetch-dest': 'empty',
               'sec-fetch-mode': 'cors',
               'sec-fetch-site': 'same-origin',
               'sec-fetch-user': '?1',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    params = {
            'period': 0,
            'tournamentId': 29364,
            'isTournament': False,
            'stakeTypes[]': [1, 702, 2, 3, 37],
            'langId': 1,
            'partnerId': 3000091
    }

    r = requests.get("https://sport.pm.by/980bb12b-3630-4bb5-b920-68a557da9e06/prematch/matches",
                     params=params,
                     headers=headers)
    print(r.text)
