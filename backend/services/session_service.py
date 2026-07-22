import time
import threading
from dataclasses import dataclass
from typing import Optional
from utils.logger import logger


SESSION_TTL = 30 * 60


@dataclass
class SessionData:
    last_intent: str = ""
    last_entity: str = ""
    last_context: str = ""
    last_member: str = ""
    last_sekbid: str = ""
    last_event: str = ""
    updated_at: float = 0.0


class SessionStore:
    def __init__(self):
        self._store: dict[str, SessionData] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> Optional[SessionData]:
        with self._lock:
            session = self._store.get(session_id)
            if not session:
                return None
            if time.time() - session.updated_at > SESSION_TTL:
                del self._store[session_id]
                logger.info("[SESSION] Session expired: %s", session_id)
                return None
            return session

    def save(
        self,
        session_id: str,
        *,
        context: str = "",
        intent: str = "",
        entity: str = "",
        last_member: str = "",
        last_sekbid: str = "",
        last_event: str = "",
    ):
        with self._lock:
            data = SessionData(
                last_intent=intent,
                last_entity=entity,
                last_context=context,
                last_member=last_member,
                last_sekbid=last_sekbid,
                last_event=last_event,
                updated_at=time.time(),
            )
            self._store[session_id] = data
        self._log_session(session_id)

    def _log_session(self, session_id: str) -> None:
        session = self._store.get(session_id)
        if not session:
            return
        logger.info("=== SESSION ===")
        logger.info("  last_member : %s", session.last_member or "-")
        logger.info("  last_sekbid : %s", session.last_sekbid or "-")
        logger.info("  last_event  : %s", session.last_event or "-")
        logger.info("=" * 14)

    def clear_expired(self):
        with self._lock:
            now = time.time()
            expired = [
                sid
                for sid, s in self._store.items()
                if now - s.updated_at > SESSION_TTL
            ]
            for sid in expired:
                del self._store[sid]
            if expired:
                logger.info(
                    "[SESSION] Cleared %d expired session(s)", len(expired)
                )

    def get_last_context(self, session_id: str) -> Optional[str]:
        session = self.get(session_id)
        if session and session.last_context:
            entity_preview = session.last_entity[:60] if session.last_entity else "(empty)"
            logger.info(
                "[SESSION] Using previous context: %s", entity_preview
            )
            return session.last_context
        return None

    def get_last_entity(self, session_id: str) -> Optional[str]:
        session = self.get(session_id)
        if session:
            return session.last_entity
        return None

    def get_last_intent(self, session_id: str) -> Optional[str]:
        session = self.get(session_id)
        if session:
            return session.last_intent
        return None

    def get_last_sekbid(self, session_id: str) -> Optional[str]:
        session = self.get(session_id)
        if session:
            return session.last_sekbid or None
        return None

    def get_last_member(self, session_id: str) -> Optional[str]:
        session = self.get(session_id)
        if session:
            return session.last_member or None
        return None

    def get_last_event(self, session_id: str) -> Optional[str]:
        session = self.get(session_id)
        if session:
            return session.last_event or None
        return None


session_store = SessionStore()
