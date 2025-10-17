import os


def load_env(key, default=None, cast=str):
    v = os.getenv(key, default)
    try:
        return cast(v) if v is not None else None
    except Exception:
        return v

