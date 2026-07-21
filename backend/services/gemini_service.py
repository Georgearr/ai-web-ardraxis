"""
DEPRECATED: This module is kept for backward compatibility.
New code should use services.ai_service and services.deepseek_service.
The build_context() function is still used and maintained here.
"""

from pathlib import Path

from utils.logger import logger
from models.member import format_position, position_emoji

BACKEND_DIR = Path(__file__).resolve().parent.parent
SYSTEM_PROMPT_PATH = BACKEND_DIR / "prompts" / "system_prompt.txt"


def _load_system_prompt() -> str:
    try:
        with open(SYSTEM_PROMPT_PATH, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning("system_prompt.txt not found, using default prompt")
        return (
            "You are DRAX, the official AI Assistant for OSIS SMA Ignatius Global School. "
            "Answer only using the provided data. Never hallucinate."
        )


SYSTEM_PROMPT = _load_system_prompt()


def build_context(
    members_data: list[dict],
    events_data: list[dict],
    faqs_data: list[dict],
    programs_data: list[dict],
    matched_sekbids: list[str] | None = None,
) -> str:
    context_parts = []

    context_parts.append("=== DATA ANGGOTA OSIS ===")
    if matched_sekbids:
        filtered = [
            m for m in members_data
            if m.get("sekbid", "").lower()
            in [s.lower() for s in matched_sekbids]
        ]
        if filtered:
            context_parts.append(
                f"(Menampilkan anggota dari: {', '.join(matched_sekbids)})"
            )
            for m in filtered:
                pos = format_position(
                    m.get("jabatan", ""),
                    m.get("sekbid", ""),
                    m.get("sub_sekbid"),
                )
                emoji = position_emoji(
                    m.get("sekbid", ""),
                    m.get("sub_sekbid"),
                )
                context_parts.append(
                    f"- {m.get('nama_lengkap')} ({m.get('nama_panggilan')}) - {pos}"
                )
                if m.get("instagram"):
                    insta_line = f"  Instagram: @{m.get('instagram')}"
                    if emoji:
                        insta_line += f" {emoji}"
                    context_parts.append(insta_line)
                if m.get("deskripsi"):
                    context_parts.append(f"  Deskripsi: {m.get('deskripsi')}")
        else:
            context_parts.append(
                f"(Tidak ada anggota ditemukan untuk: {', '.join(matched_sekbids)})"
            )
    else:
        for m in members_data:
            pos = format_position(
                m.get("jabatan", ""),
                m.get("sekbid", ""),
                m.get("sub_sekbid"),
            )
            emoji = position_emoji(
                m.get("sekbid", ""),
                m.get("sub_sekbid"),
            )
            context_parts.append(
                f"- {m.get('nama_lengkap')} ({m.get('nama_panggilan')}) - {pos}"
            )
            if m.get("instagram"):
                insta_line = f"  Instagram: @{m.get('instagram')}"
                if emoji:
                    insta_line += f" {emoji}"
                context_parts.append(insta_line)
            if m.get("deskripsi"):
                context_parts.append(f"  Deskripsi: {m.get('deskripsi')}")

    context_parts.append("")
    context_parts.append("=== DATA EVENT ===")
    if events_data:
        for e in events_data:
            line = f"- {e.get('nama_event')} | {e.get('tanggal')}"
            for label, key in [
                ("Ketua Pelaksana", "ketua_pelaksana"),
                ("Wakil Ketua Pelaksana 1", "wakil_ketua_pelaksana_1"),
                ("Wakil Ketua Pelaksana 2", "wakil_ketua_pelaksana_2"),
                ("Koordinator Acara", "koordinator_acara"),
                ("Koordinator Keamanan", "koordinator_keamanan"),
            ]:
                val = e.get(key)
                if val:
                    line += f"\n  {label}: {val}"
            context_parts.append(line)
    else:
        context_parts.append("(Tidak ada event tercatat)")

    context_parts.append("")
    context_parts.append("=== DATA PROGRAM KERJA ===")
    if programs_data:
        for p in programs_data:
            context_parts.append(
                f"- {p.get('nama_program')} ({p.get('sekbid')}) - {p.get('deskripsi')}"
            )
    else:
        context_parts.append("(Tidak ada program kerja tercatat)")

    context_parts.append("")
    context_parts.append("=== DATA FAQ ===")
    if faqs_data:
        for faq in faqs_data:
            context_parts.append(
                f"Q: {faq.get('pertanyaan')}"
            )
            context_parts.append(
                f"A: {faq.get('jawaban')}"
            )
    else:
        context_parts.append("(Tidak ada FAQ tercatat)")

    return "\n".join(context_parts)
