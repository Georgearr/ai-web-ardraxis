import gspread
from google.oauth2.service_account import Credentials
from config import Config
from models.member import Member
from models.event import Event
from services.cache_manager import cache_manager
from utils.logger import logger


SHEET_COLUMNS_MEMBERS = [
    "id", "nama_panggilan", "nama_lengkap", "jabatan",
    "sekbid", "instagram", "deskripsi",
]

SHEET_COLUMNS_EVENTS = [
    "id", "nama_event", "tanggal", "lokasi", "instagram", "deskripsi",
]


def _get_client() -> gspread.Client:
    creds_data = Config.get_service_account_creds()
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    ]
    creds = Credentials.from_service_account_info(creds_data, scopes=scopes)
    return gspread.authorize(creds)


def _load_members(sheet) -> list[Member]:
    try:
        records = sheet.get_all_records(expected_headers=SHEET_COLUMNS_MEMBERS)
    except Exception:
        sheet_data = sheet.get_all_values()
        if len(sheet_data) < 2:
            return []
        headers = sheet_data[0]
        records = []
        for row in sheet_data[1:]:
            records.append(dict(zip(headers, row)))

    members = []
    for row in records:
        try:
            member = Member(
                id=str(row.get("id", "")),
                nama_panggilan=str(row.get("nama_panggilan", "")),
                nama_lengkap=str(row.get("nama_lengkap", "")),
                jabatan=str(row.get("jabatan", "")),
                sekbid=str(row.get("sekbid", "")),
                instagram=str(row.get("instagram")) if row.get("instagram") else None,
                deskripsi=str(row.get("deskripsi")) if row.get("deskripsi") else None,
            )
            if member.nama_lengkap:
                members.append(member)
        except Exception as e:
            logger.warning("Skipping malformed member row: %s", e)
            continue
    return members


def _load_events(sheet) -> list[Event]:
    try:
        records = sheet.get_all_records(expected_headers=SHEET_COLUMNS_EVENTS)
    except Exception:
        sheet_data = sheet.get_all_values()
        if len(sheet_data) < 2:
            return []
        headers = sheet_data[0]
        records = []
        for row in sheet_data[1:]:
            records.append(dict(zip(headers, row)))

    events = []
    for row in records:
        try:
            event = Event(
                id=str(row.get("id", "")),
                nama_event=str(row.get("nama_event", "")),
                tanggal=str(row.get("tanggal", "")),
                lokasi=str(row.get("lokasi", "")),
                instagram=str(row.get("instagram")) if row.get("instagram") else None,
                deskripsi=str(row.get("deskripsi")) if row.get("deskripsi") else None,
            )
            if event.nama_event:
                events.append(event)
        except Exception as e:
            logger.warning("Skipping malformed event row: %s", e)
            continue
    return events


def refresh_data():
    try:
        client = _get_client()
        sheet = client.open_by_key(Config.GOOGLE_SHEET_ID)

        members_ws = sheet.worksheet("Members")
        events_ws = sheet.worksheet("Events")

        members = _load_members(members_ws)
        events = _load_events(events_ws)

        cache_manager.set("members", members)
        cache_manager.set("events", events)

        logger.info(
            "Cache refreshed: %d members, %d events", len(members), len(events)
        )
        return members, events
    except Exception as e:
        logger.error("Failed to refresh sheet data: %s", e)
        raise


def get_members() -> list[Member]:
    cached = cache_manager.get("members")
    if cached is not None:
        return cached
    members, _ = refresh_data()
    return members


def get_events() -> list[Event]:
    cached = cache_manager.get("events")
    if cached is not None:
        return cached
    _, events = refresh_data()
    return events
