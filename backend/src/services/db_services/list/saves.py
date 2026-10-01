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

        basic_condition = ("sl.usr = $1", user_id)
        page_query_clauses =  PageQuery(
            cursor="(sl.created_at, sl.list)",
            search="l.name"
        )

        # Conta quantas listas salvas pelo usuário correspondem a busca
        where, params = build_where(basic_condition, page_query_clauses, page_query, None, True)
        total_saves = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM SavedLists sl
            JOIN Lists l ON l.id = sl.list
            WHERE {where}
        ''', *params)

        # Pega uma página de listas salvas
        where, params = build_where(basic_condition, page_query_clauses, page_query, "<")
        rows = await conn.fetch(f'''
            SELECT l.id AS list_id, l.name, u.id AS user_id, u.username, u.pfp, sl.created_at AS saved_at,
            (SELECT COUNT(*) FROM SavedLists s  WHERE s.list  = l.id) AS saves
            FROM SavedLists sl
            JOIN Lists l ON l.id = sl.list
            JOIN Users u ON u.id = l.creator
            WHERE {where}
            ORDER BY sl.created_at DESC, sl.list DESC
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        saved_lists = [ListOutOverview(
            name=r["name"],
            list_id=r["list_id"],
            creator=User(user_id=r["user_id"], username=r["username"], pfp=r["pfp"]),
            list_saves_count=r["saves"],
        ) for r in rows]

        page_result = PageResult(
            total=total_saves,
            page_size=len(rows),
            content=saved_lists
        )

        page_result.next_page = encode_tuple_to_cursor(rows[-1]["saved_at"], rows[-1]["list_id"]) if has_more else None

        # Se o cursor é None, estamos na busca pela primeira página, então com certeza não existe página anterior
        if page_query.cursor is None:
            return page_result

        # Acha o cursor para a página de listas salvas anterior
        where, params = build_where(basic_condition, page_query_clauses, page_query, ">=")
        rows = await conn.fetch(f'''
            SELECT sl.list AS id, sl.created_at
            FROM SavedLists sl
            JOIN Lists l ON l.id = sl.list
            WHERE {where}
            ORDER BY sl.created_at ASC, sl.list ASC
            LIMIT ${len(params)}
            ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        page_result.current_page = page_query.cursor
        page_result.previous_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None

        return page_result


@db_query
async def DB_read_list_savers(conn, list_id: str, page_query: PageQuery):
    async with conn.transaction():

        basic_condition = ("sl.list = $1", list_id)
        page_query_clauses =  PageQuery(
            cursor="(sl.created_at, sl.usr)",
            search="sl.usr"
        )

        # Conta quantas usuários que salvaram a lista correspondem a busca
        where, params = build_where(basic_condition, page_query_clauses, page_query, None, True)
        total_savers = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM SavedLists sl
            WHERE {where}
        ''', *params)

        # Pega uma página de usuários que salvaram a lista
        where, params = build_where(basic_condition, page_query_clauses, page_query, "<")
        rows = await conn.fetch(f'''
            SELECT u.id AS user_id, u.username, u.pfp, sl.created_at,
            FROM SavedLists sl
            LEFT JOIN Users u ON u.id = sl.usr
            WHERE {where}
            ORDER BY sl.created_at DESC, sl.usr DESC
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        list_savers = [User(
            user_id=r["user_id"],
            username=r["username"],
            pfp=r["pfp"]
        ) for r in rows]

        page_result = PageResult(
            total=total_savers,
            page_size=len(rows),
            content=list_savers
        )

        # Monta o cursor para a próxima página de usuários que salvaram a lista
        page_result.next_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["user_id"]) if has_more else None

        # Se o cursor é None, estamos na busca pela primeira página, então com certeza não existe página anterior
        if page_query.cursor is None:
            return page_result

        # Acha o cursor para a página de usuários que salvaram a lista anterior
        where, params = build_where(*basic_condition, page_query_clauses, page_query, ">=")
        rows = await conn.fetch(f'''
                SELECT sl.usr AS user_id, sl.created_at
                FROM SavedLists sl
                LEFT JOIN Users u ON u.id = sl.usr
                WHERE {where}
                ORDER BY sl.created_at ASC, sl.usr ASC
                LIMIT ${len(params)}
            ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        page_result.current_page = page_query.cursor
        page_result.previous_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["user_id"]) if has_more else None

        return page_result