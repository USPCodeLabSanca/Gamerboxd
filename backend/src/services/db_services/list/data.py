from uuid import uuid4

from models.schemas.list import *
from utils import *


@db_query
async def DB_create_list(conn, new_list: ListIn, user_id: str):
    """Adiciona uma lista nova ao BD"""

    list_id = str(uuid4())

    await conn.execute('''
        INSERT INTO Lists(id, name, description, creator, is_private)
        VALUES($1, $2, $3, $4, $5)
    ''', list_id, new_list.name, new_list.description, user_id, new_list.is_private)

    return list_id


@db_query
async def DB_delete_list(conn, list_id: str):
    """Deleta uma lista do BD"""

    await conn.execute('''
        DELETE FROM Lists WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_creator(conn, list_id: str) -> str:
    """Lê o id do usuário que criou uma lista"""

    return await conn.fetchval('''
        SELECT creator FROM Lists WHERE id = $1
    ''', list_id) 


@db_query
async def DB_read_list_privacy(conn, list_id: str) -> bool:
    """Lê a privacidade de uma lista a partir do list.id"""

    return await conn.fetchval('''
        SELECT is_private FROM Lists WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_name(conn, list_id: str) -> str:
    """Lê o nome de uma lista a partir do list_id"""

    return await conn.fetchval('''
        SELECT name FROM Lists WHERE id = $1
    ''', list_id)


@db_query
async def DB_read_list_name_taken(conn, list_name: str, user_id: str) -> str | None:
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
        list_id = await DB_read_list_name_taken(conn, bl, user_id)

        games = await conn.fetch('''
            SELECT g.id AS game_id, g.name, g.picture, g.year
            FROM Games g
            JOIN ListContent lc ON lc.game = g.id
            JOIN Lists l ON lc.list = l.id
            WHERE l.creator = $1 AND l.name = $2
            ORDER BY lc.created_at DESC
            LIMIT 4
        ''', user_id, bl)

        games_schema = [
            GameRawg(
                game_id=g["game_id"],
                name=g["name"],
                picture=g["picture"],
                year=g["year"]
            ) for g in games
        ]

        list_games = ListGames(list_id=list_id, name=bl, games_count=len(games_schema), games=games_schema)

        basic_lists.append(list_games)

    return basic_lists


@db_query
async def DB_update_list(conn, list_id: str, new_list: ListIn):
    """Atualiza os dados de uma lista"""
    
    await conn.execute('''
        UPDATE Lists 
        SET name = $1, description = $2, is_private = $3, updated_at = NOW()
        WHERE id = $4
    ''', new_list.name, new_list.description, new_list.is_private, list_id)


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
        SELECT
            l.name, l.description, l.is_private, l.created_at,
            u.id AS creator_id, u.username, u.pfp,
            (SELECT COUNT(*) FROM SavedLists sl WHERE sl.list = l.id) AS saves,
            (SELECT COUNT(*) FROM ListContent lc WHERE lc.list = l.id) AS games
        FROM Lists l
        JOIN Users u ON u.id = l.creator
        WHERE l.id = $1
    ''', list_id)

    if row is None:
        return None

    user = User(user_id=row["creator_id"], username=row["username"], pfp=row["pfp"])

    user_list = ListOutComplete(
        name=row["name"],
        list_id=list_id,
        description=row["description"],
        creator=user,
        is_private=row["is_private"],
        created_at=fix_date(row["created_at"]),
        list_saves_count=row["saves"],
        list_games_count=row["games"]
    )

    return user_list


@db_query
async def DB_read_user_created_lists(conn, user_id: str, page_query: PageQuery):
    """Busca uma página de listas criadas por um usuário"""

    async with conn.transaction():

        basic_condition = ("l.creator = $1", user_id)
        page_query_clauses =  PageQuery(
            cursor="(l.updated_at, l.id)",
            search="l.name"
        )

        # Conta quantas listas criadas pelo usuário correspondem a busca
        where, params = build_where(basic_condition, page_query_clauses, page_query, None, True)
        total_created_lists = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Lists l
            JOIN Users u ON u.id = l.creator
            WHERE {where}
        ''', *params)

        # Pega uma página de listas criadas
        where, params = build_where(basic_condition, page_query_clauses, page_query, "<")
        rows = await conn.fetch(f'''
            SELECT l.id AS list_id, l.name, u.id AS user_id, u.username, u.pfp, l.updated_at,
            (SELECT COUNT(*) FROM SavedLists sl  WHERE sl.list  = l.id) AS saves
            FROM Lists l
            RIGHT JOIN Users u ON u.id = l.creator
            WHERE {where}
            ORDER BY l.updated_at DESC, l.id DESC
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])

        created_lists = [ListOutOverview(
            name=r["name"],
            list_id=r["list_id"],
            creator=User(user_id=r["user_id"], username=r["username"], pfp=r["pfp"]),
            list_saves_count=r["saves"],
        ) for r in rows]

        page_result = PageResult(
            total=total_created_lists,
            page_size=len(rows),
            content=created_lists
        )

        # Monta o cursor para a próxima página de listas criadas
        page_result.next_page = encode_tuple_to_cursor(rows[-1]["updated_at"], rows[-1]["list_id"]) if has_more else None

        # Se o cursor é None, estamos na busca pela primeira página, então com certeza não existe página anterior
        if page_query.cursor is None:
            return page_result

        # Acha o cursor para a página de listas criadas anterior)
        where, params = build_where(basic_condition, page_query_clauses, page_query, ">=")
        rows = await conn.fetch(f'''
            SELECT l.id AS list_id, l.updated_at
            FROM Lists l
            JOIN Users u ON u.id = l.creator
            WHERE {where}
            ORDER BY l.updated_at ASC, l.id ASC
            LIMIT ${len(params)}
        ''', *params)

        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])
        
        page_result.current_page = page_query.cursor
        page_result.previous_page = encode_tuple_to_cursor(rows[-1]["updated_at"], rows[-1]["list_id"]) if has_more else None

        return page_result

