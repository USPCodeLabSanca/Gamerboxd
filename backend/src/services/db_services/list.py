from uuid import uuid4

from models.schemas.list import *
from utils.utils import db_query
from utils.helper import fix_date


@db_query
async def DB_create_list(conn, new_list: List):
    """Adiciona uma lista nova ao BD"""

    list_id = str(uuid4())
    await conn.execute('''
        INSERT INTO Lists(id, name, description, creator, is_private)
        VALUES($1, $2, $3, $4, $5)
    ''', list_id, new_list.name, new_list.description, new_list.creator, new_list.is_private)

    return list_id


@db_query
async def DB_create_list_save(conn, list_id: str, user_id: str):
    """Salva uma lista na "biblioteca" do usuário"""

    await conn.execute('''
        INSERT INTO SavedLists(usr, list) VALUES($1, $2)
    ''', user_id, list_id)


@db_query
async def DB_create_list_game(conn, list_id, game_id):
    """Inclui um game em uma lista"""

    await conn.execute('''
        INSERT INTO ListContent(list, game) VALUES($1, $2)
    ''', list_id, game_id)


@db_query
async def DB_delete_list(conn, list_name: str, user_id: str):
    """Deleta uma lista do BD"""

    await conn.execute('''
        DELETE FROM Lists WHERE name = $1 AND creator = $2
    ''', list_name, user_id)
    

@db_query
async def DB_delete_list_save(conn, list_id: str, user_id: str):
    """Remove uma lista na "biblioteca" do usuário"""

    await conn.execute('''
        DELETE FROM SavedLists WHERE list = $1 AND usr = $2
    ''', list_id, user_id)


@db_query
async def DB_delete_list_game(conn, list_id: str, game_id: int):
    """Remove um game de uma lista"""

    await conn.execute('''
        DELETE FROM ListContent WHERE list = $1 AND game = $2
    ''', list_id, game_id)


@db_query
async def DB_read_user_list_id(conn, user_id: str, list_name: str, only_public: bool):
    """Lê o id de uma lista a partir do nome e do criador"""

    if only_public:
        query = "SELECT list_id FROM Lists WHERE creator = $1 AND name = $2 AND is_private = false"

    else:
        query = "SELECT list_id FROM Lists WHERE creator = $1 AND name = $2"

    list_id = await conn.fetchval(query, user_id, list_name)

    return list_id


@db_query
async def DB_read_user_saved_lists(conn, user_id: str):
    """Lê as listas salvas por um usuário"""

    rows = await conn.fetch(
        '''
        SELECT l.name, l.description, u.username AS creator, l.is_private, l.created_at,
        COUNT(sl2.usr) AS saves
        FROM SavedLists sl
        JOIN Lists l ON l.id = sl.list
        JOIN Users u ON u.id = l.creator
        LEFT JOIN SavedLists sl2 ON sl2.list = sl.list
        WHERE sl.usr = $1
        GROUP BY l.name, l.description, u.username, l.is_private, l.created_at
        ORDER BY l.created_at DESC
    ''', user_id)

    lists = [
        ListOut(
            name=r["name"],
            description=r["description"],
            creator=r["creator"],
            is_private=r["is_private"],
            created_at=fix_date(r["created_at"]),
            list_saves=r["saves"],
        )
        for r in rows
    ]

    user_lists = UserLists(count=len(lists), lists=lists)

    return user_lists


@db_query
async def DB_read_user_lists(conn, user_id: str):
    """Lê as listas criadas por um usuário"""

    rows = await conn.fetch('''
        SELECT l.name, l.description, u.username AS creator, l.is_private, l.created_at,
        COUNT(sl.usr) AS saves
        FROM Lists l
        JOIN Users u ON u.id = l.creator
        LEFT JOIN SavedLists sl ON sl.list = l.id
        WHERE l.creator = $1
        GROUP BY l.name, l.description, u.username, l.is_private, l.created_at
        ORDER BY l.created_at DESC
    ''', user_id)

    lists = [
        ListOut(
            name=r["name"],
            description=r["description"],
            creator=r["creator"],
            is_private=r["is_private"],
            created_at=fix_date(r["created_at"]),
            list_saves=r["saves"],
        )
        for r in rows
    ]

    user_lists = UserLists(count=len(lists), lists=lists)

    return user_lists
    

