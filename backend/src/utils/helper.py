from datetime import datetime, timezone
import base64
import json

from .errors import QueryError

def fix_date(date: datetime):
    """Padroniza datas que estão no DB para uma human readable string"""
    return date.strftime("%d/%m/%Y")


def escape_like(term: str) -> str:
    """Troca caractéres que podem ser nocivos para uma cláusula LIKE pelos seus correspondentes seguros"""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def encode_tuple_to_cursor(date: datetime, id: str | int) -> str:
    """Converte uma tupla (data, id) para uma string de cursor"""

    payload = json.dumps([date.isoformat(), id]).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def decode_cursor_to_tuple(cursor: str) -> tuple[datetime, str | int]:
    """Converte uma string de cursor para uma tupla (data, id)"""

    try:
        raw_date, raw_id = json.loads(base64.urlsafe_b64decode(cursor.encode("utf-8")))
        date = datetime.fromisoformat(raw_date)

        if (type(raw_id) != int) and (type(raw_id) != str):
            raise TypeError()

    except (ValueError, TypeError):
        raise QueryError(406, "Cursor inválido!")

    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    return date, raw_id