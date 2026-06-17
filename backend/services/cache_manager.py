from cachetools import TTLCache
from config import Config


class CacheManager:
    def __init__(self):
        self._cache = TTLCache(
            maxsize=100,
            ttl=Config.CACHE_TTL_SECONDS,
        )

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value):
        self._cache[key] = value

    def invalidate(self, key: str):
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()

    @property
    def is_loaded(self) -> bool:
        return "members" in self._cache and "events" in self._cache


cache_manager = CacheManager()
