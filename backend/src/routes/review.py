from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from models.schemas.review import *
from services.security_services import is_review_insertion_valid, is_review_update_valid, classify_relationship, resolve_review_clearence  
from services.db_services.list import DB_create_list_game, DB_read_list_id, DB_delete_list_game
from services.db_services.user import DB_read_user_column
from services.db_services.review import *

from utils import *

review_router = APIRouter(prefix="/reviews", tags=["review"])


@review_router.post("")
async def create_review(review: ReviewNew, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Cria uma review para um jogo. Cada usuário pode ter apenas uma review por jogo"""

    validated_review = await is_review_insertion_valid(conn, review, user_id)
    review_id = await DB_create_review(conn, validated_review, user_id)

    # Se o usuário marcou que completou o game, ele é inserido na lista de games completados dele
    if review.completed:
        completed_games_list_id = await DB_read_list_id(conn, "Jogos Completados", user_id)
        await DB_create_list_game(conn, completed_games_list_id, review.game_id)

    # Se o usuário marcou que gostou do game, ele é inserido na lista de games favoritos dele
    if review.liked:
        favorite_games_list_id = await DB_read_list_id(conn, "Jogos Favoritos", user_id)
        await DB_create_list_game(conn, favorite_games_list_id, review.game_id)
    
    return JSONResponse({"message":"Review criada com sucesso!", "review_id": review_id})
    
                    
@review_router.put("/{review_id}")
async def update_review(review_id: str, review: ReviewEdit, conn = Depends(get_conn), user_id = Depends(require_login)):  
    """Atualiza a review do usuário autenticado para um jogo. O campo `game` não pode ser alterado"""

    reviewer_id = await DB_read_review_creator(conn, review_id)

    if reviewer_id is None:
        raise QueryError(404, REVIEW_NOT_FOUND_MSG)

    if user_id != reviewer_id:
        raise QueryError(403, LACK_OF_REVIEW_OWNERSHIP_MSG)

    validated_review_update = await is_review_update_valid(conn, review, review_id, user_id)

    old_review_liked, old_review_completed = await DB_read_liked_and_completed(conn, review_id)

    game_id = await DB_read_review_game(conn, review_id)

    if review.liked != old_review_liked:
        args = (conn, await DB_read_list_id(conn, "Jogos Favoritos", user_id), game_id)
        await DB_create_list_game(*args) if review.liked else await DB_delete_list_game(*args)

    if review.completed != old_review_completed:
        args = (conn, await DB_read_list_id(conn, "Jogos Completados", user_id), game_id)
        await DB_create_list_game(*args) if review.completed else await DB_delete_list_game(*args)
        
    await DB_update_review(conn, review_id, validated_review_update)
    updated_review = await DB_read_review(conn, review_id)
    updated_review.rel = RelationshipStatus.OWNER

    return JSONResponse(updated_review.model_dump())

                                                    
@review_router.delete("/{review_id}")
async def delete_review(review_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove a review do usuário autenticado para um jogo"""

    reviewer_id = await DB_read_review_creator(conn, review_id)

    if reviewer_id is None:
        raise QueryError(404, REVIEW_NOT_FOUND_MSG)

    if user_id != reviewer_id:
        raise QueryError(403, LACK_OF_REVIEW_OWNERSHIP_MSG)

    old_review_liked, old_review_completed = await DB_read_liked_and_completed(conn, review_id)
    review_game_id = await DB_read_review_game(conn, review_id)

    if old_review_liked:
        args = (conn, await DB_read_list_id(conn, "Jogos Favoritos", user_id), review_game_id)
        await DB_delete_list_game(*args)

    if old_review_completed:
        args = (conn, await DB_read_list_id(conn, "Jogos Completados", user_id), review_game_id)
        await DB_delete_list_game(*args)

    await DB_delete_review(conn, review_id)

    return JSONResponse({"message":"Review deletada com sucesso!"})


@review_router.get("/created/{user_id}")
async def get_reviews(user_id: str, page_query = Depends(validate_queries(["title", "created_at", "updated_at"], "!created_at")), 
    conn = Depends(get_conn), user_id_viewer = Depends(optional_login), path = Depends(get_current_url)):
    """Retorna uma página com as mais recente reviews públicas de um usuário"""

    if await DB_read_user_column(conn, "username", user_id=user_id) is None:
        raise QueryError(404, USER_NOT_FOUND_MSG)

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    prev_relationship = await classify_relationship(conn, user_id_viewer, user_id)
    resolve_review_clearence(prev_relationship, None)

    created_reviews_page = await DB_read_user_created_reviews(conn, user_id, prev_relationship, page_query)

    # Verifica qual o relacionamento do usuário que está vendo com cada review
    for cr in created_reviews_page.content:
        has_liked = await DB_read_review_like(conn, cr.review_id, user_id_viewer)
        cr.rel = RelationshipStatus.LIKED if has_liked > 0 else RelationshipStatus.ANY

        if cr.creator.user_id == user_id_viewer:
            cr.rel += RelationshipStatus.OWNER

    created_reviews_page_with_urls = convert_cursors_to_paths(created_reviews_page, path)

    return JSONResponse(created_reviews_page_with_urls.model_dump())
    

@review_router.get("/{review_id}")
async def get_one_review(review_id: str, conn = Depends(get_conn), user_id = Depends(optional_login)):
    """Retorna os detalhes completos da review pública de um usuário para um jogo específico"""

    review_creator_id = await DB_read_review_creator(conn, review_id)

    if review_creator_id is None:
        raise QueryError(404, REVIEW_NOT_FOUND_MSG)

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    prev_relationship = await classify_relationship(conn, user_id, review_creator_id)
    review_privacy = await DB_read_review_privacy(conn, review_id)
    resolve_review_clearence(prev_relationship, review_privacy)
    
    review = await DB_read_review(conn, review_id)

    if review is None:
        raise QueryError(404, REVIEW_NOT_FOUND_MSG)
    
    return JSONResponse(review.model_dump())


@review_router.post("/like/{review_id}")
async def like_review(review_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Dá like na review pública de outro usuário para um jogo"""

    review_creator_id = await DB_read_review_creator(conn, review_id)

    if review_creator_id is None:
       raise QueryError(404, REVIEW_NOT_FOUND_MSG)

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    prev_relationship = await classify_relationship(conn, user_id, review_creator_id)
    review_privacy = await DB_read_review_privacy(conn, review_id)
    resolve_review_clearence(prev_relationship, review_privacy)
    
    # Usuário já deu like na review (idempotência)
    if await DB_read_review_like(conn, review_id, user_id) > 0:
        return JSONResponse({"message": "Like adicionado com sucesso!"})
        
    await DB_create_like_review(conn, review_id, user_id)

    return JSONResponse({"message": "Like adicionado com sucesso!"})


@review_router.delete("/like/{review_id}")
async def unlike_review(review_id: str, conn = Depends(get_conn), user_id = Depends(require_login)):
    """Remove o like do usuário autenticado de uma review"""
    
    reviewer_id = await DB_read_review_creator(conn, review_id)

    if reviewer_id is None:
       raise QueryError(404, REVIEW_NOT_FOUND_MSG)
        
    await DB_delete_like_review(conn, review_id, user_id)

    return JSONResponse({"message": "Like removido com sucesso!"})


@review_router.get("/like/users/{review_id}")
async def get_review_likes(review_id: str, page_query = Depends(validate_queries(["username", "created_at"], "!created_at")),
    conn = Depends(get_conn), user_id = Depends(optional_login),  path = Depends(get_current_url)):
    """Retorna quem tem dado like na review"""

    review_creator_id = await DB_read_review_creator(conn, review_id)

    if review_creator_id is None:
        raise QueryError(404, REVIEW_NOT_FOUND_MSG)

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    prev_relationship = await classify_relationship(conn, user_id, review_creator_id)
    review_privacy = await DB_read_review_privacy(conn, review_id)
    resolve_review_clearence(prev_relationship, review_privacy)

    review_likes_page = await DB_read_review_likers(conn, review_id, page_query)
    review_likes_page_with_urls = convert_cursors_to_paths(review_likes_page, path)
    
    return JSONResponse(review_likes_page_with_urls.model_dump())


@review_router.get("/like/reviews")
async def get_review_likes(page_query = Depends(validate_queries(["title", "created_at", "updated_at"], "!created_at")),
    conn = Depends(get_conn), user_id = Depends(require_login),  path = Depends(get_current_url)):
    """Retorna as reviews para qual o usuário já deu like"""

    user_review_likes_page = await DB_read_user_likes(conn, user_id, page_query)
    user_review_likes_page_with_urls = convert_cursors_to_paths(user_review_likes_page, path)
    
    return JSONResponse(user_review_likes_page_with_urls.model_dump())