from datetime import datetime
from uuid import uuid4

from models.schemas.review import *
from utils import *
from .like import DB_read_count_likes
from ..game import DB_read_game_name
from ..user import DB_read_user_column


@db_query
async def DB_create_review(conn, review: ReviewIn, user_id: str):   
    """Insere uma review no DB"""

    review_id = str(uuid4())

    await conn.execute('''
        INSERT INTO Reviews(id, reviewer, game, rating_num, rating_text, is_private, time_played, liked, completed)
        VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9) 
    ''', review_id, user_id, review.game, review.rating_num, review.rating_text, review.is_private,
    review.time_played, review.liked, review.completed)

    return review


@db_query
async def DB_delete_review(conn, review_game: int, user_id: str):
    """Deleta uma review do DB"""

    await conn.execute('''
        DELETE FROM Reviews 
        WHERE game = $1 AND reviewer = $2
    ''', review_game, user_id)


@db_query
async def DB_read_user_game_review(conn, game: int, user_id: str):
    return await conn.fetchrow('''
        SELECT * FROM Reviews WHERE game = $1 AND reviewer = $2
    ''', game, user_id)


@db_query
async def DB_read_review(conn, username: str, game: int):
    """Lê os dados completos de uma review"""

    review = await conn.fetchrow('''
        SELECT r.*
        FROM Reviews r
        JOIN Users u ON u.id = r.reviewer
        WHERE u.username = $1
        AND r.game = $2
    ''', username, game)

    if review is None:
        return None
    
    rows = await conn.fetch('''
        SELECT t.name
        FROM ReviewTags rt
        JOIN Tags t ON t.id = rt.tag
        WHERE rt.review = $1
    ''', review["id"])
    
    likes = await DB_read_count_likes(conn, review["id"])
    game_name = await DB_read_game_name(conn, review["game"])

    if game_name is None:
        return None
        
    tags = [r["tag_name"] for r in rows]

    review_found = ReviewOutOne(
        username = username,
        rating_num = review["rating_num"],
        rating_text = review["rating_text"],
        time_played = review["time_played"],
        is_private = review["is_private"],
        completed = review["completed"],
        tag_count = len(tags),
        tags = tags,
        likes_count = likes,
        liked = review["liked"],
        game_name = game_name,
        created_at = fix_date(review["created_at"]),
        updated_at = fix_date(review["updated_at"])
    )
    
    return review_found

@db_query
async def DB_read_review_privacy(conn, username: str, game: int):
    review_is_private = await conn.fetchval('''
        SELECT r.is_private
        FROM Reviews r
        JOIN Users u on u.id = r.reviewer
        WHERE u.username = $1
        AND r.game = $2
    ''', username, game)

    return review_is_private

@db_query
async def DB_read_review_id(conn, username: str, game: int):
    review_id = await conn.fetchval('''
        SELECT r.id
        FROM Reviews r
        JOIN Users u ON u.id = r.reviewer
        WHERE u.username = $1
        AND r.game = $2
    ''', username, game)

    return review_id


@db_query
async def DB_read_limit_reviews(conn, username: str, limit: int):
    reviews = await conn.fetch('''
        SELECT r.* FROM Reviews r 
        JOIN Users u On u.id = r.reviewer 
        WHERE u.username = $1 AND r.is_private = false 
        LIMIT $2
    ''', username, limit)

    reviews_out = []
    for r in reviews:

        game_name = await DB_read_game_name(conn, r["game"])

        if game_name is None:
            # POR WARNING AQ
            continue
        
        likes = await DB_read_count_likes(conn, r["review_id"])

        reviews_out.append(
            ReviewOut(
                rating_num = r["rating_num"],
                rating_text = r["rating_text"],
                likes_count = likes,
                liked = r["liked"],
                is_private = r["is_private"],
                game_name = game_name,
                created_at = fix_date(r["created_at"])
            )
        )
    
    return reviews_out


@db_query
async def DB_update_review(conn, review: ReviewIn, old_review_game: int, user_id: str):    
    time_now = datetime.now()

    await conn.execute('''
        UPDATE Reviews
        SET game = $1, rating_num = $2, rating_text = $3,
        is_private = $4, time_played = $5, liked = $6, completed = $7, updated_at = $8 
        WHERE game = $9 AND reviewer = $10
    ''', review.game, review.rating_num, review.rating_text, review.is_private, review.time_played, 
    review.liked, review.completed, time_now, old_review_game, user_id)
