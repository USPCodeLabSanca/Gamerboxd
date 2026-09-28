from datetime import datetime
import base64
import json

def fix_date(date: datetime):
    return date.strftime("%d/%m/%Y")


def encode_tuple_to_cursor(date: datetime, id: str) -> str:
    tup = (date, id)
    json_bytes = json.dumps(tup).encode('utf-8')
    return base64.b64encode(json_bytes).decode('utf-8')


def decode_cursor_to_tuple(cursor: str) -> tuple[datetime, str]:
    decoded_list = json.loads(base64.b64decode(cursor))
    return tuple(decoded_list)