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
    ):
        with self._lock:
            data = SessionData(
                last_intent=intent,
                last_entity=entity,
                last_context=context,
                updated_at=time.time(),
            )
            self._store[session_id] = data
            entity_preview = entity[:60] if entity else "(empty)"
            logger.info("[SESSION] New context saved: %s", entity_preview)

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


session_store = SessionStore()
