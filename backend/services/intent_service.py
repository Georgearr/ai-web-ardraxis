import re
from enum import Enum
from typing import Any, Optional

from models.member import Member
from models.event import Event
from models.faq import FAQ
from models.program import Program
from utils.logger import logger


_SEKBID_KEYWORDS = [
    "multimedia website", "multimedia onfield", "multimedia on-field",
    "onfield", "on-field", "humas dan publikasi",
    "humas", "publikasi", "design", "dokumentasi",
    "bela negara", "ketuhanan", "sosial", "environment",
    "governance", "komunikasi", "bahasa", "apresiasi seni",
    "apresiasi seni & olahraga",
    "ilustrator", "video editor", "produser",
    "desain", "kreatif", "klub olahraga", "klub seni", "klub penalaran",
]

# Maps short/alias sekbid names (from semantic service or keywords) to the
# canonical name used in the CSV.  This avoids mismatches like
# "Humas dan Publikasi" → "Hubungan Masyarakat dan Publikasi".
_SEKBID_CANONICAL: dict[str, str] = {
    "humas": "hubungan masyarakat dan publikasi",
    "humas dan publikasi": "hubungan masyarakat dan publikasi",
    "apresiasi seni": "apresiasi seni dan olahraga",
    "apresiasi seni & olahraga": "apresiasi seni dan olahraga",
    "multimedia lapangan": "multimedia onfield",
}

# Phrases that MUST trigger FAQ retrieval and NEVER member retrieval.
_SPECIAL_FAQ_PATTERNS: list[re.Pattern] = [
    re.compile(r'\btop[\s-]*3\b', re.IGNORECASE),
    re.compile(r'\btop[\s-]*three\b', re.IGNORECASE),
]


def is_special_faq_query(message: str) -> bool:
    return any(p.search(message) for p in _SPECIAL_FAQ_PATTERNS)


# ---------------------------------------------------------------------------
# Entity‑mention preprocessing – detect names / nicknames / Instagram /
# positions / sekbids in the raw message so we can force MEMBER_SEARCH
# instead of running the FAQ classifier.
# ---------------------------------------------------------------------------

def _detect_entity_mention(message: str,
                           member_models: list[Member]) -> str | None:
    """Return a label (fullname|nickname|instagram|position|sekbid|alias)
       if the message matches any member identity field, or None."""
    msg = message.lower()

    # 1) Full name
    for m in member_models:
        if m.nama_lengkap and m.nama_lengkap.lower() in msg:
            logger.info("FULLNAME MATCH: \"%s\" in \"%s\" → %s",
                        m.nama_lengkap, message, m.nama_lengkap)
            return "fullname"

    # 2) Nickname (word boundary)
    for m in member_models:
        if m.nama_panggilan:
            for sep in ('/', ','):
                for nick in m.nama_panggilan.split(sep):
                    nick = nick.strip().lower()
                    if nick and re.search(r'\b' + re.escape(nick) + r'\b', msg):
                        logger.info("NICKNAME MATCH: \"%s\" in \"%s\"  → %s",
                                    nick, message, m.nama_lengkap)
                        return "nickname"

    # 3) Instagram username
    for m in member_models:
        if m.instagram and m.instagram.lower() in msg:
            logger.info("INSTAGRAM MATCH: \"%s\" in \"%s\" → %s",
                        m.instagram, message, m.nama_lengkap)
            return "instagram"

    # 4) Position – all significant words present
    for m in member_models:
        if m.jabatan:
            significant = [w.lower() for w in m.jabatan.split()
                           if len(w) > 1 and not w.isnumeric()]
            if significant and all(w in msg for w in significant):
                logger.info("POSITION MATCH: \"%s\" in \"%s\" → %s",
                            m.jabatan, message, m.nama_lengkap)
                return "position"

    # 5) Sekbid / sub‑sekbid
    for m in member_models:
        if m.sekbid and m.sekbid.lower() in msg:
            logger.info("SEKBID MATCH: \"%s\" in \"%s\" → %s",
                        m.sekbid, message, m.nama_lengkap)
            return "sekbid"
        if m.sub_sekbid and m.sub_sekbid.lower() in msg:
            logger.info("SEKBID MATCH: \"%s\" in \"%s\" → %s",
                        m.sub_sekbid, message, m.nama_lengkap)
            return "sekbid"

    # 6) Alias – any name token (len > 3) found in query, excluding stop words
    skip_tokens = _STOP_WORDS | {"yang", "para", "saja", "dari", "dengan",
                                  "untuk", "telah", "sudah", "akan", "bisa",
                                  "dapat", "tidak", "ada", "pada", "oleh",
                                  "secara", "atau", "dan", "juga", "siapa"}
    for m in member_models:
        if m.nama_lengkap:
            name_tokens = [t for t in m.nama_lengkap.lower().split()
                           if len(t) > 3 and t not in skip_tokens]
            if any(t in msg for t in name_tokens):
                logger.info("ALIAS MATCH: token from \"%s\" in \"%s\" → %s",
                            m.nama_lengkap, message, m.nama_lengkap)
                return "alias"

    return None


