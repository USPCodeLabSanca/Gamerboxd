from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse

from ..models.schemas.review import ReviewNew, ReviewEdit
from ..services.security_services import is_review_insertion_valid, is_review_update_valid, resolve_review_clearence  
from ..services.db_services.list import DB_create_list_game, DB_read_list_id, DB_delete_list_game
from ..services.db_services.review import *
from ..utils import pagination as pag
from ..utils import errors as err
from ..utils.utils import RelationshipStatus
from . import dependencies as dep

review_router = APIRouter(prefix="/reviews", tags=["review"])


@review_router.post("")
async def create_review(review: ReviewNew, conn = Depends(dep.get_conn), user_id = Depends(dep.require_login)):
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
async def update_review(review: ReviewEdit, review_id: str = Depends(dep.review_is_owned_by_auth), 
        conn = Depends(dep.get_conn), user_id = Depends(dep.require_login)):  
    """Atualiza a review do usuário autenticado para um jogo"""

    validated_review_update = await is_review_update_valid(conn, review, review_id, user_id)

    current_review_privacy = await DB_read_review_privacy(conn, review_id)
    new_privacy = validated_review_update.privacy

    if new_privacy > current_review_privacy:
        await DB_delete_likes_after_privacy(conn, review_id, user_id, new_privacy)

    old_review_liked, old_review_completed = await DB_read_liked_and_completed(conn, review_id)
    game_id = await DB_read_review_game(conn, review_id) if (old_review_liked or old_review_completed) else None

    if review.liked != old_review_liked:
        args = (conn, await DB_read_list_id(conn, "Jogos Favoritos", user_id), game_id)
        await DB_create_list_game(*args) if review.liked else await DB_delete_list_game(*args)

    if review.completed != old_review_completed:
        args = (conn, await DB_read_list_id(conn, "Jogos Completados", user_id), game_id)
        await DB_create_list_game(*args) if review.completed else await DB_delete_list_game(*args)

    current_review_privacy = await DB_read_review_privacy(conn, review_id)
    new_privacy = validated_review_update.privacy

    if new_privacy > current_review_privacy:
        await DB_delete_likes_after_privacy_change(conn, review_id, user_id, new_privacy)
        
    await DB_update_review(conn, review_id, validated_review_update)
    updated_review = await DB_read_review(conn, review_id)
    updated_review.rel = RelationshipStatus.OWNER

    return JSONResponse(updated_review.model_dump())

                                                    
@review_router.delete("/{review_id}")
async def delete_review(review_id: str = Depends(dep.review_is_owned_by_auth), 
        conn = Depends(dep.get_conn), user_id = Depends(dep.require_login)):
    """Remove a review do usuário autenticado para um jogo"""

    old_review_liked, old_review_completed = await DB_read_liked_and_completed(conn, review_id)
    review_game_id = await DB_read_review_game(conn, review_id)

    if old_review_liked:
        fav_list_id = await DB_read_list_id(conn, "Jogos Favoritos", user_id)
        await DB_delete_list_game(conn, fav_list_id, review_game_id)

    if old_review_completed:
        comp_list_id = await DB_read_list_id(conn, "Jogos Completados", user_id)
        await DB_delete_list_game(conn, comp_list_id, review_game_id)

    await DB_delete_review(conn, review_id)

    return JSONResponse({"message":"Review deletada com sucesso!"})


@review_router.get("/created/{user_id}")
async def get_reviews(user_id: str = Depends(dep.user_id_exists), page_query = Depends(dep.validate_queries(["title", "created_at", "updated_at"], "created_at")), 
    conn = Depends(dep.get_conn), user_id_viewer = Depends(dep.optional_login), path = Depends(dep.get_current_url)):
    """Retorna uma página com as mais recente reviews de um usuário"""

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    prev_relationship = await resolve_review_clearence(conn, None,  user_id_viewer, user_id)
    created_reviews_page = await DB_read_user_created_reviews(conn, user_id, prev_relationship, page_query)

    # Verifica qual o relacionamento do usuário que está vendo com cada review
    for cr in created_reviews_page.content:
        has_liked = await DB_read_review_like(conn, cr.review_id, user_id_viewer)
        cr.rel = RelationshipStatus.LIKED if has_liked > 0 else RelationshipStatus.ANY

        if cr.creator.user_id == user_id_viewer:
            cr.rel += RelationshipStatus.OWNER

    created_reviews_page_with_urls = pag.convert_cursors_to_paths(created_reviews_page, path)

    return JSONResponse(created_reviews_page_with_urls.model_dump())
    

