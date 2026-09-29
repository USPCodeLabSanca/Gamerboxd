from .data import DB_update_list_updated_at
from models.schemas.list import *
from utils.utils import db_query
from utils.helper import fix_date


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
async def DB_read_user_saved_lists(conn, user_id: str):
    """Lê as listas salvas por um usuário"""

    rows = await conn.fetch('''
        SELECT l.name, l.description, u.username AS creator, l.is_private, l.created_at,
        COUNT(sl2.usr) AS saves
        FROM SavedLists sl
        JOIN Lists l ON l.id = sl.list
        JOIN Users u ON u.id = l.creator
        LEFT JOIN SavedLists sl2 ON sl2.list = sl.list
        WHERE sl.usr = $1
        GROUP BY l.name, l.description, u.username, l.is_private, l.created_at, l.updated_at
        ORDER BY l.updated_at DESC
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

