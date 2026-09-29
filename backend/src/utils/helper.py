from datetime import datetime, timezone
import base64
import json

from .utils import QueryError

def fix_date(date: datetime):
    return date.strftime("%d/%m/%Y")


def escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def encode_tuple_to_cursor(date: datetime, id: str | int) -> str:
    payload = json.dumps([date.isoformat(), id]).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def decode_cursor_to_tuple(cursor: str) -> tuple[datetime, str | int]:
    try:
        raw_date, raw_id = json.loads(base64.urlsafe_b64decode(cursor.encode("utf-8")))
        date = datetime.fromisoformat(raw_date)

    except (ValueError, TypeError):
        raise QueryError(400, "Erro no cursor")

    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    return date, raw_id