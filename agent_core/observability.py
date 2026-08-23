import os
from langfuse import get_client

_enabled = bool(
    os.getenv("LANGFUSE_PUBLIC_KEY")
    and os.getenv("LANGFUSE_SECRET_KEY")
)

langfuse = get_client() if _enabled else None

def is_enabled():
    return _enabled and langfuse is not None

def flush():
    if langfuse is not None:
        langfuse.flush()
