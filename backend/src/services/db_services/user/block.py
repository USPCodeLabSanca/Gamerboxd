from models.schemas.user import *
from utils import *


@db_query
async def DB_create_block(conn, user_id_blocker: str, user_id_blocked:str):
    """Insere um bloqueio no DB"""

    await conn.execute('''
        INSERT INTO Blocks(blocker, blocked)
        VALUES($1, $2)
    ''', user_id_blocker, user_id_blocked)


@db_query
async def DB_delete_block(conn, user_id_blocker: str, user_id_blocked:str):
    """Remove um bloqueio do DB"""

    await conn.execute('''
        DELETE FROM Blocks
        WHERE blocker = $1 AND blocked = $2
    ''', user_id_blocker, user_id_blocked)


@db_query
async def DB_read_user_blockeds(conn, user_id: str, page_query: PageQuery):
    """Lê uma página de bloqueados pelo usuário"""

    async with conn.transaction():

        basic_condition = ("b.blocker = $1", user_id)
        page_query_clauses =  PageQuery(
            cursor="(b.created_at, b.blocked)",
            search="u.username"
        )

        # Conta quantos bloqueados pelo usuário correspondem a busca
        where, params = build_where(basic_condition, page_query_clauses, page_query, None, True)
        total_blockeds = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Blocks b
            JOIN Users u ON u.id = b.blocker
            WHERE {where}
        ''', *params)

        # Pega uma página de bloqueados pelo usuário
        where, params = build_where(basic_condition, page_query_clauses, page_query, "<")
        rows = await conn.fetch(f'''
            SELECT u.id, u.username, u.pfp, b.created_at
            FROM Blocks b
            JOIN Users u ON u.id = b.blocked
            WHERE {where}
            ORDER BY b.created_at DESC, b.blocked DESC
            LIMIT ${len(params)}
        ''', *params)
    
        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])
    
        blocks = [User(user_id=r["id"], username=r["username"], pfp=r["pfp"]) for r in rows]

        page_result = PageResult(
            total=total_blockeds,
            page_size=len(rows),
            content=blocks
        )

        # Monta o cursor para a próxima página de bloqueados pelo usuário
        page_result.next_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None

        # Se o cursor é None, estamos na busca pela primeira página, então com certeza não existe página anterior
        if page_query.cursor is None:
            return page_result

        # Acha o cursor para a página de bloqueados pelo usuário anterior
        where, params = build_where(basic_condition, page_query_clauses, page_query, ">=")
        rows = await conn.fetch(f'''
                SELECT b.blocked AS id, b.created_at
                FROM Blocks b
                WHERE {where}
                ORDER BY b.created_at ASC, b.blocked ASC
                LIMIT ${len(params)}
            ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        page_result.current_page = page_query.cursor
        page_result.previous_page = encode_tuple_to_cursor(rows[-1]["created_at"], rows[-1]["id"]) if has_more else None

        return page_result


@db_query
async def is_blocked(conn, user_id_blocker: str, user_id_blocked: str):
    """Lê se um usuário bloqueia o outro"""

    blocked = await conn.fetchval(f'''
        SELECT COUNT(*)
        FROM Blocks b
        WHERE b.blocker = $1 AND b.blocked = $2
    ''', user_id_blocker, user_id_blocked)

    return False if blocked == 0 else True
