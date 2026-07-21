from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Event:
    id: str
    nama_event: str
    tanggal: str
    ketua_pelaksana: Optional[str]
    wakil_ketua_pelaksana_1: Optional[str]
    wakil_ketua_pelaksana_2: Optional[str]
    koordinator_acara: Optional[str]
    koordinator_keamanan: Optional[str]

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