# ---------------------------------------------------------------------------
# Responsibility mapping – keywords → sekbid / sub‑sekbid
# ---------------------------------------------------------------------------

_RESPONSIBILITY_MAP: list[tuple[str, str, str | None]] = [
    # Hubungan Masyarakat dan Publikasi
    ("instagram",        "Hubungan Masyarakat dan Publikasi", None),
    ("media sosial",     "Hubungan Masyarakat dan Publikasi", None),
    ("publikasi",        "Hubungan Masyarakat dan Publikasi", None),
    ("humas",            "Hubungan Masyarakat dan Publikasi", None),
    # Multimedia (Website)
    ("multimedia website",  "Multimedia", "Website"),
    ("website",          "Multimedia", "Website"),
    ("web",              "Multimedia", "Website"),
    ("hosting",          "Multimedia", "Website"),
    ("domain",           "Multimedia", "Website"),
    # Multimedia (On‑Field)
    ("multimedia onfield",  "Multimedia", "On-Field"),
    ("multimedia on-field", "Multimedia", "On-Field"),
    ("onfield",          "Multimedia", "On-Field"),
    ("on-field",         "Multimedia", "On-Field"),
    ("kamera",           "Multimedia", "On-Field"),
    ("obs",              "Multimedia", "On-Field"),
    ("streaming",        "Multimedia", "On-Field"),
    ("livestream",       "Multimedia", "On-Field"),
    ("lighting",         "Multimedia", "On-Field"),
    ("sound system",     "Multimedia", "On-Field"),
    ("videotron",        "Multimedia", "On-Field"),
    ("audio",            "Multimedia", "On-Field"),
    # Multimedia (general – when only "multimedia" is mentioned)
    ("multimedia",       "Multimedia", None),
    # Desain, Dokumentasi, dan Visual (general)
    ("kreatif",          "Desain, Dokumentasi, dan Visual", "Kreatif"),
    # Dokumentasi (sub‑sekbid of Desain, Dokumentasi, dan Visual)
    ("foto",             "Desain, Dokumentasi, dan Visual", "Dokumentasi"),
    ("video",            "Desain, Dokumentasi, dan Visual", "Dokumentasi"),
    ("dokumentasi",      "Desain, Dokumentasi, dan Visual", "Dokumentasi"),
    # Desain (sub‑sekbid of Desain, Dokumentasi, dan Visual)
    ("poster",           "Desain, Dokumentasi, dan Visual", "Desain"),
    ("design",           "Desain, Dokumentasi, dan Visual", "Desain"),
    ("desain",           "Desain, Dokumentasi, dan Visual", "Desain"),
    ("banner",           "Desain, Dokumentasi, dan Visual", "Desain"),
    ("feed",             "Desain, Dokumentasi, dan Visual", "Desain"),
    # Kepribadian, Wawasan Kebangsaan, dan Bela Negara
    ("bela negara",      "Kepribadian, Wawasan Kebangsaan, dan Bela Negara", None),
    ("wawasan kebangsaan", "Kepribadian, Wawasan Kebangsaan, dan Bela Negara", None),
    ("kebangsaan",       "Kepribadian, Wawasan Kebangsaan, dan Bela Negara", None),
    ("keamanan",         "Kepribadian, Wawasan Kebangsaan, dan Bela Negara", None),
    ("kepribadian",      "Kepribadian, Wawasan Kebangsaan, dan Bela Negara", None),
    # Keimanan dan Ketaqwaan Terhadap Tuhan Yang Maha Esa
    ("keimanan",         "Keimanan dan Ketaqwaan Terhadap Tuhan Yang Maha Esa", None),
    ("ketaqwaan",        "Keimanan dan Ketaqwaan Terhadap Tuhan Yang Maha Esa", None),
    ("agama",            "Keimanan dan Ketaqwaan Terhadap Tuhan Yang Maha Esa", None),
    ("rohani",           "Keimanan dan Ketaqwaan Terhadap Tuhan Yang Maha Esa", None),
    # Sosial
    ("sosial",           "Sosial", None),
    # Bahasa
    ("bahasa",           "Bahasa", None),
    # Teknologi dan Komunikasi
    ("teknologi",        "Teknologi dan Komunikasi", None),
    ("komunikasi",       "Teknologi dan Komunikasi", None),
    ("tik",              "Teknologi dan Komunikasi", None),
    # Apresiasi Seni dan Olahraga
    ("acara",            "Apresiasi Seni dan Olahraga", None),
    ("seni",             "Apresiasi Seni dan Olahraga", None),
    ("olahraga",         "Apresiasi Seni dan Olahraga", None),
    ("klub",             "Apresiasi Seni dan Olahraga", None),
    ("apresiasi seni",   "Apresiasi Seni dan Olahraga", None),
    # Broadcasting
    ("broadcasting",     "Broadcasting", None),
    ("ilustrator",       "Broadcasting", "Ilustrator"),
    ("produser",         "Broadcasting", "Produser"),
    ("video editor",     "Broadcasting", "Video Editor"),
    # Environment and Governance
    ("environment",      "Environment and Governance", "Environment"),
    ("governance",       "Environment and Governance", "Governance"),
    ("lingkungan",       "Environment and Governance", "Environment"),
]


