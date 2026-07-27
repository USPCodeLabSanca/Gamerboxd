from uuid import uuid4

from models.schemas.list import *
from utils.utils import db_query
from utils.helper import fix_date


@db_query
async def DB_create_list(conn, new_list: List):      
    list_id = str(uuid4())
    await conn.execute('''
        INSERT INTO Lists(list_id, list_name, list_description, list_creator, is_private)
        VALUES($1, $2, $3, $4, $5)
    ''', list_id, new_list.name, new_list.description, new_list.creator, new_list.is_private)

    return list_id


@db_query
async def DB_create_list_save(conn, list_id: str, user_id: str):
    await conn.execute('''
        INSERT INTO SavedLists(user_a, list) VALUES($1, $2)
    ''', user_id, list_id)


@db_query
async def DB_create_list_game(conn, list_id, game_id):
    await conn.execute('''
        INSERT INTO ListContent(list, game) VALUES($1, $2)
    ''', list_id, game_id)


@db_query
async def DB_delete_list(conn, list_name: str, user_id: str):
    await conn.execute('''
        DELETE FROM Lists WHERE list_name = $1 AND list_creator = $2
    ''', list_name, user_id)
    

@db_query
async def DB_delete_list_save(conn, list_id: str, user_id: str):
    await conn.execute('''
        DELETE FROM SavedLists WHERE list = $1 AND user_a = $2
    ''', list_id, user_id)


@db_query
async def DB_delete_list_game(conn, list_id: str, game_id: int):
    await conn.execute('''
        DELETE FROM ListContent WHERE list = $1 AND game = $2
    ''', list_id, game_id)


@db_query
async def DB_read_user_list_id(conn, user_id: str, list_name: str, only_public: bool):
    if only_public:
        query = "SELECT list_id FROM Lists WHERE list_creator = $1 AND list_name = $2 AND is_private = false"

    else:
        query = "SELECT list_id FROM Lists WHERE list_creator = $1 AND list_name = $2"

    list_id = await conn.fetchval(query, user_id, list_name)

    return list_id


@db_query
async def DB_read_user_lists(conn, user_id: str):
    rows = await conn.fetch(
        """
        SELECT l.list_name, l.list_description, u.username AS list_creator, l.is_private, l.created_at,
        COUNT(sl2.user_a) AS list_saves
        FROM SavedLists sl
        JOIN Lists l ON l.list_id = sl.list
        JOIN Users u ON u.user_id = l.list_creator
        LEFT JOIN SavedLists sl2 ON sl2.list = sl.list
        WHERE sl.user_a = $1
        GROUP BY l.list_name, l.list_description, u.username, l.is_private, l.created_at
        """,
        user_id,
    )

    lists = [
        ListOut(
            name=r["list_name"],
            description=r["list_description"],
            creator=r["list_creator"],
            is_private=r["is_private"],
            created_at=fix_date(r["created_at"]),
            list_saves=r["list_saves"],
        )
        for r in rows
    ]

    user_lists = UserLists(list_count=len(lists), lists=lists)

    return user_lists
    

@db_query
async def DB_read_list_full(conn, list_id: str):
    full_row = await conn.fetchrow('''
        SELECT l.list_name, l.list_description, u.username AS list_creator,
                l.is_private, l.created_at, COUNT(sl.user_a) AS list_saves
        FROM Lists l
        JOIN Users u ON u.user_id = l.list_creator
        LEFT JOIN SavedLists sl ON sl.list = l.list_id
        WHERE l.list_id = $1
        GROUP BY l.list_name, l.list_description, u.username, l.is_private, l.created_at
    ''', list_id)

    games = await conn.fetch('''
        SELECT g.game_id, g.game_name, g.game_picture, g.game_year,
                COUNT(r.liked) FILTER (WHERE r.liked = true) AS like_count,
                COALESCE(ROUND(AVG(r.rating_num) FILTER (WHERE r.is_private = false)::numeric, 2), -1) AS gamerboxd_rating
        FROM Games g
        LEFT JOIN ListContent lc ON lc.game = g.game_id
        LEFT JOIN Reviews r ON r.game = g.game_id
        WHERE lc.list = $1
        GROUP BY g.game_id, g.game_name, g.game_picture, g.game_year
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
    list_id = await conn.fetchval('''
        UPDATE Lists 
        SET list_name = $1, list_description = $2, is_private = $3 
        WHERE list_name = $4 AND list_creator = $5 
        RETURNING list_id
    ''', new_list.name, new_list.description, new_list.is_private, old_list_name, user_id)

    full_row = await conn.fetchrow('''
        SELECT l.list_name, l.list_description, u.username AS list_creator,
                l.is_private, l.created_at, COUNT(sl.user_a) AS list_saves
        FROM Lists l
        JOIN Users u ON u.user_id = l.list_creator
        LEFT JOIN SavedLists sl ON sl.list = l.list_id
        WHERE l.list_id = $1
        GROUP BY l.list_name, l.list_description, u.username, l.is_private, l.created_at
    ''', list_id)

    games = await conn.fetch('''
        SELECT g.game_id, g.game_name, g.game_picture, g.game_year,
                COUNT(r.liked) FILTER (WHERE r.liked = true) AS like_count,
                COALESCE(ROUND(AVG(r.rating_num) FILTER (WHERE r.is_private = false)::numeric, 2), -1) AS gamerboxd_rating
        FROM Games g
        JOIN ListContent lc ON lc.game = g.game_id
        LEFT JOIN Reviews r ON r.game = g.game_id
        WHERE lc.list = $1
        GROUP BY g.game_id, g.game_name, g.game_picture, g.game_year
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

    updated_list = ListFull(
        name=full_row["list_name"],
        description=full_row["list_description"],
        creator=full_row["list_creator"],
        is_private=full_row["is_private"],
        created_at=fix_date(full_row["created_at"]),
        list_saves=full_row["list_saves"],
        games=games_list
    )
    return updated_list

