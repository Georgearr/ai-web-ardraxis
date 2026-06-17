from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Member:
    id: str
    nama_panggilan: str
    nama_lengkap: str
    jabatan: str
    sekbid: str
    instagram: Optional[str]
    deskripsi: Optional[str]

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}
