"""
DEPRECATED: This module is kept for backward compatibility.
New code should use services.ai_service and services.deepseek_service.
The build_context() function is still used and maintained here.
"""

from pathlib import Path

from utils.logger import logger

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
                context_parts.append(
                    f"- {m.get('nama_lengkap')} ({m.get('nama_panggilan')}) - "
                    f"{m.get('jabatan')} - {m.get('sekbid')}"
                )
                if m.get("instagram"):
                    context_parts.append(f"  Instagram: @{m.get('instagram')}")
                if m.get("deskripsi"):
                    context_parts.append(f"  Deskripsi: {m.get('deskripsi')}")
        else:
            context_parts.append(
                f"(Tidak ada anggota ditemukan untuk: {', '.join(matched_sekbids)})"
            )
    else:
        for m in members_data:
            context_parts.append(
                f"- {m.get('nama_lengkap')} ({m.get('nama_panggilan')}) - "
                f"{m.get('jabatan')} - {m.get('sekbid')}"
            )
            if m.get("instagram"):
                context_parts.append(f"  Instagram: @{m.get('instagram')}")
            if m.get("deskripsi"):
                context_parts.append(f"  Deskripsi: {m.get('deskripsi')}")

    context_parts.append("")
    context_parts.append("=== DATA EVENT ===")
    if events_data:
        for e in events_data:
            context_parts.append(
                f"- {e.get('nama_event')} | {e.get('tanggal')} | {e.get('lokasi')}"
            )
            if e.get("instagram"):
                context_parts.append(f"  Instagram: @{e.get('instagram')}")
            if e.get("deskripsi"):
                context_parts.append(f"  Deskripsi: {e.get('deskripsi')}")
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
