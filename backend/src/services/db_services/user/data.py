from uuid import uuid4

from ....models.schemas.user import UserNew, UserOut, UserEdit, UserDetails
from ....utils.utils import db_query, fix_date
from ....utils import pagination as pag

@db_query
async def DB_create_user(conn, user: UserNew):
    user_id = str(uuid4())
    await conn.execute('''
        INSERT INTO Users(id, username, email, password)
        VALUES($1, $2, $3, $4)
    ''', user_id, user.username, user.email, user.password)
    
    return user_id


@db_query
async def DB_delete_user(conn, user_id: str):
    await conn.execute('''
        DELETE FROM Users
        WHERE id = $1
    ''', user_id)


@db_query
async def DB_read_user_column(conn, column: str, user_id: str = None, email: str = None, username: str = None):
    if not any([x is not None for x in (username, user_id, email)]):
        raise TypeError("username, email e id não podem estar todos vazios")

    column_result = None

    if (user_id) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE id = $1", user_id)

    if (email) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE email = $1", email)

    if (username) and (column_result is None):
        column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE username = $1", username)
    
    return column_result


@db_query
async def DB_read_user_out(conn, user_id: str):
    row = await conn.fetchrow('''
        SELECT username, pfp, bio, banner, created_at
        FROM Users
        WHERE id = $1
    ''', user_id)

    if row is None:
        return None

    user = UserOut(
        user_id=user_id,
        username=row["username"],
        pfp=row["pfp"],
        bio=row["bio"],
        created_at=fix_date(row["created_at"]),
        banner=row["banner"]
    )

    return user


@db_query
async def DB_update_user(conn, user: UserEdit, user_id: str):
    await conn.execute('''
        UPDATE Users 
        SET username = $1, email = $2, bio = $3 , pfp = $4, banner = $5
        WHERE id = $6
    ''', user.username, user.email, user.bio, user.pfp, user.banner, user_id)

    return user


@db_query
async def DB_read_users_page(conn, user_id: str, page_query: pag.PageQuery):
    """Lê uma página de usuários"""

    async with conn.transaction():

        clauses = pag.PageClauses(
            basic_conditions=[("u.id IS DISTINCT FROM $1", user_id)],
            table_alias="u",
            col2="id",
            search_col="u.username"
        )

        # Conta quantos usuários correspondem a busca
        where, order_by, cursor_cols, params = pag.build_where(clauses, page_query, True)
        total_suggestions = await conn.fetchval(f'''
            SELECT COUNT(*)
            FROM Users u
            WHERE {where}
        ''', *params)

        # Pega uma página de usuários
        where, order_by, cursor_cols, params = pag.build_where(clauses, page_query, False)
        rows = await conn.fetch(f'''
            SELECT u.id, u.username, u.pfp,
            (SELECT COUNT(*) FROM Lists l WHERE l.creator = u.id) AS list_count,
            (SELECT COUNT(*) FROM Reviews r WHERE r.reviewer = u.id) AS review_count,
            (SELECT COUNT(*) FROM Reviews r WHERE r.reviewer = u.id AND r.liked = True) AS liked_count,
            (SELECT COUNT(*) FROM Follows fr WHERE fr.follower = u.id) AS followed_count,
            (SELECT COUNT(*) FROM Follows fd WHERE fd.followed = u.id) AS follower_count,
            {cursor_cols}
            FROM Users u
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ${len(params)}
        ''', *params)
    
        has_more = len(rows) > page_query.page_size
        rows = list(rows[:page_query.page_size])
    
        suggestions = [
            UserDetails(
                user_id=r["id"], 
                username=r["username"],
                pfp=r["pfp"],
                reviews=r["review_count"],
                lists=r["list_count"],
                liked=r["liked_count"],
                followeds=r["followed_count"],
                followers=r["follower_count"]
            ) for r in rows
        ]

        return pag.PageResult(
            total=total_suggestions,
            page_len=len(rows),
            content=suggestions,
            current_url=page_query.cursor,
            next_url=pag.encode_tuple_to_cursor((rows[-1]["main_col"], rows[-1]["other_col"])) if has_more else None
        )

