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

        basic_condition = (f"f.{other_col} = $1", user_id)
        page_query_clauses = PageQuery(
            cursor=f"(f.created_at, f.{owner_col})",
            search="u.username"
        )

        # Conta quantos seguidores/seguidos correspondem a busca
        where, params = build_where(basic_condition, page_query_clauses, page_query, None, True)
        total_followers = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Follows f
            JOIN Users u ON u.id = f.{owner_col}
            WHERE {where}
        ''', *params)

        # Pega uma página de seguidores/seguidos
        where, params = build_where(basic_condition, page_query_clauses, page_query, "<")
        rows = await conn.fetch(f'''
            SELECT u.id, u.username, u.pfp, f.created_at
            FROM Follows f
            JOIN Users u ON u.id = f.{owner_col}
            WHERE {where}
            ORDER BY f.created_at DESC, f.{owner_col} DESC
            LIMIT ${len(params)}
        ''', *params)
    
        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])
    
        followers = [User(user_id=r["id"], username=r["username"], pfp=r["pfp"]) for r in rows]

        page_result = PageResult(
            total=total_followers,
            page_size=len(rows),
            content=followers
        )

        # Monta o cursor para a próxima página de seguidores/seguidos
        page_result.next_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None

        # Se o cursor é None, estamos na busca pela primeira página, então com certeza não existe página anterior
        if page_query.cursor is None:
            return page_result

        # Acha o cursor para a página de seguidores/seguidos anterior
        where, params = build_where(basic_condition, page_query_clauses, page_query, ">=")
        rows = await conn.fetch(f'''
            SELECT f.{owner_col} AS id, f.created_at
            FROM Follows f
            WHERE {where}
            ORDER BY f.created_at ASC, f.{owner_col} ASC
            LIMIT ${len(params)}
            ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        page_result.current_page = page_query.cursor
        page_result.previous_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None

        return page_result
        

@db_query
async def DB_read_user_followeds(conn, user_id: str, page_query: PageQuery):
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

        return UserFollows(follower_count=total_followers, following_count=total_followeds)