from models.schemas.user import *
from utils import *


@db_query
async def DB_create_follow(conn, user_id_follower: str, user_id_followed: str):
    """Insere uma relação de seguidor do DB"""

    await conn.execute('''
        INSERT INTO Follows(follower, followed)
        VALUES($1, $2)
    ''', user_id_follower, user_id_followed)


@db_query    
async def DB_delete_follow(conn, user_id_follower: str, user_id_followed: str):
    """Remove uma relação de seguidor do DB"""

    await conn.execute('''
        DELETE FROM Follows
        WHERE follower = $1 AND followed = $2 
    ''', user_id_follower, user_id_followed)


async def _DB_read_user_follow_page(conn, user_id: str, page_query: PageQuery, owner_col: str, other_col: str):
    """Lê uma página de seguidores/seguidos do usuário"""

    async with conn.transaction():

        clauses = PageClauses(
            basic_conditions = [(f"f.{other_col} = $1", user_id)],
            table_alias="f",
            col2=owner_col,
            search_col="u.username"
        )

        # Conta quantos seguidores/seguidos correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_followers = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Follows f
            JOIN Users u ON u.id = f.{owner_col}
            WHERE {where}
        ''', *params)

        # Pega uma página de seguidores/seguidos
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT u.id, u.username, u.pfp,
            {cursor_cols}
            FROM Follows f
            JOIN Users u ON u.id = f.{owner_col}
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)
    
        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])
    
        followers = [User(user_id=r["id"], username=r["username"], pfp=r["pfp"]) for r in rows]

        return PageResult(
            total=total_followers,
            page_len=len(rows),
            content=followers,
            current_url=page_query.cursor,
            next_url=encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )

        
@db_query
async def DB_read_user_followings(conn, user_id: str, page_query: PageQuery):
    """Lê uma página de seguidos pelo usuário. Filtra por follower, mostra followed"""

    return await _DB_read_user_follow_page(conn, user_id, page_query, "followed", "follower")
    

@db_query
async def DB_read_user_followers(conn, user_id: str, page_query: PageQuery):
    """Lê uma página de seguidores do usuário"""

    return await _DB_read_user_follow_page(conn, user_id, page_query, "follower", "followed")


@db_query
async def DB_read_user_follows(conn, user_id: str):
    """Conta quantas pessoas o usuário segue e quantos seguidores ele tem"""

    async with conn.transaction():

        total_followers = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Follows f
            WHERE f.follower = $1
        ''', user_id)

        total_followeds = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Follows f
            WHERE f.followed = $1
        ''', user_id)

    return total_followers, total_followeds


@db_query
async def DB_read_already_follows(conn, user_id_follower: str, user_id_followed: str):
    """Retorna se um usuário segue o outro"""

    return await conn.fetchval(f'''
        SELECT COUNT(*)
        FROM Follows f
        WHERE f.follower = $1 AND f.followed = $2
    ''', user_id_follower, user_id_followed)
