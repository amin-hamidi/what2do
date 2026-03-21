import hashlib
import re
import unicodedata
from datetime import datetime


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


def compute_content_hash(title: str, date: datetime | None, venue: str | None) -> str:
    """SHA256 hash for event deduplication."""
    normalized = (
        f"{title.lower().strip()}"
        f"|{date.isoformat() if date else ''}"
        f"|{(venue or '').lower().strip()}"
    )
    return hashlib.sha256(normalized.encode()).hexdigest()