@review_router.get("/{review_id}")
async def get_one_review(review_id: str, conn = Depends(dep.get_conn), user_id = Depends(dep.optional_login)):
    """Retorna os detalhes completos da review pública de um usuário para um jogo específico"""

    review_creator_id = await DB_read_review_creator(conn, review_id)

    if review_creator_id is None:
        raise err.QueryError(404, err.REVIEW_NOT_FOUND_MSG)

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    await resolve_review_clearence(conn, review_id,  user_id, review_creator_id)
    
    review = await DB_read_review(conn, review_id)
    
    return JSONResponse(review.model_dump())


@review_router.post("/like/{review_id}")
async def like_review(review_id: str, conn = Depends(dep.get_conn), user_id = Depends(dep.require_login)):
    """Dá like na review pública de outro usuário para um jogo"""

    review_creator_id = await DB_read_review_creator(conn, review_id)

    if review_creator_id is None:
       raise err.QueryError(404, err.REVIEW_NOT_FOUND_MSG)

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    await resolve_review_clearence(conn, review_id,  user_id, review_creator_id)
    
    # Usuário já deu like na review (idempotência)
    if await DB_read_review_like(conn, review_id, user_id) > 0:
        return JSONResponse({"message": "Like adicionado com sucesso!"})
    
    await DB_create_like_review(conn, review_id, user_id)

    return JSONResponse({"message": "Like adicionado com sucesso!"})


@review_router.delete("/like/{review_id}")
async def unlike_review(review_id: str, conn = Depends(dep.get_conn), user_id = Depends(dep.require_login)):
    """Remove o like do usuário autenticado de uma review"""
    
    reviewer_id = await DB_read_review_creator(conn, review_id)

    if reviewer_id is None:
       raise err.QueryError(404, err.REVIEW_NOT_FOUND_MSG)
        
    await DB_delete_like_review(conn, review_id, user_id)

    return JSONResponse({"message": "Like removido com sucesso!"})


@review_router.get("/like/users/{review_id}")
async def get_review_likes(review_id: str, page_query = Depends(dep.validate_queries(["username", "created_at"], "created_at")),
    conn = Depends(dep.get_conn), user_id = Depends(dep.optional_login), path = Depends(dep.get_current_url)):
    """Retorna quem tem dado like na review"""

    review_creator_id = await DB_read_review_creator(conn, review_id)

    if review_creator_id is None:
        raise err.QueryError(404, err.REVIEW_NOT_FOUND_MSG)

    # Verifica qual a relação do usuário visualizador com o usuário criador das reviews
    await resolve_review_clearence(conn, review_id,  user_id, review_creator_id)

    review_likes_page = await DB_read_review_likers(conn, review_id, page_query)
    review_likes_page_with_urls = pag.convert_cursors_to_paths(review_likes_page, path)
    
    return JSONResponse(review_likes_page_with_urls.model_dump())


@review_router.get("/like/reviews")
async def get_review_likes(page_query = Depends(dep.validate_queries(["title", "created_at", "updated_at"], "created_at")),
    conn = Depends(dep.get_conn), user_id = Depends(dep.require_login),  path = Depends(dep.get_current_url)):
    """Retorna as reviews para qual o usuário já deu like"""

    user_review_likes_page = await DB_read_user_likes(conn, user_id, page_query)
    user_review_likes_page_with_urls = pag.convert_cursors_to_paths(user_review_likes_page, path)
    
    return JSONResponse(user_review_likes_page_with_urls.model_dump())