def _detect_responsibility(message: str,
                           member_models: list[Member] | None = None) -> Optional[dict]:
    """Return first matching responsibility mapping, or None.

    Tries the explicit keyword-to-sekbid map first.  As a fallback, checks
    whether the message contains a known sekbid / sub-sekbid token and, if
    the query also contains a responsibility-style trigger word (mengurus,
    bertanggung jawab, menangani, mengelola, divisi, tim, anggota), returns
    that sekbid with no sub-sekbid.
    """
    msg = message.lower()

    # Phase 1 – explicit keyword map (longest match wins)
    for kw, sekbid, sub in sorted(_RESPONSIBILITY_MAP,
                                   key=lambda x: len(x[0]), reverse=True):
        if kw in msg:
            return {"sekbid": sekbid, "sub_sekbid": sub, "keyword": kw}

    # Phase 2 – fallback: does the query mention a sekbid name directly?
    # Only activate when the query style sounds like a "who handles X" question.
    _TRIGGERS = ("mengurus", "bertanggung jawab", "menangani", "mengelola",
                 "divisi", "tim", "anggota")
    if not any(t in msg for t in _TRIGGERS):
        return None

    # Check _SEKBID_KEYWORDS
    for kw in _SEKBID_KEYWORDS:
        if kw in msg:
            # Try to find the canonical sekbid name by matching against members
            if member_models:
                for m in member_models:
                    if m.sekbid and kw in m.sekbid.lower():
                        return {"sekbid": m.sekbid, "sub_sekbid": None,
                                "keyword": kw}
                    if m.sub_sekbid and kw in m.sub_sekbid.lower():
                        return {"sekbid": m.sekbid, "sub_sekbid": m.sub_sekbid,
                                "keyword": kw}
            return {"sekbid": kw.title(), "sub_sekbid": None, "keyword": kw}

    # Check member sekbid / sub-sekbid names directly
    if member_models:
        for m in member_models:
            if m.sekbid and m.sekbid.lower() in msg:
                return {"sekbid": m.sekbid, "sub_sekbid": None, "keyword": m.sekbid.lower()}
            if m.sub_sekbid and m.sub_sekbid.lower() in msg:
                return {"sekbid": m.sekbid, "sub_sekbid": m.sub_sekbid,
                        "keyword": m.sub_sekbid.lower()}

    return None


def _norm_sekbid(s: str) -> str:
    return re.sub(r'[\s-]+', ' ', s).strip().lower()


def _squash_sekbid(s: str) -> str:
    return re.sub(r'[\s-]+', '', s).lower()


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


