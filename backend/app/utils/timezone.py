from datetime import datetime, timezone
from zoneinfo import ZoneInfo

CST = ZoneInfo("America/Chicago")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_local(dt: datetime, tz: str = "America/Chicago") -> datetime:
    """Convert a UTC datetime to a local timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo(tz))


def to_utc(dt: datetime) -> datetime:
    """Ensure a datetime is UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
