import datetime
import dateutil.parser
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import logging

discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                'version=v4')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'


class ModulesToGoogle:

    def __init__(self, config):
        self.config = config

        # This is the timezone for this script. It actually doesn't matter what value is used here as calls
        # to datetime.datetime.now(self.tz) will convert to whatever timezone you specify and comparions just need
        # a TZ in both sides of the operator
        self.tz = dateutil.tz.gettz("Australia/Melbourne")

        self.logger = logging.getLogger("modules-to-google.ModulesToGoogle")
        self.logger.debug("creating an instance of ModulesToGoogle")

    def get_authenticated_service_account(self):
        credentials = service_account.Credentials.from_service_account_file(self.config['service-account-secrets-file'],
                                                                            scopes=SCOPES)
        return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    def main(self):
        self.logger.info("Creating authenticated service")
        service = self.get_authenticated_service_account()
        google_sheet = service.spreadsheets()

        # Interrogate the spreadsheet to obtain the sheetID for the worksheet.
        result = google_sheet.get(spreadsheetId=self.config['spreadsheet_id']).execute()
        self.logger.info("Obtained the sheet")
        sheets = result['sheets']

        sheet_id = ""

        for sheet in sheets:
            # print(sheet['properties']['title'])
            # print(sheet['properties']['sheetId'])
            if sheet['properties']['title'] == self.config['worksheet']:
                sheet_id = sheet['properties']['sheetId']

        self.logger.info("ID of worksheet '{}' to be updated is: {}".format(self.config['worksheet'], sheet_id))

        # Read the modules files to obtain the data for uploading to the worksheet
        with open(self.config['modules_file']) as f:
            modules_from_file = f.read()

        # Create the body for updating the worksheet
        # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request
        body = {
                "requests": [{"updateCells": {"range": {"sheetId": sheet_id}, "fields": "*"}},
                             {"pasteData": {"coordinate": {"columnIndex": 0, "rowIndex": 0, "sheetId": sheet_id},
                                            "data": modules_from_file,
                                            "type": "PASTE_VALUES",
                                            "delimiter": ","}}],
                "includeSpreadsheetInResponse": True}
        body_json = json.dumps(body, indent=4)
        self.logger.debug("Type: {}".format(type(body_json)))
        self.logger.debug("Body: {}".format(body_json))

        service = self.get_authenticated_service_account()
        google_sheet = service.spreadsheets()

        self.logger.info("Updating Sheet: {}, worksheet {}".format(self.config['spreadsheet_id'], sheet_id))
        result = google_sheet.batchUpdate(spreadsheetId=self.config['spreadsheet_id'],
                                          body=json.loads(body_json)).execute()
        self.logger.info("Result: {}".format(result))
