"""
One-time script to initialize Google Sheets with headers and sample data.

Usage:
    python scripts/seed_sheets.py

Requires:
    - GOOGLE_SERVICE_ACCOUNT_JSON env var
    - GOOGLE_SHEET_ID env var
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

MEMBERS_HEADERS = [
    "id", "nama_panggilan", "nama_lengkap", "jabatan",
    "sekbid", "instagram", "deskripsi",
]

EVENTS_HEADERS = [
    "id", "nama_event", "tanggal", "lokasi", "instagram", "deskripsi",
]


def main():
    creds_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    sheet_id = os.environ["GOOGLE_SHEET_ID"]

    creds = Credentials.from_service_account_info(
        json.loads(creds_json), scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)

    try:
        members_ws = sheet.worksheet("Members")
    except gspread.WorksheetNotFound:
        members_ws = sheet.add_worksheet("Members", rows=100, cols=20)
    members_ws.clear()
    members_ws.append_row(MEMBERS_HEADERS)

    try:
        events_ws = sheet.worksheet("Events")
    except gspread.WorksheetNotFound:
        events_ws = sheet.add_worksheet("Events", rows=100, cols=20)
    events_ws.clear()
    events_ws.append_row(EVENTS_HEADERS)

    print("Sheets initialized successfully.")


if __name__ == "__main__":
    main()
