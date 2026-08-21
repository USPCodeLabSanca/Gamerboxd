from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.review import *
from services.security_services import is_review_insertion_valid, is_review_update_valid
from services.db_services.review import *
from utils.dependencies import get_conn, require_login
from utils.utils import QueryError

review_router = APIRouter(prefix="/review", tags=["review"])


@review_router.post("/")
async def create_review(review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):
    validated_review = await is_review_insertion_valid(conn, review, user_id)
    await DB_create_review(conn, validated_review, user_id)
    
    return JSONResponse({"message":"Review criada com sucesso!"})
    
                        
@review_router.put("/{old_review_game}")
async def update_review(old_review_game: int, new_review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):  
    validated_review_update = await is_review_update_valid(conn, new_review, old_review_game, user_id)
    updated_review = await DB_update_review(conn, validated_review_update, old_review_game, user_id)

    return JSONResponse(updated_review.model_dump())

                                                    
@review_router.delete("/{review_game}")
async def delete_review(review_game: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    await DB_delete_review(conn, review_game, user_id)
    
    return JSONResponse({"message":"Review deletada com sucesso!"})


@review_router.post("/like/{username}/{game}")
async def like_review(username: str, game: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    review_id = await DB_read_review_id(conn, username, game)

    if review_id is None:
        raise QueryError(404, "Review não encontrada!")

    like_validated = await DB_read_review_like(conn, review_id, user_id)

    if like_validated is not None:
        raise QueryError(400, "Você já deu like nessa review!")
        
    await DB_create_like_review(conn, ReviewLike(user_a = user_id, review = review_id))

    return JSONResponse({"message": "Like dado com sucesso!"})


@review_router.post("/unlike/{username}/{game}")
async def unlike_review(username: str, game: int, conn = Depends(get_conn), user_id = Depends(require_login)):
    review_id = await DB_read_review_id(conn, username, game)

    if review_id is None:
        raise QueryError(404, "Review não encontrada!")

    like_validated = await DB_read_review_like(conn, review_id, user_id)

    if like_validated is None:
        raise QueryError(400, "Você não deu like nessa review!")
        
    await DB_delete_like_review(conn, ReviewLike(user_a = user_id, review = review_id))

    return JSONResponse({"message": "Like removido com sucesso!"}, 200)


@review_router.get("/{username}")
async def get_all_reviews(username: str, limit: int = 10, conn = Depends(get_conn)):

    if limit > 20:
        raise QueryError(400, "Não podem ser apresentadas mais de 20 reviews!")
    
    reviews = await DB_read_limit_reviews(conn, username, limit)

    return JSONResponse([review.model_dump() for review in reviews], 200)
    

@review_router.get("/{username}/{game}")
async def get_one_review(username: str, game: int, conn = Depends(get_conn)):
    review = await DB_read_review(conn, username, game)

    if review is None:
        raise QueryError(404, "Review não encontrada!")
    
    return JSONResponse(review.model_dump(), 200)
