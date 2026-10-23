from datetime import datetime
from functools import wraps
from .errors import QueryError
from enum import IntEnum


class RelationshipStatus(IntEnum):
    """Possíveis relações entre 2 usuários"""
    BLOCKED = -20
    BLOCKER = -10
    ANY = 0
    FOLLOWER = 10
    FOLLOWED = 20
    MUTUAL_FOLLOW = 30
    OWNER = 40
    SAVED = 50
    LIKED = 50
    OWNER_LIKED = 90


def db_query(func):
    """Decorador para tratar erros de funções que mexem com o DB"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except QueryError as q:
            raise q
        
        except Exception as e:
            raise QueryError(500, f"{func.__name__}: {e}")
    
    return wrapper


def fix_date(date: datetime):
    """Padroniza datas que estão no DB para uma human readable string"""

    return date.strftime("%d/%m/%Y")


def is_isoformat(date_string: str):
    """Verifica se uma string pode ser convertida para um datetime"""

    try:
        datetime.fromisoformat(date_string)
        return True
    except (ValueError, TypeError):
        return False


def op_to_dir(op: str):
    """Converte um operador aritmético para um sentido em SQL"""

    return "ASC" if op == ">" else "DESC"


def col_name(table_alias: str, col: str):
    """Monta o nome de uma coluna específica em uma tabela"""

    if col[0] == "-":
        col = col[1:]

    return f"{table_alias}.{col}"


def escape_like(term: str) -> str:
    """Troca caracteres que podem ser nocivos para uma cláusula LIKE pelos seus correspondentes seguros"""

    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

