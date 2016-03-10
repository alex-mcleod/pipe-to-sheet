import gspread

from oauth2client.client import SignedJwtAssertionCredentials

from apiclient.discovery import build

from httplib2 import Http

from datetime import datetime

import sys

import csv

import StringIO

import json


DEFAULT_TITLE = "Data"

SCOPE = ['https://www.googleapis.com/auth/drive', 'https://spreadsheets.google.com/feeds']

URL = 'https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0'

DRIVE_CREDENTIALS = json.loads(open('~/.gs/credentials.json'))


def get_credentials():
    return SignedJwtAssertionCredentials(DRIVE_CREDENTIALS['client_email'], DRIVE_CREDENTIALS['private_key'].encode(), SCOPE)


def open_google_spreadsheet(sheet_id):
    credentials = get_credentials()
    gc = gspread.authorize(credentials)
    sht = gc.open_by_key(sheet_id)
    return sht


def create_google_spreadsheet(title, parent_folder_ids=[], share_domains=[]):

    """ Adapted from https://gist.github.com/miohtama/f988a5a83a301dd27469 """

    credentials = get_credentials()

    http_auth = credentials.authorize(Http())

    drive_api = build('drive', 'v3', http=http_auth)

    body = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
    }

    if parent_folder_ids:
        body["parents"] = [
            {
                'kind': 'drive#fileLink',
                'id': parent_folder_ids
            }
        ]

    req = drive_api.files().create(body=body)
    new_sheet = req.execute()

    # Get id of fresh sheet
    spread_id = new_sheet["id"]

    # Grant permissions
    if share_domains:
        for domain in share_domains:

            # https://developers.google.com/drive/v3/web/manage-sharing#roles
            # https://developers.google.com/drive/v3/reference/permissions#resource-representations
            domain_permission = {
                'type': 'domain',
                'role': 'writer',
                'domain': domain,
                # Magic almost undocumented variable which makes files appear in your Google Drive
                'allowFileDiscovery': True,
            }

            req = drive_api.permissions().create(
                fileId=spread_id,
                body=domain_permission,
                fields="id"
            )

            req.execute()

    spread = open_google_spreadsheet(spread_id)

    return spread


def main():

    print "Reading in data"

    data = sys.stdin.read()

    try:
        reader = csv.reader(StringIO.StringIO(data), csv.excel)
    except IOError:
        raise Exception('Unable to read input as CSV')

    title = DEFAULT_TITLE

    print "Creating sheet named \"%s\"" % title

    sht = create_google_spreadsheet(title)
    ws = sht.get_worksheet(0)

    print "Writing data to sheet"

    as_list = list(reader)
    # Set to length of longest row. Ensures CSVs with variable
    # length rows are supported.
    col_count = max([len(row) for row in as_list])
    col_start = 'A'
    col_end = chr((col_count - 1) + ord(col_start))
    row_start = '1'
    row_end = str(len(as_list))

    range_build = col_start + row_start + ':' + col_end + row_end

    cell_list = ws.range(range_build)
    cur_cell = 0
    next_row_start = col_count

    for row in as_list:
        for data in row:
            cell_list[cur_cell].value = data
            cur_cell += 1
        # Jump cur_cell to start of next row.
        # Need to do this to support CSVs which have
        # variable length rows.
        cur_cell = next_row_start
        next_row_start += col_count

    ws.update_cells(cell_list)

    print 'Sheet is available at', URL.format(sheet_id=sht.id)


if __name__ == '__main__':
    sys.exit(main())
