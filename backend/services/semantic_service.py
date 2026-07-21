import re


SEMANTIC_MAP: dict[str, str] = {
    "website": "Multimedia Website",
    "developer": "Multimedia Website",
    "programmer": "Multimedia Website",
    "technology": "Multimedia Website",
    "instagram": "Humas dan Publikasi",
    "media sosial": "Humas dan Publikasi",
    "publikasi": "Humas dan Publikasi",
    "mc": "Komunikasi",
    "lighting": "Multimedia Onfield",
    "sound system": "Multimedia Onfield",
    "sound system": "Multimedia Onfield",
    "videotron": "Multimedia Onfield",
    "feedback": "Governance",
    "kritik": "Governance",
    "saran": "Governance",
    "video": "Video Editor",
    "script": "Producer",
}


def find_sekbids(message: str) -> list[str]:
    message_lower = message.lower()
    matched: set[str] = set()
    for keyword, sekbid in SEMANTIC_MAP.items():
        if keyword in message_lower:
            matched.add(sekbid)
    return list(matched)
