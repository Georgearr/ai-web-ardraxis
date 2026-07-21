from enum import Enum
from typing import Any

from models.member import Member
from models.event import Event
from models.faq import FAQ
from models.program import Program


_SEKBID_KEYWORDS = [
    "multimedia website", "multimedia onfield", "humas dan publikasi",
    "humas", "publikasi", "design", "dokumentasi",
    "bela negara", "ketuhanan", "sosial", "environment",
    "governance", "komunikasi", "bahasa", "apresiasi seni",
    "ilustrator", "video editor", "producer",
]


def _collect_sekbid_targets(
    msg: str,
    matched_sekbids: list[str] | None,
) -> set[str]:
    targets: set[str] = set()
    if matched_sekbids:
        targets.update(s.lower() for s in matched_sekbids)
    for kw in _SEKBID_KEYWORDS:
        if kw in msg:
            targets.add(kw.lower())
    return targets


def _sekbid_matches(targets: set[str], sekbid: str) -> bool:
    sekbid_lower = sekbid.lower()
    return any(t in sekbid_lower for t in targets)


class Intent(Enum):
    MEMBER_SEARCH = "MEMBER_SEARCH"
    EVENT_SEARCH = "EVENT_SEARCH"
    LIST_SEKBID = "LIST_SEKBID"
    COUNT_MEMBERS = "COUNT_MEMBERS"
    LIST_MEMBERS = "LIST_MEMBERS"
    FAQ = "FAQ"
    PROGRAM_SEARCH = "PROGRAM_SEARCH"
    UNKNOWN = "UNKNOWN"


_INTENT_PATTERNS: list[tuple[Intent, list[str]]] = [
    (Intent.LIST_SEKBID, [
        "sekbid apa", "sebutkan sekbid", "ada sekbid apa",
        "sekbid apa saja", "divisi apa", "ada divisi apa",
        "list sekbid", "daftar sekbid", "seluruh sekbid",
        "pembagian sekbid", "sekbid yang ada",
    ]),
    (Intent.COUNT_MEMBERS, [
        "berapa anggota", "ada berapa anggota", "total anggota",
        "jumlah anggota", "berapa banyak anggota",
        "hitung anggota", "total member", "ada berapa orang",
    ]),
    (Intent.LIST_MEMBERS, [
        "siapa saja", "tampilkan seluruh", "tampilkan semua",
        "seluruh anggota", "daftar anggota", "list anggota",
        "anggota dari",
    ]),
    (Intent.PROGRAM_SEARCH, [
        "program kerja", "proker", "program dari",
        "program apa", "program di",
    ]),
    (Intent.FAQ, [
        "apa itu", "apa sih", "bagaimana cara",
        "visi kabinet", "misi kabinet", "instagram resmi",
        "cara menghubungi",
    ]),
    (Intent.EVENT_SEARCH, [
        "event", "acara", "kegiatan",
        "open house", "expo",
    ]),
    (Intent.MEMBER_SEARCH, [
        "siapa", "siapa kah", "siapa yang",
        "ketua", "wakil ketua", "sekretaris",
        "bendahara", "koordinator",
        "mengurus", "bertanggung jawab",
    ]),
]


def detect_intent(message: str) -> Intent:
    msg = message.lower()
    for intent, patterns in _INTENT_PATTERNS:
        for pattern in patterns:
            if pattern in msg:
                return intent
    return Intent.UNKNOWN


# ---------------------------------------------------------------------------
# Data processors – each returns a dict with the information needed
# ---------------------------------------------------------------------------

def _process_list_sekbid(
    message: str,
    member_models: list[Member],
    **_kwargs,
) -> dict[str, Any]:
    uniq = sorted({m.sekbid for m in member_models if m.sekbid})
    return {"sekbid_list": uniq, "count": len(uniq)}


def _process_count_members(
    message: str,
    member_models: list[Member],
    **_kwargs,
) -> dict[str, Any]:
    return {"total": len(member_models)}


def _process_list_members(
    message: str,
    member_models: list[Member],
    matched_sekbids: list[str] | None = None,
    **_kwargs,
) -> dict[str, Any]:
    msg = message.lower()
    targets = _collect_sekbid_targets(msg, matched_sekbids)

    if not targets:
        return {"matched": []}

    matched = [m for m in member_models if _sekbid_matches(targets, m.sekbid)]
    return {"matched": matched, "sekbid_filter": list(targets)}


def _process_program_search(
    message: str,
    program_models: list[Program],
    matched_sekbids: list[str] | None = None,
    **_kwargs,
) -> dict[str, Any]:
    msg = message.lower()
    targets = _collect_sekbid_targets(msg, matched_sekbids)

    if not targets:
        return {"matched": []}

    matched = [p for p in program_models if _sekbid_matches(targets, p.sekbid)]
    return {"matched": matched, "sekbid_filter": list(targets)}


def _process_faq(
    message: str,
    faq_models: list[FAQ],
    **_kwargs,
) -> dict[str, Any]:
    msg = message.lower()
    for faq in faq_models:
        if faq.pertanyaan and faq.pertanyaan.lower() in msg:
            return {"matched": [faq], "source": "faq"}
    return {"matched": []}


def _process_event_search(
    message: str,
    event_models: list[Event],
    **_kwargs,
) -> dict[str, Any]:
    msg = message.lower()
    scored: list[tuple[int, Event]] = []
    for e in event_models:
        if e.nama_event:
            name_lower = e.nama_event.lower()
            name_tokens = name_lower.split()
            matching_tokens = sum(1 for t in name_tokens if t in msg and len(t) > 2)
            if matching_tokens > 0:
                scored.append((matching_tokens, e))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return {"matched": [e for _, e in scored]}
    return {"matched": event_models}


