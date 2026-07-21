from dataclasses import dataclass, asdict


@dataclass
class FAQ:
    id: str
    pertanyaan: str
    jawaban: str

    def to_dict(self) -> dict:
        return asdict(self)
