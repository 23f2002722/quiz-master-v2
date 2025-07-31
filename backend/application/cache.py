import os, json, functools, hashlib
import redis
from flask import request, current_app

_redis = None

def get_redis():
    global _redis
    if _redis is None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis = redis.from_url(url, decode_responses=True)
    return _redis

def _cache_key(prefix: str):
    raw = f"{prefix}:{request.path}:{sorted(request.args.items())}"
    return "cache:" + hashlib.sha256(raw.encode()).hexdigest()

def cache_response(timeout=60):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                r = get_redis()
                key = _cache_key(fn.__name__)
                cached = r.get(key)
                if cached:
                    return current_app.response_class(cached, mimetype="application/json")
                resp = fn(*args, **kwargs)
                data, status = resp if isinstance(resp, tuple) else (resp, 200)
                if hasattr(data, 'get_data'):
                    body = data.get_data(as_text=True)
                else:
                    body = json.dumps(data)
                r.setex(key, timeout, body)
                return resp
            except Exception:
                return fn(*args, **kwargs)
        return wrapper
    return decorator