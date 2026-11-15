import re
import unicodedata
from uuid import uuid4


def make_slug(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    prefix = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")[:120].rstrip("-")
    return f"{prefix or 'post'}-{uuid4().hex}"
