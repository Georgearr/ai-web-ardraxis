from models.member import Member
from models.event import Event


MOCK_MEMBERS = [
    Member(
        id="1",
        nama_panggilan="George",
        nama_lengkap="George Alexander",
        jabatan="Ketua OSIS",
        sekbid="Top Management",
        instagram="osis.smaigs",
        deskripsi="Memimpin kabinet ARDRAXIS periode 2025/2026.",
    ),
    Member(
        id="2",
        nama_panggilan="Justin",
        nama_lengkap="Justin Michael",
        jabatan="Wakil Ketua OSIS 1",
        sekbid="Top Management",
        instagram="osis.smaigs",
        deskripsi="Bertanggung jawab atas koordinasi internal OSIS.",
    ),
    Member(
        id="3",
        nama_panggilan="Chris",
        nama_lengkap="Christopher Lee",
        jabatan="Koordinator",
        sekbid="Multimedia Website",
        instagram="ardraxis.web",
        deskripsi="Mengurus website dan sistem digital ARDRAXIS.",
    ),
    Member(
        id="4",
        nama_panggilan="Sarah",
        nama_lengkap="Sarah Wijaya",
        jabatan="Koordinator",
        sekbid="Humas dan Publikasi",
        instagram="ardraxis.humas",
        deskripsi="Mengelola media sosial dan publikasi resmi OSIS.",
    ),
]

MOCK_EVENTS = [
    Event(
        id="1",
        nama_event="OSIS Expo 2026",
        tanggal="15 Maret 2026",
        lokasi="Aula SMA Ignatius Global School",
        instagram="osis.smaigs",
        deskripsi="Pameran program kerja dan pendaftaran ekstrakurikuler OSIS.",
    ),
    Event(
        id="2",
        nama_event="Charity Concert ARDRAXIS",
        tanggal="20 April 2026",
        lokasi="Gedung Serbaguna SMAIGS",
        instagram="ardraxis.event",
        deskripsi="Konser amal untuk mendukung program sosial kabinet ARDRAXIS.",
    ),
]


def get_mock_members() -> list[Member]:
    return MOCK_MEMBERS


def get_mock_events() -> list[Event]:
    return MOCK_EVENTS


def _format_member(member: Member) -> str:
    lines = [
        f"Nama:\n{member.nama_lengkap}",
        f"\nJabatan:\n{member.jabatan}",
        f"\nSekbid:\n{member.sekbid}",
    ]
    if member.instagram:
        lines.append(f"\nInstagram:\n@{member.instagram}")
    if member.deskripsi:
        lines.append(f"\nDeskripsi:\n{member.deskripsi}")
    return "".join(lines)


def _format_event(event: Event) -> str:
    lines = [
        f"Nama Event:\n{event.nama_event}",
        f"\nTanggal:\n{event.tanggal}",
        f"\nLokasi:\n{event.lokasi}",
    ]
    if event.instagram:
        lines.append(f"\nInstagram:\n@{event.instagram}")
    if event.deskripsi:
        lines.append(f"\nDeskripsi:\n{event.deskripsi}")
    return "".join(lines)


def mock_ai_response(
    user_message: str,
    members: list[Member],
    events: list[Event],
) -> str:
    message = user_message.lower()

    if any(word in message for word in ("event", "acara", "kegiatan")):
        if events:
            return _format_event(events[0])
        return "Maaf, saya belum menemukan informasi tersebut pada database resmi ARDRAXIS. 🔥"

    for member in members:
        name_tokens = [
            member.nama_lengkap.lower(),
            member.nama_panggilan.lower(),
            *member.nama_lengkap.lower().split(),
        ]
        if any(token and token in message for token in name_tokens):
            return _format_member(member)

    role_keywords = {
        "ketua": "ketua osis",
        "wakil": "wakil ketua",
        "website": "multimedia website",
        "instagram": "humas dan publikasi",
        "humas": "humas dan publikasi",
    }
    for keyword, target in role_keywords.items():
        if keyword in message:
            for member in members:
                haystack = f"{member.jabatan} {member.sekbid}".lower()
                if target in haystack:
                    return _format_member(member)

    if any(word in message for word in ("berapa", "jumlah", "total")) and "anggota" in message:
        return f"Saat ini terdapat {len(members)} anggota OSIS yang tercatat pada database resmi ARDRAXIS. ✨"

    if "instagram" in message and "osis" in message:
        for member in members:
            if member.jabatan.lower() == "ketua osis" and member.instagram:
                return f"Instagram resmi OSIS: @{member.instagram} 📱"

    return (
        "Maaf, saya belum menemukan informasi tersebut pada database resmi ARDRAXIS. 🔥\n\n"
        "Coba tanyakan tentang Ketua OSIS, event terdekat, atau anggota Multimedia Website."
    )
