from .data import DB_update_list_updated_at
from models.schemas.list import *
from utils import *


@db_query
async def DB_create_list_save(conn, list_id: str, user_id: str):
    """Salva uma lista na "biblioteca" do usuário"""

    await conn.execute('''
        INSERT INTO SavedLists(usr, list) VALUES($1, $2)
    ''', user_id, list_id)


@db_query
async def DB_delete_list_save(conn, list_id: str, user_id: str):
    """Remove uma lista na "biblioteca" do usuário"""

    await conn.execute('''
        DELETE FROM SavedLists WHERE list = $1 AND usr = $2
    ''', list_id, user_id)


@db_query
async def DB_read_user_has_saved_list(conn, list_id: str, user_id: str):
    """Verifica se um usário salvou uma lista"""

    has_saved = await conn.execute('''
        SELECT COUNT(*) FROM SavedLists WHERE list = $1 AND usr = $2
    ''')

    return True if has_saved > 0 else False


@db_query
async def DB_delete_list_saves_after_privacy_change(conn, list_id: str, user_id: str):
    """Remove a lista da "biblioteca" de todos os usuários que tinham salvado ela, menos o criador"""

    await conn.execute('''
        DELETE FROM SavedLists WHERE list = $1 AND usr != $2
    ''', list_id, user_id)

    await DB_update_list_updated_at(conn, list_id)


@db_query
async def DB_read_user_saved_lists(conn, user_id: str, page_query: PageQuery):
    """Busca uma página de listas salvas por um usuário"""

    async with conn.transaction():

        clauses = PageClauses(
            basic_conditions=[("sl.usr = $1", user_id)],
            table_alias="sl",
            col2= "list",
            search_col="l.name"
        )

        # Conta quantas listas salvas pelo usuário correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_saves = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM SavedLists sl
            JOIN Lists l ON l.id = sl.list
            WHERE {where}
        ''', *params)

        # Pega uma página de listas salvas
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT l.id AS list_id, l.name, u.id AS user_id, u.username, u.pfp,
            (SELECT COUNT(*) FROM SavedLists sl WHERE sl.list  = l.id) AS saves,
            (SELECT g.picture FROM Games g 
            LEFT JOIN ListContent lc ON lc.game = g.id 
            WHERE lc.list = l.id ORDER BY lc.created_at ASC 
            LIMIT 1) AS cover,
            {cursor_cols}
            FROM SavedLists sl
            JOIN Lists l ON l.id = sl.list
            JOIN Users u ON u.id = l.creator
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        saved_lists = [ListOutOverview(
            name=r["name"],
            list_id=r["list_id"],
            creator=User(user_id=r["user_id"], username=r["username"], pfp=r["pfp"]),
            saves_count=r["saves"],
            cover_picture=r["cover"],
            rel = RelationshipStatus.OWNER
        ) for r in rows]

        return PageResult(
            total=total_saves,
            page_len=len(rows),
            content=saved_lists,
            current_url=page_query.cursor,
            next_url=encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )
