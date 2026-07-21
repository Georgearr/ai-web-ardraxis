import csv
import os
import threading
from pathlib import Path
from typing import Optional

from models.member import Member
from models.event import Event
from models.faq import FAQ
from models.program import Program
from utils.logger import logger


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _empty_to_none(value: str) -> Optional[str]:
    return value if value else None


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        logger.warning("CSV not found: %s", path)
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        logger.error("Failed to read CSV %s: %s", path, e)
        return []


class CsvDataStore:
    def __init__(self):
        self._members: list[Member] = []
        self._events: list[Event] = []
        self._faqs: list[FAQ] = []
        self._programs: list[Program] = []
        self._mtimes: dict[str, float] = {}
        self._lock = threading.Lock()
        self._load_all()

    def _mtime(self, path: Path) -> float:
        return os.path.getmtime(path) if path.exists() else 0

    def _needs_reload(self, key: str, path: Path) -> bool:
        return self._mtime(path) != self._mtimes.get(key, 0)

    def _mark_loaded(self, key: str, path: Path):
        self._mtimes[key] = self._mtime(path)

    def _load_members(self):
        path = DATA_DIR / "members.csv"
        rows = _read_csv(path)
        members = []
        for row in rows:
            try:
                member = Member(
                    id=row.get("id", ""),
                    nama_panggilan=row.get("nama_panggilan", ""),
                    nama_lengkap=row.get("nama_lengkap", ""),
                    jabatan=row.get("jabatan", ""),
                    sekbid=row.get("sekbid", ""),
                    instagram=_empty_to_none(row.get("instagram", "")),
                    deskripsi=_empty_to_none(row.get("deskripsi", "")),
                )
                if member.nama_lengkap:
                    members.append(member)
            except Exception as e:
                logger.warning("Skipping malformed member row: %s", e)
        self._members = members
        self._mark_loaded("members", path)
        logger.info("Loaded %d members from CSV", len(members))

    def _load_events(self):
        path = DATA_DIR / "events.csv"
        rows = _read_csv(path)
        events = []
        for row in rows:
            try:
                event = Event(
                    id=row.get("id", ""),
                    nama_event=row.get("nama_event", ""),
                    tanggal=row.get("tanggal", ""),
                    lokasi=row.get("lokasi", ""),
                    instagram=_empty_to_none(row.get("instagram", "")),
                    deskripsi=_empty_to_none(row.get("deskripsi", "")),
                )
                if event.nama_event:
                    events.append(event)
            except Exception as e:
                logger.warning("Skipping malformed event row: %s", e)
        self._events = events
        self._mark_loaded("events", path)
        logger.info("Loaded %d events from CSV", len(events))

    def _load_faqs(self):
        path = DATA_DIR / "faq.csv"
        rows = _read_csv(path)
        faqs = []
        for row in rows:
            try:
                faq = FAQ(
                    id=row.get("id", ""),
                    pertanyaan=row.get("pertanyaan", ""),
                    jawaban=row.get("jawaban", ""),
                )
                if faq.pertanyaan:
                    faqs.append(faq)
            except Exception as e:
                logger.warning("Skipping malformed faq row: %s", e)
        self._faqs = faqs
        self._mark_loaded("faqs", path)
        logger.info("Loaded %d FAQs from CSV", len(faqs))

    def _load_programs(self):
        path = DATA_DIR / "programs.csv"
        rows = _read_csv(path)
        programs = []
        for row in rows:
            try:
                program = Program(
                    id=row.get("id", ""),
                    sekbid=row.get("sekbid", ""),
                    nama_program=row.get("nama_program", ""),
                    deskripsi=row.get("deskripsi", ""),
                )
                if program.nama_program:
                    programs.append(program)
            except Exception as e:
                logger.warning("Skipping malformed program row: %s", e)
        self._programs = programs
        self._mark_loaded("programs", path)
        logger.info("Loaded %d programs from CSV", len(programs))

    def _load_all(self):
        self._load_members()
        self._load_events()
        self._load_faqs()
        self._load_programs()

    def _auto_reload(self):
        if self._needs_reload("members", DATA_DIR / "members.csv"):
            self._load_members()
        if self._needs_reload("events", DATA_DIR / "events.csv"):
            self._load_events()
        if self._needs_reload("faqs", DATA_DIR / "faq.csv"):
            self._load_faqs()
        if self._needs_reload("programs", DATA_DIR / "programs.csv"):
            self._load_programs()

    def get_members(self) -> list[Member]:
        with self._lock:
            self._auto_reload()
            return list(self._members)

    def get_events(self) -> list[Event]:
        with self._lock:
            self._auto_reload()
            return list(self._events)

    def get_faqs(self) -> list[FAQ]:
        with self._lock:
            self._auto_reload()
            return list(self._faqs)

    def get_programs(self) -> list[Program]:
        with self._lock:
            self._auto_reload()
            return list(self._programs)

    def refresh(self):
        with self._lock:
            self._load_all()


csv_store = CsvDataStore()
