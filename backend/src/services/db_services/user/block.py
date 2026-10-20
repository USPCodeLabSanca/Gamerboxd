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

        clauses = PageClauses(
            basic_conditions=[("b.blocker = $1", user_id)],
            table_alias="b",
            col2="blocked",
            search_col="u.username"
        )

        # Conta quantos bloqueados pelo usuário correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_blockeds = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Blocks b
            JOIN Users u ON u.id = b.blocked
            WHERE {where}
        ''', *params)

        # Pega uma página de bloqueados pelo usuário
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT u.id, u.username, u.pfp,
            {cursor_cols}
            FROM Blocks b
            JOIN Users u ON u.id = b.blocked
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)
    
        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])
    
        blocks = [User(user_id=r["id"], username=r["username"], pfp=r["pfp"]) for r in rows]

        return PageResult(
            total=total_blockeds,
            page_size=len(rows),
            content=blocks,
            current_page=page_query.cursor,
            next_page=encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )


@db_query
async def DB_read_is_blocked(conn, user_id_blocker: str, user_id_blocked: str):
    """Lê se um usuário bloqueia o outro"""

    return await conn.fetchval(f'''
        SELECT COUNT(*)
        FROM Blocks b
        WHERE b.blocker = $1 AND b.blocked = $2
    ''', user_id_blocker, user_id_blocked)
