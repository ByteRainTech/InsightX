"""
缓存
"""

from threading import RLock
from typing import Any

_cache_dict: dict[str, Any] = {}
_lock: RLock = RLock()


def store(key: str, value: Any):
    with _lock:
        _cache_dict[key] = value


def get(key: str, default=None):
    with _lock:
        return _cache_dict.get(key, default)
