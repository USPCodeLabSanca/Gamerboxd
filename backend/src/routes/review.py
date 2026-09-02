from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.review import *
from services.security_services import is_review_insertion_valid, is_review_update_valid, is_blocked
from services.db_services.review import *
from services.db_services.user import DB_read_user_column
from utils.dependencies import get_conn, require_login, optional_login
from utils.utils import QueryError

review_router = APIRouter(prefix="/review", tags=["review"])


@review_router.post("/")
async def create_review(review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Cria uma review para um jogo. Cada usuário pode ter apenas uma review por jogo"""

    validated_review = await is_review_insertion_valid(conn, review, user_id)
    await DB_create_review(conn, validated_review, user_id)
    
    return JSONResponse({"message":"Review criada com sucesso!"})
    
                        
@review_router.put("/{old_review_game}")
async def update_review(old_review_game: int, new_review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):  
    """Atualiza a review do usuário autenticado para um jogo. O campo `game` não pode ser alterado"""

    validated_review_update = await is_review_update_valid(conn, new_review, old_review_game, user_id)
    updated_review = await DB_update_review(conn, validated_review_update, old_review_game, user_id)

    return JSONResponse(updated_review.model_dump())

                                                    
@review_router.delete("/{review_game}")
async def delete_review(review_game: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove a review do usuário autenticado para um jogo"""

    await DB_delete_review(conn, review_game, user_id)
    return JSONResponse({"message":"Review deletada com sucesso!"})


@review_router.post("/like/{username}/{game}")
async def like_review(username: str, game: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Dá like na review pública de outro usuário para um jogo"""

    review_creator_id = await DB_read_user_column(conn, "id", username=username)

    if review_creator_id is None:
       raise QueryError(404, "Usuário não encontrado!")

    if await is_blocked(conn, review_creator_id, user_id):
        raise QueryError(403, "Usuário está tentando dar like em uma review escrita por alguém que o bloqueou!")

    review_id = await DB_read_review_id(conn, username, game)

    if review_id is None:
        raise QueryError(404, "Review não encontrada!")

    like_validated = await DB_read_review_like(conn, review_id, user_id)

    if like_validated is not None:
        raise QueryError(409, "Você já deu like nessa review!")
        
    await DB_create_like_review(conn, ReviewLike(user_id, review_id))

    return JSONResponse({"message": "Like adicionado com sucesso!"})


@review_router.delete("/like/{username}/{game}")
async def unlike_review(username: str, game: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove o like do usuário autenticado de uma review"""
    
    review_id = await DB_read_review_id(conn, username, game)

    if review_id is None:
        raise QueryError(404, "Review não encontrada!")

    like = await DB_read_review_like(conn, review_id, user_id)

    if like is None:
        raise QueryError(409, "Você não deu like nessa review!")
        
    await DB_delete_like_review(conn, ReviewLike(user_id, review_id))

    return JSONResponse({"message": "Like removido com sucesso!"})


@review_router.get("/{username}")
async def get_all_reviews(username: str, limit: int = 10, conn = Depends(get_conn), user_id = Depends(optional_login)):
    """Retorna uma lista das reviews públicas mais recentes de um usuário"""

    if user_id is not None:
        review_creator_id = await DB_read_user_column(conn, "id", username=username)

        if review_creator_id is None:
            raise QueryError(404, "Usuário não encontrado!")

        if await is_blocked(conn, review_creator_id, user_id):
            raise QueryError(403, "Usuário está tentando dar like em uma review escrita por alguém que o bloqueou!")

    if limit > 20:
        raise QueryError(400, "Não podem ser apresentadas mais de 20 reviews!")
    
    reviews = await DB_read_limit_reviews(conn, username, limit)

    return JSONResponse([review.model_dump() for review in reviews])
    

@review_router.get("/{username}/{game}")
async def get_one_review(username: str, game: int, conn = Depends(get_conn), user_id = Depends(optional_login)):
    """Retorna os detalhes completos da review pública de um usuário para um jogo específico"""

    if user_id is not None:
        review_creator_id = await DB_read_user_column(conn, "id", username=username)

        if review_creator_id is None:
            raise QueryError(404, "Usuário não encontrado!")

        if await is_blocked(conn, review_creator_id, user_id):
            raise QueryError(403, "Usuário está tentando dar like em uma review escrita por alguém que o bloqueou!")

    review = await DB_read_review(conn, username, game)

    if review is None:
        raise QueryError(404, "Review não encontrada!")
    
    return JSONResponse(review.model_dump())
