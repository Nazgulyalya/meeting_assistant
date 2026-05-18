"""Simple in-memory hash-based cache for pipeline results."""
import hashlib

_CACHE = {}

def _key(transcript: str) -> str:
    return hashlib.sha256(transcript.encode()).hexdigest()[:16]

def get_cached(transcript: str):
    return _CACHE.get(_key(transcript))

def set_cached(transcript: str, result):
    _CACHE[_key(transcript)] = result

def clear_cache():
    _CACHE.clear()

def cache_size() -> int:
    return len(_CACHE)