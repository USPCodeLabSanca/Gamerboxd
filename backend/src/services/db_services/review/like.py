from models.schemas.review import *
from utils import *


@db_query
async def DB_create_like_review(conn, review_id: str, user_id: str):
    """Insere um like de um usuário em uma review"""

    await conn.execute('''
        INSERT INTO ReviewLikes(usr, review)
        VALUES($1, $2)
    ''', user_id, review_id)
    
    
@db_query
async def DB_delete_like_review(conn, review_id: str, user_id: str):
    """Remove um like de um usuário em uma review"""

    await conn.execute('''
        DELETE FROM ReviewLikes 
        WHERE usr = $1 AND review = $2
    ''', user_id, review_id)
    

@db_query
async def DB_read_review_like(conn, review_id: str, user_id: str):
    """Lê se uma review recebeu like do usuário ou não"""

    review_like = await conn.fetchrow('''
        SELECT * FROM ReviewLikes WHERE usr = $1 AND review = $2 
    ''', user_id, review_id)

    return review_like
    
    
@db_query
async def DB_read_count_likes(conn, review_id: str):
    """Conta quantos likes uma review tem"""

    likes = await conn.fetchval('''
        SELECT COUNT(*) FROM ReviewLikes WHERE review = $1 
    ''', review_id)

    return likes


@db_query
async def DB_read_review_likers(conn, review_id: str, page_query: PageQuery):
    """Busca uma página de usuários que deram like numa review"""

    async with conn.transaction():

        clauses = PageClauses(
            basic_conditions=[("rl.review = $1", review_id)],
            table_alias="rl",
            col2="usr",
            search_col="u.username"
        )

        # Conta quantos usuários que curtiram a review correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_review_likes = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Users u
            JOIN ReviewLikes rl ON rl.usr = u.id
            WHERE {where}
        ''', *params)

        # Pega uma página de usuários que curtiram a review
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT u.id AS user_id, u.pfp, u.username,
            {cursor_cols}
            FROM Users u
            JOIN ReviewLikes rl ON rl.usr = u.id
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        review_likes = [User(
            user_id=r["user_id"],
            username=r["username"],
            pfp=r["pfp"]
        ) for r in rows]

        return PageResult(
            total=total_review_likes,
            page_size=len(rows),
            content=review_likes,
            current_page=page_query.cursor,
            next_page=encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )

    
@db_query
async def DB_read_user_likes(conn, user_id: str, page_query: PageQuery):
    """Busca uma página de reviews curtidas por um usuário"""

    async with conn.transaction():

        clauses = PageClauses(
            basic_conditions=[("rl.usr = $1", user_id)],
            table_alias="rl",
            col2="review",
            search_col="g.title"
        )

        # Conta quantas reviews curtidas pelo usuário correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_user_likes = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Reviews r
            JOIN ReviewLikes rl ON rl.review = r.id
            JOIN Games g ON g.id = r.game
            WHERE {where}
        ''', *params)

        # Pega uma página de reviews curtidas
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT r.*, u.id AS user_id, u.pfp, u.username, g.id AS game_id, g.name, g.picture, g.year,
            {cursor_cols}
            (SELECT COUNT(*) FROM ReviewLikes rl WHERE rl.usr  = r.reviewer) AS likes_count
            FROM Reviews r
            RIGHT JOIN Games g ON g.id = r.game
            RIGHT JOIN Users u ON u.id = r.reviewer
            RIGHT JOIN ReviewLikes rl ON rl.review = r.id
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        reviews_liked = [ReviewOutOverview(
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
            total=total_user_likes,
            page_size=len(rows),
            content=reviews_liked,
            current_page=page_query.cursor,
            next_page=encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )
