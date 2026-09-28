from fastapi import Request
from .utils import QueryError
from models.schemas.pagination import PageResult

async def get_conn(request: Request):
    """Empresta uma conexão com a vm da pool"""

    pool = request.app.state.internal_pool
    async with pool.acquire() as conn:
        yield conn


async def get_exconn(request: Request):
    """Empresta uma conexão externa da pool"""

    yield request.app.state.external_pool


def require_login(request: Request) -> str:
    """Garante que o usuário está logado e retorna o user_id dele"""

    login = request.state.user_login
    if not login["logged_in"]:
        raise QueryError(401, "É necessário fazer login para esta ação")
    return login["user_id"]


def optional_login(request: Request) -> str | None:
    """Retorna o user_id do usuário caso ele esteja logado ou None se não tiver"""

    login = request.state.user_login
    return login["user_id"]


def get_key(request: Request) -> str:
    """Retorna a chave para codificar/decodificar jwts"""

    return request.app.state.jwt_key


def get_rawg(request: Request) -> str:
    """Retorna a url já com a chave rawg para o acesso da API de jogos"""
    
    return request.app.state.rawg_key 


def current_page(request: Request) -> PageResult:
    """Cria uma página de resultado"""

    request_path = request.url.path
    page_result = PageResult(current=request_path, content=[])

    # Primeira busca
    if "cursor=" not in request_path:
        page_result.previous = None

    return page_result