def _process_member_search(
    message: str,
    member_models: list[Member],
    matched_sekbids: list[str] | None = None,
    **_kwargs,
) -> dict[str, Any]:
    msg = message.lower()

    scored: list[tuple[int, Member, str]] = []

    for m in member_models:
        if m.jabatan:
            significant = [
                w.lower() for w in m.jabatan.split()
                if len(w) > 1 and not w.isnumeric()
            ]
            if significant and all(w in msg for w in significant):
                scored.append((len(m.jabatan), m, "jabatan"))

    if not scored:
        for m in member_models:
            name_tokens = [
                m.nama_lengkap.lower(),
                m.nama_panggilan.lower(),
                *m.nama_lengkap.lower().split(),
            ]
            if any(token and token in msg for token in name_tokens):
                scored.append((100, m, "name"))
                break

    if not scored:
        targets = _collect_sekbid_targets(msg, matched_sekbids)
        if targets:
            sekbid_matched = [m for m in member_models if _sekbid_matches(targets, m.sekbid)]
            for m in sekbid_matched:
                scored.append((80, m, "sekbid"))

    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        return {"matched": [m for _, m, _ in scored], "match_type": scored[0][2]}

    return {"matched": []}


_PROCESSORS: dict[Intent, Any] = {
    Intent.LIST_SEKBID: _process_list_sekbid,
    Intent.COUNT_MEMBERS: _process_count_members,
    Intent.LIST_MEMBERS: _process_list_members,
    Intent.PROGRAM_SEARCH: _process_program_search,
    Intent.FAQ: _process_faq,
    Intent.EVENT_SEARCH: _process_event_search,
    Intent.MEMBER_SEARCH: _process_member_search,
}


def process_intent(
    intent: Intent,
    message: str,
    member_models: list[Member],
    event_models: list[Event],
    faq_models: list[FAQ],
    program_models: list[Program],
    matched_sekbids: list[str] | None = None,
) -> dict[str, Any]:
    processor = _PROCESSORS.get(intent)
    if processor is None:
        return {"intent": Intent.UNKNOWN, "matched": []}
    result = processor(
        message=message,
        member_models=member_models,
        event_models=event_models,
        faq_models=faq_models,
        program_models=program_models,
        matched_sekbids=matched_sekbids,
    )
    result["intent"] = intent
    return result


# (No direct-response formatters — Gemini handles all NL generation)


# ---------------------------------------------------------------------------
# Context builder for Gemini path (minimal, intent-aware)
# ---------------------------------------------------------------------------

def _short_member_lines(m: Member) -> str:
    emoji = m.position_emoji()
    position = m.position_display()
    line = f"- {m.nama_lengkap} ({m.nama_panggilan}) - {position}"
    extras = []
    if m.instagram:
        insta_line = f"  Instagram: @{m.instagram}"
        if emoji:
            insta_line += f" {emoji}"
        extras.append(insta_line)
    if m.deskripsi:
        extras.append(f"  Deskripsi: {m.deskripsi}")
    if extras:
        line += "\n" + "\n".join(extras)
    return line


def build_intent_context(result: dict[str, Any]) -> str:
    intent = result.get("intent")
    parts: list[str] = []

    if intent == Intent.LIST_SEKBID:
        parts.append("=== DAFTAR SEKBID ===")
        for s in result.get("sekbid_list", []):
            parts.append(f"- {s}")
        parts.append(f"\nTotal: {result.get('count', 0)} Sekbid")

    elif intent == Intent.COUNT_MEMBERS:
        total = result.get("total", 0)
        parts.append(
            f"Jumlah anggota OSIS kabinet ARDRAXIS adalah {total} orang."
        )

    elif intent in (Intent.LIST_MEMBERS, Intent.MEMBER_SEARCH):
        matched = result.get("matched", [])
        if matched:
            parts.append("=== DATA ANGGOTA OSIS ===")
            for m in matched:
                parts.append(_short_member_lines(m))
        else:
            parts.append("(Tidak ada anggota yang cocok)")

    elif intent == Intent.PROGRAM_SEARCH:
        matched = result.get("matched", [])
        if matched:
            parts.append("=== DATA PROGRAM KERJA ===")
            for p in matched:
                line = f"- {p.nama_program} ({p.sekbid})"
                if p.deskripsi:
                    line += f"\n  {p.deskripsi}"
                parts.append(line)
        else:
            parts.append("(Tidak ada program kerja yang cocok)")

    elif intent == Intent.FAQ:
        matched = result.get("matched", [])
        if matched:
            parts.append("=== DATA FAQ ===")
            parts.append(f"Q: {matched[0].pertanyaan}")
            parts.append(f"A: {matched[0].jawaban}")
        else:
            parts.append("(Tidak ada FAQ yang cocok)")

    elif intent == Intent.EVENT_SEARCH:
        matched = result.get("matched", [])
        if matched:
            parts.append("=== DATA EVENT ===")
            for e in matched:
                line = f"- {e.nama_event} | {e.tanggal}"
                fields = [
                    ("Ketua Pelaksana", e.ketua_pelaksana),
                    ("Wakil Ketua Pelaksana 1", e.wakil_ketua_pelaksana_1),
                    ("Wakil Ketua Pelaksana 2", e.wakil_ketua_pelaksana_2),
                    ("Koordinator Acara", e.koordinator_acara),
                    ("Koordinator Keamanan", e.koordinator_keamanan),
                ]
                for label, value in fields:
                    if value:
                        line += f"\n  {label}: {value}"
                parts.append(line)
        else:
            parts.append("(Tidak ada event tercatat)")

    else:
        return ""

    return "\n".join(parts)
