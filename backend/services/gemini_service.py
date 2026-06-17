import google.generativeai as genai
from config import Config
from utils.logger import logger


SYSTEM_PROMPT_PATH = "system_prompt.txt"


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


def init_gemini():
    genai.configure(api_key=Config.GEMINI_API_KEY)


def build_context(
    members_data: list[dict],
    events_data: list[dict],
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

    return "\n".join(context_parts)


SYSTEM_PROMPT = _load_system_prompt()


def ask_gemini(user_message: str, context: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\n\nPertanyaan: {user_message}"
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        return "Maaf, terjadi kesalahan saat memproses pertanyaan Anda. Silakan coba lagi."