def _member_matches_sekbid(targets: set[str], member: Member) -> bool:
    sekbid_norm = _norm_sekbid(member.sekbid) if member.sekbid else ""
    sub_norm = _norm_sekbid(member.sub_sekbid) if member.sub_sekbid else ""
    combined_norm = f"{sekbid_norm} {sub_norm}" if sub_norm else sekbid_norm
    sekbid_sq = _squash_sekbid(member.sekbid) if member.sekbid else ""
    sub_sq = _squash_sekbid(member.sub_sekbid) if member.sub_sekbid else ""
    combined_sq = f"{sekbid_sq}{sub_sq}" if sub_sq else sekbid_sq

    candidates: set[str] = set()
    for t in targets:
        resolved = _SEKBID_CANONICAL.get(t, t)
        candidates.add(_norm_sekbid(t))
        candidates.add(_squash_sekbid(t))
        candidates.add(_norm_sekbid(resolved))
        candidates.add(_squash_sekbid(resolved))

    for t in candidates:
        if t == sekbid_norm or t == sekbid_sq:
            return True
        if sub_norm and (t == sub_norm or t == sub_sq):
            return True
        if sub_norm and (t == combined_norm or t == combined_sq):
            return True
        if sub_norm and (t in sub_norm or t in sub_sq):
            return True
        tw = t.split()
        if len(tw) > 1 and all(w in combined_norm for w in tw):
            return True
        if not sub_norm and (t in sekbid_norm or t in sekbid_sq):
            return True
    return False


def _log_search(mode: str, keyword, matched: list):
    names = "\n".join(f"- {m.nama_lengkap}" for m in matched)
    parts = [f"[SEARCH]\nMode: {mode}"]
    if keyword:
        kw = ", ".join(keyword) if isinstance(keyword, (set, list)) else str(keyword)
        parts.append(f"\nKeyword:\n{kw}")
    if matched:
        parts.append(f"\nMatched:\n{names}")
    parts.append(f"\nTotal:\n{len(matched)} member(s)")
    logger.info("".join(parts))


class Intent(Enum):
    MEMBER_SEARCH = "MEMBER_SEARCH"
    EVENT_SEARCH = "EVENT_SEARCH"
    LIST_SEKBID = "LIST_SEKBID"
    COUNT_MEMBERS = "COUNT_MEMBERS"
    LIST_MEMBERS = "LIST_MEMBERS"
    FAQ = "FAQ"
    PROGRAM_SEARCH = "PROGRAM_SEARCH"
    RESPONSIBILITY = "RESPONSIBILITY"
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
            if re.search(r'\b' + re.escape(pattern) + r'\b', msg):
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

    matched = [m for m in member_models if _member_matches_sekbid(targets, m)]
    if matched:
        mode = "SUB_SEKBID" if any(m.sub_sekbid for m in matched) else "SEKBID"
        _log_search(mode, targets, matched)
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


_STOP_WORDS: frozenset = frozenset({
    "apa", "itu", "yang", "siapa", "bagaimana", "kah", "dong",
    "tolong", "di", "ke", "dari", "adalah", "dan", "atau",
    "ini", "tersebut", "para", "saja", "dengan", "untuk",
    "juga", "sudah", "telah", "akan", "bisa", "dapat",
    "tidak", "ada", "pada", "oleh", "sebagai", "secara",
    "no", "yg",
})

_MIN_FAQ_SCORE = 2


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r'\b\w+\b', text.lower())
    result: set[str] = set()
    for t in tokens:
        if t not in _STOP_WORDS and len(t) > 1:
            result.add(t)
        # Split mixed alpha‑numeric tokens so "top3" yields {"top3", "top"}
        for part in re.split(r'(\d+)', t):
            if part and part not in _STOP_WORDS and len(part) > 1 and part != t:
                result.add(part)
    return result


