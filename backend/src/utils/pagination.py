import base64
from datetime import datetime, timezone
from fastapi import Query
import json
from pydantic import BaseModel

from .errors import *

class PageResult(BaseModel):
    """Dados de uma página"""

    total: int
    page_size: int = 10
    previous_page: str | None = None
    current_page: str | None = None
    next_page: str | None = None
    content: list


class PageQuery(BaseModel):
    """Dados necessários para estabelecer paginação"""

    page_size: int = Query(default=10) 
    cursor: str | None = Query(default=None)
    search: str | None = Query(default=None)


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
        raise RequestError("Cursor inválido!")

    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    return date, raw_id


def build_where(basic_condition: tuple, clause_queries: PageQuery, param_queries: PageQuery, op: str | None, count: bool = False):
    """Constroi as clausulas where para paginar uma busca"""

    # Condição básica de selecionar linhas de um DB
    clauses = [basic_condition[0]]
    params = [basic_condition[1]]

    # Condição de busca
    if param_queries.search is not None:
        params.append(escape_like(param_queries.search) + "%")
        clauses.append(f"{clause_queries.search} ILIKE ${len(params)}")

    # Cursor para paginação
    if (param_queries.cursor is not None) and (not count):
        cursor_date, cursor_id = decode_cursor_to_tuple(param_queries.cursor)
        params += [cursor_date, cursor_id]
        clauses.append(f"{clause_queries.cursor} {op} (${len(params)-1}, ${len(params)})")

    if op is not None:
        params.append(param_queries.page_size +1)

    where = " AND ".join(clauses)
    return where, params


def convert_cursors_to_paths(page_result: PageResult, current_path: str) -> PageResult:
    """Converte os cursores do page_result de encoded strs para paths de rota"""

    start_index = current_path.find("cursor=")

    # Primeira busca (cursor não existe, então só colocar no final)
    if start_index == -1:
        query_char = "&" if "?" in current_path else "?"
        prev_path = None
        next_path = current_path + query_char + "cursor=" + page_result.next_page if page_result.next_page is not None else None

    # Outra busca (cursor veio de uma busca passada)
    else:
        start_index += len("cursor=")

        # Acha o que tiver depois do query parameter "cursor"
        end_index = current_path[start_index:].find("&")

        start_of_path = current_path[:start_index]
        end_of_path = current_path[start_index + end_index:] if end_index != -1 else ""

        next_path = start_of_path + page_result.next_page + end_of_path if page_result.next_page is not None else None

        # Página > 2
        if page_result.previous_page is not None:
            prev_path = start_of_path + page_result.previous_page + end_of_path

        # Página 2
        else:
            before = start_of_path[:-1*len("cursor=")]   

            # Se existia outro query parameter depois do cursor, só remove o "&cursor=abc" de dentro da string
            if len(end_of_path) != 0:
                prev_path = before + end_of_path[1:]

            # Se não existia outro query parameter depois do cursor, só tira o ? ou &
            else:
                prev_path = before.rstrip("?&")

    page_result.current_page = current_path
    page_result.previous_page = prev_path
    page_result.next_page = next_path

    return page_result