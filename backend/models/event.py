from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Event:
    id: str
    nama_event: str
    tanggal: str
    lokasi: str
    instagram: Optional[str]
    deskripsi: Optional[str]

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
