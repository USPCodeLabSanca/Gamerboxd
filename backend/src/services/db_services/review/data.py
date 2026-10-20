from datetime import datetime
from uuid import uuid4

from models.schemas.review import *
from utils import *
from .like import DB_read_count_likes
from ..game import DB_read_game_basic
from ..user import DB_read_user_column


@db_query
async def DB_create_review(conn, review: ReviewIn, user_id: str):   
    """Insere uma review no DB"""

    review_id = str(uuid4())

    await conn.execute('''
        INSERT INTO Reviews(id, reviewer, game, rating_num, rating_text, privacy, time_played, liked, completed)
        VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9) 
    ''', review_id, user_id, review.game_id, review.rating_num, review.rating_text, review.privacy,
    review.time_played, review.liked, review.completed)

    return review_id


@db_query
async def DB_delete_review(conn, review_id: str):
    """Deleta uma review do DB"""

    await conn.execute('''
        DELETE FROM Reviews 
        WHERE id = $1
    ''', review_id)


@db_query
async def DB_read_review_game(conn, review_id: str):
    """Lê o id do game de uma review"""

    return await conn.fetchval('''
        SELECT game FROM Reviews WHERE id = $1
    ''', review_id)


@db_query
async def DB_read_review_creator(conn, review_id: str):
    """Lê o id do autor de uma review"""

    return await conn.fetchval('''
        SELECT reviewer FROM Reviews WHERE id = $1
    ''', review_id)


@db_query
async def DB_read_liked_and_completed(conn, review_id: str):
    """Retorna se o game está marcado como liked e completed"""

    row = await conn.fetchrow('''
        SELECT liked, completed FROM Reviews WHERE id = $1
    ''', review_id)

    return row["liked"], row["completed"]


@db_query
async def DB_read_review(conn, review_id: str):
    """Lê os dados completos de uma review"""

    review = await conn.fetchrow('''
        SELECT r.*, u.username, u.pfp,
        (SELECT COUNT(*) FROM ReviewLikes rl  WHERE rl.usr  = r.reviewer) AS likes_count
        FROM Reviews r
        JOIN Users u ON u.id = r.reviewer
        WHERE r.id = $1
    ''', review_id)
    
    rows = await conn.fetch('''
        SELECT t.name
        FROM ReviewTags rt
        JOIN Tags t ON t.id = rt.tag
        WHERE rt.review = $1
    ''', review_id)
    
    game_info = await DB_read_game_basic(conn, review["game"])

    if game_info is None:
        return None
        
    tags = [r["tag_name"] for r in rows]

    review_found = ReviewOutComplete(
        review_id = review["id"],
        reviewer = User(user_id=review["reviewer"], username=review["username"], pfp=review["pfp"] ),
        game = game_info,
        rating_num = review["rating_num"],
        rating_text = review["rating_text"],
        time_played = review["time_played"],
        privacy = review["privacy"],
        completed = review["completed"],
        tag_count = len(tags),
        tags = tags,
        likes_count = review["likes_count"],
        liked = review["liked"],
        created_at = fix_date(review["created_at"]),
        updated_at = fix_date(review["updated_at"])
    )
    
    return review_found


@db_query
async def DB_read_review_privacy(conn, review_id: str):
    """Lê a privacidade de uma review"""

    return await conn.fetchval('''
        SELECT privacy FROM Reviews WHERE id = $1
    ''', review_id)


@db_query
async def DB_read_review_id(conn, user_id: str, game_id: int):
    """Lê o id de uma review a partir do id do game e do criador da review"""
    
    return await conn.fetchval('''
        SELECT id
        FROM Reviews r
        WHERE reviewer = $1 AND game = $2
    ''', user_id, game_id)


@db_query
async def DB_read_user_created_reviews(conn, user_id: str, clearence: int, page_query: PageQuery):
    """Busca uma página de reviews criadas por um usuário"""

    async with conn.transaction():
        
        clauses =  PageClauses(
            basic_conditions=[("r.reviewer = $1", user_id), ("r.privacy <= $2", clearence)],
            table_alias="r",
            col2="id",
            search_col="g.title"
        )

        # Conta quantas reviews criadas pelo usuário correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_created_reviews = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Reviews r
            JOIN Games g ON g.id = r.game
            WHERE {where}
        ''', *params)

        # Pega uma página de reviews criadas
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT r.*, u.id AS user_id, u.pfp, u.username, g.id AS game_id, g.name, g.picture, g.year,
            (SELECT COUNT(*) FROM ReviewLikes rl  WHERE rl.usr  = r.reviewer) AS likes_count,
            {cursor_cols}
            FROM Reviews r
            JOIN Users u ON u.id = r.reviewer
            JOIN Games g ON g.id = r.game
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        created_reviews = [ReviewOutOverview(
            review_id = r["id"],  
            reviewer = User(user_id=r["user_id"], username=r["username"], pfp=r["pfp"]), 
            rating_num = r["rating_num"],
            rating_text = r["rating_text"],
            liked = r["liked"],                     
            privacy = r["privacy"],
            likes_count = r["likes_count"],
            game = GameOverview(game_id=r["game_id"], title=r["title"], picture=r["picture"], year=r["year"]),
            created_at = r["created_at"]
        ) for r in rows]

        return PageResult(
            total=total_created_reviews,
            page_size=len(rows),
            content=created_reviews,
            current_page=page_query.cursor,
            next_page = encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )


@db_query
async def DB_update_review(conn, review_id: str, review: ReviewIn):
    """Atualiza uma review no DB a partir do seu id"""    
    
    time_now = datetime.now()

    await conn.execute('''
        UPDATE Reviews
        SET game = $1, rating_num = $2, rating_text = $3,
        privacy = $4, time_played = $5, liked = $6, completed = $7, updated_at = $8 
        WHERE id = $9
    ''', review.game_id, review.rating_num, review.rating_text, review.privacy, review.time_played, 
    review.liked, review.completed, time_now, review_id)
