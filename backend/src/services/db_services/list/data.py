from uuid import uuid4

from models.schemas.list import *
from utils import *


@db_query
async def DB_create_list(conn, new_list: ListNew, user_id: str):
    """Adiciona uma lista nova ao BD"""

    list_id = str(uuid4())

    await conn.execute('''
        INSERT INTO Lists(id, name, description, creator, privacy)
        VALUES($1, $2, $3, $4, $5)
    ''', list_id, new_list.name, new_list.description, user_id, new_list.privacy)

    return list_id


@db_query
async def DB_delete_list(conn, list_id: str):
    """Deleta uma lista do BD"""

    await conn.execute('''
        DELETE FROM Lists WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_creator(conn, list_id: str):
    """Lê o id do usuário que criou uma lista"""

    return await conn.fetchval('''
        SELECT creator FROM Lists WHERE id = $1
    ''', list_id) 


@db_query
async def DB_read_list_privacy(conn, list_id: str):
    """Lê a privacidade de uma lista a partir do list.id"""

    return await conn.fetchval('''
        SELECT privacy FROM Lists WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_name(conn, list_id: str):
    """Lê o nome de uma lista a partir do list_id"""

    return await conn.fetchval('''
        SELECT name FROM Lists WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_desc(conn, list_id: str):
    """Retorna a descrição de uma lista do DB"""

    return await conn.fetchval('''
        SELECT description FROM Lists WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_id(conn, list_name: str, user_id: str):
    """Retorna se o usuário já tem uma lista com esse nome, se sim, retorna o id dela, caso não, retorna None"""

    return await conn.fetchval('''
        SELECT id FROM Lists WHERE name = $1 AND creator = $2 
    ''', list_name, user_id)


@db_query
async def DB_read_user_basic_lists(conn, user_id: str):
    """Lê dados das listas básicas de um usuário"""
    basic_lists_names = ("Jogos Favoritos", "Jogos Completados")

    basic_lists = []

    for bl in basic_lists_names:
        list_id = await DB_read_list_id(conn, bl, user_id)

        games = await conn.fetch('''
            SELECT g.id AS game_id, g.title, g.picture, g.year
            FROM Games g
            JOIN ListContent lc ON lc.game = g.id
            JOIN Lists l ON lc.list = l.id
            WHERE l.creator = $1 AND l.name = $2
            ORDER BY lc.created_at DESC
            LIMIT 4
        ''', user_id, bl)

        games_schema = [
            GameOverview(
                game_id=g["game_id"],
                title=g["title"],
                picture=g["picture"],
                year=g["year"]
            ) for g in games
        ]

        list_games = ListGames(list_id=list_id, name=bl, games_len=len(games_schema), games=games_schema)

        basic_lists.append(list_games)

    return basic_lists


@db_query
async def DB_update_list(conn, list_id: str, new_list: List):
    """Atualiza os dados de uma lista"""
    
    await conn.execute('''
        UPDATE Lists 
        SET name = $1, description = $2, privacy = $3, updated_at = NOW()
        WHERE id = $4
    ''', new_list.name, new_list.description, new_list.privacy, list_id)


@db_query
async def DB_update_list_updated_at(conn, list_id: str):
    """Atualiza a data de última modificação de uma lista"""
    
    await conn.execute('''
        UPDATE Lists
        SET updated_at = NOW()
        WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_data(conn, list_id: str):
    """Lê os dados completos de uma lista"""

    row = await conn.fetchrow('''
        SELECT l.name, l.description, l.privacy, l.created_at, l.updated_at,
            u.id AS creator_id, u.username, u.pfp,
            (SELECT COUNT(*) FROM SavedLists sl WHERE sl.list = l.id) AS saves,
            (SELECT COUNT(*) FROM ListContent lc WHERE lc.list = l.id) AS games,
            (SELECT g.picture FROM Games g 
            LEFT JOIN ListContent lc ON lc.game = g.id 
            WHERE lc.list = l.id ORDER BY lc.created_at ASC 
            LIMIT 1) AS cover
        FROM Lists l
        JOIN Users u ON u.id = l.creator
        WHERE l.id = $1
    ''', list_id)

    if row is None:
        return None

    user_list = ListOutComplete(
        name=row["name"],
        list_id=list_id,
        description=row["description"],
        creator=User(user_id=row["creator_id"], username=row["username"], pfp=row["pfp"]),
        privacy=row["privacy"],
        saves_count=row["saves"],
        games_count=row["games"],
        cover_picture=row["cover"],
        created_at=fix_date(row["created_at"]),
        updated_at=fix_date(row["updated_at"])
    )

    return user_list


@db_query
async def DB_read_user_created_lists(conn, user_id: str, clearence: int, page_query: PageQuery):
    """Busca uma página de listas criadas por um usuário"""

    async with conn.transaction():

        clauses = PageClauses(
            basic_conditions=[("l.creator = $1", user_id), ("l.privacy <= $2", clearence)],
            table_alias="l",
            col2="id",
            search_col="l.name"
        )

        # Conta quantas listas criadas pelo usuário correspondem a busca
        where, order_by, cursor_cols, params = build_where(clauses, page_query, True)
        total_created_lists = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Lists l
            JOIN Users u ON u.id = l.creator
            WHERE {where}
        ''', *params)

        # Pega uma página de listas criadas
        where, order_by, cursor_cols, params = build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT l.id AS list_id, l.name, u.id AS user_id, u.username, u.pfp,
            (SELECT COUNT(*) FROM SavedLists sl WHERE sl.list = l.id) AS saves,
            (SELECT g.picture FROM Games g 
            LEFT JOIN ListContent lc ON lc.game = g.id 
            WHERE lc.list = l.id ORDER BY lc.created_at ASC 
            LIMIT 1) AS cover,
            {cursor_cols}
            FROM Lists l
            RIGHT JOIN Users u ON u.id = l.creator
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        created_lists = [ListOutOverview(
            name=r["name"],
            list_id=r["list_id"],
            creator=User(user_id=r["user_id"], username=r["username"], pfp=r["pfp"]),
            saves_count=r["saves"],
            cover_picture=r["cover"]
        ) for r in rows]

        return PageResult(
            total=total_created_lists,
            page_len=len(rows),
            content=created_lists,
            current_url=page_query.cursor,
            next_url=encode_tuple_to_cursor(rows[-1]["main_col"], rows[-1]["other_col"]) if has_more else None
        )

