import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from logger import general_log
from dotenv import load_dotenv
from pprint import pprint
from datetime import datetime
from db import GSDB

load_dotenv() 

SAMPLE_SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = None
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
with open("token.json", "w") as token:
    token.write(creds.to_json())


class GoogleSheets:
    gsdb = GSDB()

    def clear_range(self, range):
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet
            .values()
            .clear(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=range
            )
            .execute()
        )
        general_log.debug(f"{result.get('updatedCells')} cells updated {range}")
        return result
   
    def write_last_update(self, range):
        body = {"values": [[datetime.now().strftime("%d/%m %H:%M:%S")]]}
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet
            .values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=range,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        general_log.debug(f"{result.get('updatedCells')} cells updated {range}")
        return result

    def write(self, range, values):
        body = {"values": values}
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        result = (
            sheet
            .values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=range,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        general_log.debug(f"{result.get('updatedCells')} cells updated {range}")
        return result

    def calculate_main_coefficient(self, coefs_list):
        """
        Я храню все коэффициенты в каждый из нужных моментов времени в виде 
        списка:
            [
                [1, True, 1.24],
                [1, False, 1.56],
                [1.5, True, 3.54],
                [1.5, False, 4.67],
                ...
            ]
        Чтобы вывести нужный коэффициент (как на букмере) мне нужно посчитать
        При каком тотале минимальная разница в коэффициентах по модулю
        Это считает данная функция
        """

        totals_coefs = {}
        for coef in coefs_list:
            if coef[0] not in totals_coefs:
                totals_coefs[coef[0]] = coef[2]
            else:
                totals_coefs[coef[0]] = round(
                        abs(
                            coef[2] - totals_coefs[coef[0]]
                            ), 
                        2)
        try:
            min_total = min(totals_coefs, key=totals_coefs.get) 
            for coef in coefs_list:
                if coef[0] == min_total and coef[1] is True:
                    return coef
        except ValueError:
            return [-1, False, -1]
        return [-1, False, -1]

    def format_data(self, matches):
        return_list = []
        for match in matches:
            match_id = match[0]
            t_id = match[1]
            c_id = match[2]
            championship_name = match[3]
            tournament_name = match[4]
            first_club_ru = match[5]
            second_club_ru = match[6]
            match_datetime = match[7]
            coefs = match[8]
            status = match[9]
            
            match_name = first_club_ru + " - " + second_club_ru
            match_datetime = match_datetime.strftime("%d/%m %H:%M")

            format_coefs = []
            for coef_name in ["open", "2d", "1d", "3h", "50m", "5m"]:
                try:
                    coefficient_list = self.calculate_main_coefficient(coefs["prematch"][coef_name]["coefficients"])
                    total = coefficient_list[0]
                    is_more = coefficient_list[1]
                    coefficient = coefficient_list[2]

                    coef = str(total) + ("б" if is_more else "м") + " " + str(coefficient)
                    format_coefs.append(coef)
                except KeyError:
                    coef = "-"
                    format_coefs.append(coef)
            for coef_name in ["open", "5m", "10m", "15m"]:
                try:
                    coefficient_list = self.calculate_main_coefficient(coefs["live"][coef_name]["coefficients"])
                    total = coefficient_list[0]
                    is_more = coefficient_list[1]
                    coefficient = coefficient_list[2]

                    coef = str(total) + ("б" if is_more else "м") + " " + str(coefficient)
                    format_coefs.append(coef)
                except KeyError:
                    coef = "-"
                    format_coefs.append(coef)
        
            match_row = [
                match_id, 
                t_id, 
                c_id, 
                championship_name,
                tournament_name,
                match_name,
                status,
                match_datetime,
            ]
            match_row.extend(format_coefs)
            return_list.append(match_row)
        return return_list


    def update_active(self):
        """
        Иногда я обновляю гугл таблицу при запуске скрипта, и вместе с 
        обновлением таблицы я обновлял и время ее обновления, хотя это не 
        логично, ведь время обновления показывает за сколько отработал парсер
        """
        data_range = "Active!A3:R"
        last_update_range = "Active!E1:E1"

        matches = self.gsdb.get_matches()
        format_data = self.format_data(matches)
        self.clear_range(data_range)
        self.write_last_update(last_update_range)
        self.write(data_range, format_data)

    def update_passed(self):
        data_range = "Passed!A3:R"
        last_update_range = "Passed!E1:E1"

        matches = self.gsdb.get_passed()
        format_data = self.format_data(matches)
        self.clear_range(data_range)
        self.write_last_update(last_update_range)
        self.write(data_range, format_data)


# if __name__ == "__main__":
#     gs = GoogleSheets()
#     gs.update_matches()
#     # gs.write_last_update()
