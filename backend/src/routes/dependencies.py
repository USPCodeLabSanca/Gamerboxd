from fastapi import Request, Depends
from ..utils import pagination as pag
from ..utils import errors as err
from ..services.db_services.user import DB_read_user_column
from ..services.db_services.game import DB_read_game_name
from ..services.db_services.list import DB_read_list_creator
from ..services.db_services.review import DB_read_review_creator


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
        raise err.QueryError(401, "É necessário fazer login para esta ação!")
    return login["user_id"]


def optional_login(request: Request):
    """Retorna o user_id do usuário caso ele esteja logado ou None se não tiver"""

    return request.state.user_login["user_id"]


async def user_id_exists(user_id: str, conn = Depends(get_conn)):
    """Verifica que o usuário existe no DB"""

    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise err.QueryError(404, err.USER_NOT_FOUND_MSG)

    return user_id


async def game_id_exists(game_id: int, conn = Depends(get_conn)):
    """Verifica que um game existe no DB"""

    if await DB_read_game_name(conn, game_id) is None:
        raise err.QueryError(404, err.GAME_NOT_FOUND_MSG)

    return game_id


async def list_is_owned_by_auth(list_id: str, user_id: str = Depends(require_login), conn = Depends(get_conn)):
    """Verifica que a lista existe, e a rota está sendo chamada pelo dono da lista"""

    list_creator_id = await DB_read_list_creator(conn, list_id)

    if list_creator_id is None:
        raise err.QueryError(404, err.LIST_NOT_FOUND_MSG)

    if list_creator_id != user_id:
        raise err.QueryError(403, err.LACK_OF_LIST_OWNERSHIP_MSG)

    return list_id


async def review_is_owned_by_auth(review_id: str, user_id: str = Depends(require_login), conn = Depends(get_conn)):
    """Verifica que a review existe, e a rota está sendo chamada pelo dono da review"""

    reviewer_id = await DB_read_review_creator(conn, review_id)
    
    if reviewer_id is None:
        raise err.QueryError(404, err.REVIEW_NOT_FOUND_MSG)

    if user_id != reviewer_id:
        raise err.QueryError(403, err.LACK_OF_REVIEW_OWNERSHIP_MSG)

    return review_id


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

    def dependency(page_query: pag.PageQuery = Depends()):
        all_orders= ["!" + ob for ob in order_bys] + order_bys

        if page_query.order is None:
            page_query.order = standard_order_by

        if page_query.order not in all_orders:
            raise err.QueryError(422, "Método de ordenação inválido!")

        if (page_query.page_size < 1) or (page_query.page_size > limit):
            raise err.QueryError(422, f"O tamanho da página tem que estar entre 1 e {limit}!")

        return page_query

    return dependency

        