def _process_faq(
    message: str,
    faq_models: list[FAQ],
    **_kwargs,
) -> dict[str, Any]:
    msg = message.lower()
    query_tokens = _tokenize(msg)

    logger.info("=== FAQ SEARCH ===")
    logger.info("Query    : %s", message)
    logger.info("Tokens   : %s", sorted(query_tokens) if query_tokens else "(empty)")

    scored: list[tuple[int, FAQ]] = []
    if query_tokens:
        for faq in faq_models:
            if not faq.pertanyaan:
                continue
            faq_tokens = _tokenize(faq.pertanyaan)
            overlap = len(query_tokens & faq_tokens)
            n = len(query_tokens)
            if n <= 2:
                # Short queries: ALL non-stop tokens must appear in FAQ
                if overlap == n:
                    scored.append((overlap, faq))
                    logger.info("  FAQ[%s] score=%d (all=%d) : %.50s", faq.id, overlap, n, faq.pertanyaan)
            else:
                # Long queries: at least 2 tokens must overlap
                if overlap >= _MIN_FAQ_SCORE:
                    scored.append((overlap, faq))
                    logger.info("  FAQ[%s] score=%d : %.50s", faq.id, overlap, faq.pertanyaan)

    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_faq = scored[0]
        logger.info("Selected : %s (score=%d)", best_faq.pertanyaan[:60], best_score)
        logger.info("=" * 30)
        return {"matched": [best_faq], "source": "faq"}

    logger.info("No FAQ matched")
    logger.info("=" * 30)
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

    # --- PRIORITY 1: Name search (most specific) ---
    for m in member_models:
        if m.nama_lengkap and m.nama_lengkap.lower() in msg:
            _log_search("NAME", None, [m])
            return {"matched": [m], "match_type": "name"}
        if m.nama_panggilan:
            for sep in ('/', ','):
                for nick in m.nama_panggilan.split(sep):
                    nick = nick.strip().lower()
                    if nick and re.search(r'\b' + re.escape(nick) + r'\b', msg):
                        _log_search("NAME", None, [m])
                        return {"matched": [m], "match_type": "name"}
        # Instagram username match
        if m.instagram and m.instagram.lower() in msg:
            _log_search("INSTAGRAM", None, [m])
            return {"matched": [m], "match_type": "instagram"}
        name_tokens = [t for t in m.nama_lengkap.lower().split() if len(t) > 2]
        if any(token in msg for token in name_tokens):
            _log_search("NAME", None, [m])
            return {"matched": [m], "match_type": "name"}

    # --- PRIORITY 2: Sekbid / Sub-sekbid (division match) ---
    targets = _collect_sekbid_targets(msg, matched_sekbids)
    if targets:
        sekbid_candidates = [m for m in member_models if _member_matches_sekbid(targets, m)]
        if sekbid_candidates:
            scored = _filter_scored_members(msg, sekbid_candidates, matched_sekbids)
            _log_member_scoring(msg, sekbid_candidates, matched_sekbids)
            if scored:
                mode = "SUB_SEKBID" if any(m.sub_sekbid for m in scored) else "SEKBID"
                _log_search(mode, targets, scored)
                return {"matched": scored, "match_type": "sekbid"}
            # All candidates scored 0 → no genuine match
            _log_search("SEKBID_ZERO_SCORE", targets, [])
            logger.info("All %d sekbid candidates scored 0 – skipping member retrieval",
                         len(sekbid_candidates))

    # --- PRIORITY 3: Position / Jabatan (broadest) ---
    scored = []
    for m in member_models:
        if m.jabatan:
            significant = [
                w.lower() for w in m.jabatan.split()
                if len(w) > 1 and not w.isnumeric()
            ]
            if significant and all(w in msg for w in significant):
                scored.append((len(m.jabatan), m, "jabatan"))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        matched = [m for _, m, _ in scored]
        keywords = {m.jabatan.lower() for _, m, _ in scored}
        _log_search("JABATAN", keywords, matched)
        return {"matched": matched, "match_type": "jabatan"}

    return {"matched": []}


def _score_member(msg: str, member: Member,
                  matched_sekbids: list[str] | None = None) -> int:
    msg_lower = msg.lower()
    score = 0

    # 1) Full‑name phrase match (highest confidence)
    if member.nama_lengkap and member.nama_lengkap.lower() in msg_lower:
        score += 5

    # 2) Nickname word‑boundary match
    if member.nama_panggilan:
        for sep in ('/', ','):
            for nick in member.nama_panggilan.split(sep):
                nick = nick.strip().lower()
                if nick and re.search(r'\b' + re.escape(nick) + r'\b', msg_lower):
                    score += 4

    # 3) Instagram username match
    if member.instagram and member.instagram.lower() in msg_lower:
        score += 4

    # 4) All significant position words present in query
    if member.jabatan:
        significant = [w.lower() for w in member.jabatan.split()
                       if len(w) > 1 and not w.isnumeric()]
        if significant and all(w in msg_lower for w in significant):
            score += 3

    # 4) Token overlap with sekbid / sub‑sekbid (only from msg, not session)
    msg_tokens = {t for t in re.findall(r'\b\w+\b', msg_lower) if len(t) > 1}
    if member.sekbid:
        st = {t for t in re.findall(r'\b\w+\b', member.sekbid.lower()) if len(t) > 1}
        st.add(_squash_sekbid(member.sekbid))
        if msg_tokens & st:
            score += 3
    if member.sub_sekbid:
        st = {t for t in re.findall(r'\b\w+\b', member.sub_sekbid.lower()) if len(t) > 1}
        st.add(_squash_sekbid(member.sub_sekbid))
        if msg_tokens & st:
            score += 3

    # 5) Any name token (len > 2) found in the query
    if member.nama_lengkap:
        name_tokens = [t for t in member.nama_lengkap.lower().split() if len(t) > 2]
        if any(t in msg_lower for t in name_tokens):
            score += 2

    # 6) Contextual match via matched_sekbids (session / semantic injection)
    #    Only used when NO direct textual evidence exists.
    if matched_sekbids and score == 0:
        for sekbid in matched_sekbids:
            if _member_matches_sekbid({sekbid.lower()}, member):
                score = 1
                break
    return score


