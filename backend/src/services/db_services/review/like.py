from models.schemas.review import *
from utils import *


@db_query
async def DB_create_like_review(conn, user, review):
    await conn.execute('''
        INSERT INTO ReviewLikes(usr, review)
        VALUES($1, $2)
    ''', user, review)
    
    
@db_query
async def DB_delete_like_review(conn, like: ReviewLike):
    await conn.execute('''
        DELETE FROM ReviewLikes 
        WHERE usr = $1 AND review = $2
    ''', like.user, like.review)
    

@db_query
async def DB_read_review_like(conn, review_id: str, user_id: str):
    review_like = await conn.fetchrow('''
        SELECT * FROM ReviewLikes WHERE usr = $1 AND review = $2 
    ''', user_id, review_id)

    return review_like
    
    
@db_query
async def DB_read_count_likes(conn, review_id: str):
    likes = await conn.fetchval('''
        SELECT COUNT(*) FROM ReviewLikes WHERE review = $1 
    ''', review_id)

    return likes
