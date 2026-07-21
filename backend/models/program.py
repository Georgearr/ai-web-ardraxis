from dataclasses import dataclass, asdict


@dataclass
class Program:
    id: str
    sekbid: str
    nama_program: str
    deskripsi: str

    def to_dict(self) -> dict:
        return asdict(self)