def _log_member_scoring(msg: str, members: list[Member],
                        matched_sekbids: list[str] | None = None):
    logger.info("=== MEMBER SCORING ===")
    for m in members:
        s = _score_member(msg, m, matched_sekbids)
        logger.info("%s", "")
        logger.info("%s", m.nama_lengkap)
        logger.info("score: %d", s)
        logger.info("matched keyword:")
    logger.info("=" * 30)


def _filter_scored_members(msg: str, members: list[Member],
                           matched_sekbids: list[str] | None = None) -> list[Member]:
    scored = [(m, _score_member(msg, m, matched_sekbids)) for m in members]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, s in scored if s > 0]


def _process_responsibility(
    message: str,
    member_models: list[Member],
    **_kwargs,
) -> dict[str, Any]:
    resp = _detect_responsibility(message)
    if not resp:
        return {"matched": []}

    sekbid = resp["sekbid"]
    sub_sekbid = resp.get("sub_sekbid")

    # Find all members matching this division
    matched = [m for m in member_models if m.sekbid and m.sekbid.lower() == sekbid.lower()]
    if sub_sekbid:
        matched = [m for m in matched if m.sub_sekbid and m.sub_sekbid.lower() == sub_sekbid.lower()]

    if not matched:
        return {"matched": []}

    # Sort so coordinator / ketua comes first
    matched.sort(key=lambda m: 0 if m.jabatan and any(
        t in m.jabatan.lower() for t in ("koordinator", "ketua")
    ) else 1)

    resp["keyword"] = next(
        (kw for kw, _, _ in _RESPONSIBILITY_MAP if kw in message.lower()),
        None,
    )

    logger.info("=== SEKBID MATCH ===")
    sekbid_label = f"{sekbid} ({sub_sekbid})" if sub_sekbid else sekbid
    logger.info("Matched Sekbid:")
    logger.info(sekbid_label)
    logger.info("")
    logger.info("Matched Members:")
    for m in matched:
        logger.info("- %s (%s)", m.nama_lengkap, m.jabatan or "-")
    logger.info("")
    logger.info("Total:")
    logger.info("%d members", len(matched))
    logger.info("=" * 30)

    return {
        "matched": matched,
        "responsibility": resp,
    }


def has_sekbid_mention(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in _SEKBID_KEYWORDS)


_PROCESSORS: dict[Intent, Any] = {
    Intent.LIST_SEKBID: _process_list_sekbid,
    Intent.COUNT_MEMBERS: _process_count_members,
    Intent.LIST_MEMBERS: _process_list_members,
    Intent.PROGRAM_SEARCH: _process_program_search,
    Intent.FAQ: _process_faq,
    Intent.EVENT_SEARCH: _process_event_search,
    Intent.MEMBER_SEARCH: _process_member_search,
    Intent.RESPONSIBILITY: _process_responsibility,
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
            return ""

    elif intent == Intent.RESPONSIBILITY:
        matched = result.get("matched", [])
        resp = result.get("responsibility") or {}
        if not matched:
            return ""
        sekbid = resp.get("sekbid", "")
        sub = resp.get("sub_sekbid")
        sekbid_display = f"{sekbid} ({sub})" if sub else sekbid
        parts.append("=== SEKBID ===")
        parts.append("")
        parts.append(f"Nama Sekbid:")
        parts.append(sekbid_display)
        parts.append("")
        coordinators = [m for m in matched
                        if m.jabatan and 'koordinator' in m.jabatan.lower()]
        if coordinators:
            coord_names = {c.nama_lengkap for c in coordinators}
            parts.append("Koordinator:")
            for c in coordinators:
                parts.append(f"{c.nama_lengkap} ({c.nama_panggilan})")
            parts.append("")
            anggota = [m for m in matched if m.nama_lengkap not in coord_names]
        else:
            anggota = list(matched)
        parts.append("Anggota:")
        for a in anggota:
            parts.append(f"- {a.nama_lengkap} ({a.nama_panggilan}) - {a.jabatan or '-'}")

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
            return ""

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
