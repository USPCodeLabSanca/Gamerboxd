from fastapi import Request, Depends
from .pagination import PageQuery
from .errors import *

async def get_conn(request: Request):
    """Empresta uma conexão com a vm da pool"""

    pool = request.app.state.internal_pool
    async with pool.acquire() as conn:
        yield conn


async def get_exconn(request: Request):
    """Empresta uma conexão externa da pool"""

    yield request.app.state.external_pool


def require_login(request: Request):
    """Garante que o usuário está logado e retorna o user_id dele"""

    login = request.state.user_login
    if not login["logged_in"]:
        raise QueryError(401, "É necessário fazer login para esta ação!")
    return login["user_id"]


def optional_login(request: Request):
    """Retorna o user_id do usuário caso ele esteja logado ou None se não tiver"""

    login = request.state.user_login
    return login["user_id"]


def get_key(request: Request):
    """Retorna a chave para codificar/decodificar jwts"""

    return request.app.state.jwt_key


def get_rawg(request: Request):
    """Retorna a url já com a chave rawg para o acesso da API de jogos"""
    
    return request.app.state.rawg_key 


def get_current_url(request: Request):
    """Retorna a url do atual request"""

    return str(request.url)


def validate_queries(order_bys: list[str], standard_order_by: str, limit: int = 50):
    """Verifica se os query parameters são válidos para aquela rota"""

    def dependency(page_query: PageQuery = Depends()):
        all_orders= ["-" + ob for ob in order_bys] + order_bys

        if page_query.order is None:
            page_query.order = standard_order_by

        if page_query.order not in order_bys:
            raise QueryError(406, f"Método de ordenação inválido! Nessa rota, são aceitos apenas as ordens: {all_orders}")

        if page_query.page_size < 1 or page_query.page_size > limit:
            raise QueryError(406, f"O tamanho da página tem que estar entre 1 e {limit}!")

        return page_query

    return dependency

        

