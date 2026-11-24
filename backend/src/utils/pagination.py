import base64
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pydantic import BaseModel
from fastapi import Query
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .utils import escape_like, is_isoformat, op_to_dir, col_name

class PageResult(BaseModel):
    """Dados de uma página"""

    total: int
    page_len: int
    current_url: str | None = None
    next_url: str | None = None
    content: list


class PageQuery(BaseModel):
    """Dados necessários para estabelecer paginação"""

    page_size: int = Query(default=10) 
    cursor: str | None = Query(default=None)
    search: str | None = Query(default=None)
    order: str | None = Query(default=None)


@dataclass
class PageClauses:
    basic_conditions: list
    table_alias: str
    col2: str
    search_col: str


def encode_tuple_to_cursor(values: tuple):
    """Converte uma tupla para uma string de cursor"""

    values = [v.isoformat() if type(v) == datetime else v for v in values]

    payload = json.dumps(values).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def decode_cursor_to_tuple(cursor: str):
    """Converte uma string de cursor para uma tupla"""

    values = json.loads(base64.urlsafe_b64decode(cursor.encode("utf-8")))
    values = [datetime.fromisoformat(v).replace(tzinfo=timezone.utc) if is_isoformat(v) else v for v in values]

    return tuple(values)


def build_where(page_clauses: PageClauses, param_queries: PageQuery, count: bool):
    """Constroi as clausulas where para paginar uma busca"""

    # Condição básica de selecionar linhas de um DB
    clauses = [bc[0] for bc in page_clauses.basic_conditions]
    params = [bc[1] for bc in page_clauses.basic_conditions]

    # Condição de busca (ILIKE)
    if param_queries.search is not None:
        params.append(escape_like(param_queries.search) + "%")
        clauses.append(f"{page_clauses.search_col} ILIKE ${len(params)}")

    col1, col2 = col_name(page_clauses.table_alias, param_queries.order), col_name(page_clauses.table_alias, page_clauses.col2)
    op = "<" if param_queries.order[0] == "!" else ">"

    # Cursor para ordenar
    if not count:
        if (param_queries.cursor is not None):
            val1, val2 = decode_cursor_to_tuple(param_queries.cursor)
            clauses.append(f"({col1}, {col2}) {op} (${len(params)+1}, ${len(params)+2})")
            params += [val1, val2]

        params.append(param_queries.page_size+1)

    where = " AND ".join(clauses)
    order_by = f"{col1} {op_to_dir(op)}, {col2} {op_to_dir(op)}"
    cols_for_cursor = f"{col1} AS main_col, {col2} AS other_col"
    return where, order_by, cols_for_cursor, params


def convert_cursors_to_urls(page_result: PageResult, current_url: str):
    """Converte os cursores do page_result de encoded strs para urls completas"""

    next_url = None

    if page_result.next_url is not None:
        # Faz parsing da URL
        parsed_url = urlparse(current_url)

        # Preserva os demais parâmetros, remove o cursor
        query_params = [
            (key, value)
            for key, value in parse_qsl(parsed_url.query, keep_blank_values=True)
            if key != "cursor"
        ]

        # Adiciona o novo cursor
        query_params.append(("cursor", page_result.next_url))

        # Faz unparsing da URL com o novo cursor
        next_url = urlunparse(parsed_url._replace(query=urlencode(query_params)))

    # Atualiza a url
    page_result.current_url = current_url
    page_result.next_url = next_url

    return page_result