from dataclasses import dataclass, asdict
from typing import Optional


_SUB_SEKBID_EMOJI: dict[str, str] = {
    "website": "💻",
    "web": "💻",
    "multimedia website": "💻",
    "on-field": "🎬",
    "onfield": "🎬",
    "desain": "🎨",
    "dokumentasi": "📸",
    "kreatif": "✨",
    "environment": "🌱",
    "governance": "⚖️",
    "klub olahraga": "🏅",
    "klub seni": "🎭",
    "klub penalaran": "🧠",
    "ilustrator": "🎨",
    "video editor": "🎬",
    "produser": "🎥",
    "producer": "🎥",
}

_SEKBID_EMOJI: dict[str, str] = {
    "multimedia website": "💻",
    "multimedia onfield": "🎬",
    "multimedia": "💻",
    "humas dan publikasi": "📱",
    "hubungan masyarakat dan publikasi": "📱",
    "desain, dokumentasi, dan visual": "🎨",
    "keimanan dan ketaqwaan terhadap tuhan yang maha esa": "🙏",
    "kepribadian, wawasan kebangsaan, dan bela negara": "🇮🇩",
    "sosial": "🤝",
    "environment and governance": "🌱",
    "teknologi dan komunikasi": "💻",
    "bahasa": "📖",
    "apresiasi seni dan olahraga": "🎭",
    "apresiasi seni & olahraga": "🎭",
    "broadcasting": "📺",
    "inti osis": "👑",
}


def format_position(jabatan: str, sekbid: str, sub_sekbid: str | None = None) -> str:
    if sub_sekbid:
        return f"{jabatan} {sekbid} ({sub_sekbid})"
    return f"{jabatan} - {sekbid}"


def position_emoji(sekbid: str, sub_sekbid: str | None = None) -> str:
    if sub_sekbid:
        cleaned = sub_sekbid.lower().strip()
        if cleaned in _SUB_SEKBID_EMOJI:
            return _SUB_SEKBID_EMOJI[cleaned]
    cleaned = sekbid.lower().strip()
    if cleaned in _SEKBID_EMOJI:
        return _SEKBID_EMOJI[cleaned]
    return ""


@dataclass
class Member:
    id: str
    nama_panggilan: str
    nama_lengkap: str
    jabatan: str
    sekbid: str
    sub_sekbid: Optional[str]
    instagram: Optional[str]
    deskripsi: Optional[str]

    def position_display(self) -> str:
        return format_position(self.jabatan, self.sekbid, self.sub_sekbid)

    def position_emoji(self) -> str:
        return position_emoji(self.sekbid, self.sub_sekbid)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