@db_query
async def DB_read_list_full(conn, list_id: str):
    """Lê os dados completos de uma lista"""

    full_row = await conn.fetchrow('''
        SELECT l.name, l.description, u.username AS creator, l.is_private, l.created_at,
        COUNT(sl.usr) AS saves
        FROM Lists l
        JOIN Users u ON u.id = l.creator
        LEFT JOIN SavedLists sl ON sl.list = l.id
        WHERE l.id = $1
        GROUP BY l.name, l.description, u.username, l.is_private, l.created_at
    ''', list_id)

    games = await conn.fetch('''
        SELECT g.id, g.name, g.picture, g.year,
                COUNT(r.liked) FILTER (WHERE r.liked = true) AS like_count,
                COALESCE(ROUND(AVG(r.rating_num) FILTER (WHERE r.is_private = false)::numeric, 2), -1) AS gamerboxd_rating
        FROM Games g
        LEFT JOIN ListContent lc ON lc.game = g.id
        LEFT JOIN Reviews r ON r.game = g.id
        WHERE lc.list = $1
        GROUP BY g.id, g.name, g.picture, g.year
    ''', list_id)

    games_list = []

    for g in games:
        game = Game(
            game_id=g["game_id"],
            name=g["game_name"],
            picture=g["game_picture"],
            year=g["game_year"],
            like_count=g["like_count"],
            gamerboxd_rating=float(g["gamerboxd_rating"])
        )
        games_list.append(game)

    user_list = ListFull(
        name=full_row["list_name"],
        description=full_row["list_description"],
        creator=full_row["list_creator"],
        is_private=full_row["is_private"],
        created_at=fix_date(full_row["created_at"]),
        list_saves=full_row["list_saves"],
        games=games_list
    )

    return user_list


@db_query
async def DB_update_list(conn, new_list: ListIn, old_list_name: str, user_id: str):
    """Atualiza os dados de uma lista e a retorna completa e atualizada"""
    
    list_id = await conn.fetchval('''
        UPDATE Lists 
        SET name = $1, description = $2, is_private = $3 
        WHERE name = $4 AND creator = $5 
        RETURNING id
    ''', new_list.name, new_list.description, new_list.is_private, old_list_name, user_id)

    full_row = await conn.fetchrow('''
        SELECT l.name, l.description, u.username AS creator,
                l.is_private, l.created_at, COUNT(sl.usr) AS saves
        FROM Lists l
        JOIN Users u ON u.id = l.creator
        LEFT JOIN SavedLists sl ON sl.list = l.id
        WHERE l.id = $1
        GROUP BY l.name, l.description, u.username, l.is_private, l.created_at
    ''', list_id)

    games = await conn.fetch('''
        SELECT g.id, g.name, g.picture, g.year,
        COUNT(r.liked) FILTER (WHERE r.liked = true) AS like_count,
        COALESCE(ROUND(AVG(r.rating_num) FILTER (WHERE r.is_private = false)::numeric, 2), -1) AS gamerboxd_rating
        FROM Games g
        JOIN ListContent lc ON lc.game = g.id
        LEFT JOIN Reviews r ON r.game = g.id
        WHERE lc.list = $1
        GROUP BY g.id, g.name, g.picture, g.year
    ''', list_id)

    games_list = []

    for g in games:
        game = Game(
            game_id=g["id"],
            name=g["name"],
            picture=g["picture"],
            year=g["year"],
            like_count=g["like_count"],
            gamerboxd_rating=float(g["gamerboxd_rating"])
        )
        games_list.append(game)

    updated_list = ListFull(
        name=full_row["name"],
        description=full_row["description"],
        creator=full_row["creator"],
        is_private=full_row["is_private"],
        created_at=fix_date(full_row["created_at"]),
        list_saves=full_row["saves"],
        games=games_list
    )
    return updated_list

