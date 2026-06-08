from uuid import uuid4

from models.schemas import *
from utils.db import DB_Result
from utils.helper import fix_date
from datetime import datetime


async def DB_create_user(conn, user: UserIn):

    user_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Users(user_id, username, email, password, bio, pfp)
            VALUES($1, $2, $3, $4, $5, $6)
        ''', user_id, user.username, user.email, user.password, user.bio, user.pfp)
        
    except Exception as e:
        return DB_Result(success=False, error=e)
    
    else:
        return DB_Result(success=True, message="Usuário criado com sucesso!", obj=user_id)
    

async def DB_create_list(conn, new_list: List):
        
    list_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Lists(list_id, list_name, list_description, list_creator, is_private)
            VALUES($1, $2, $3, $4, $5)
        ''', list_id, new_list.name, new_list.description, new_list.creator, new_list.is_private)

        return DB_Result(success=True, message="Lista criada com sucesso!", obj=list_id)
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_create_user_tags(conn, user_id, tag_name):
    try:
        tag_id = await conn.fetchval('SELECT tag_id FROM Tags WHERE tag_name = $1', tag_name)

        await conn.execute('INSERT INTO UserTags (user_a, tag) VALUES($1, $2)', user_id, tag_id)

        return DB_Result(success=True, message="Tag do usuário salva com sucesso!")

    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_create_saved_list(conn, list_id: str, user_id: str):
    try:
        await conn.execute('''
            INSERT INTO SavedLists(user_a, list) VALUES($1, $2)
        ''', user_id, list_id)

        return DB_Result(success=True, message="Lista salva com sucesso!", obj=list_id)
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_create_follow(conn, user_follower: str, user_followed: str):
    try:
        await conn.execute('''
            INSERT INTO Follows(user_a, user_b) VALUES($1, $2)
        ''', user_follower, user_followed)

        return DB_Result(success=True, message="Novo seguidor cadastrado com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_create_list_save(conn, list_id: str, user_id: str):
    try: 
        await conn.execute('''
            INSERT INTO SavedLists(user_a, list) VALUES($1, $2)
        ''', user_id, list_id)

        return DB_Result(success=True, message="Lista salva com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_delete_follow(conn, user_follower: str, user_followed: str):
    try:
        await conn.execute('''DELETE FROM Follows WHERE user_a = $1 AND user_b = $2', 
         ''', user_follower, user_followed)
    
        return DB_Result(success=True, message="Novo desseguidor cadastrado com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_delete_list(conn, list_name: str, user_id: str):
    try:
        await conn.execute('''DELETE FROM Lists WHERE list = $1 AND user_a = $2', 
         ''', list_name, user_id)
        
        return DB_Result(success=True, message="Lista foi dessalvada com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_delete_list_save(conn, list_name: str, user_id: str):
    try:
        await conn.execute('''DELETE FROM SavedLists WHERE list = $1 AND user_a = $2''',
            list_name, user_id)
        
        return DB_Result(success=True, message="Lista deletada com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_user_column(conn, column: str, user_id: str = None, email: str = None, username: str = None):
    if username == None and user_id == None and email == None:
        raise TypeError("username, email e user_id não podem estar todos vazios")

    try:
        column_result = None

        if (user_id) and (column_result is None):
            column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE user_id = $1", user_id)

        if (email) and (column_result is None):
            column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE email = $1", email)

        if (username) and (column_result is None):
            column_result = await conn.fetchval(f"SELECT {column} FROM Users WHERE username = $1", username)
        
        if column_result is None:
            return DB_Result(
            success=True, 
            message="Usuário não existe",
            obj=None
        )
        
        return DB_Result(
            success=True, 
            message=f"{column} do usuário encontrado com sucesso!",
            obj=column_result
        )
        
    except Exception as e:
        return DB_Result(success=False, error = e)
    

async def DB_read_user_out(conn, user_id: str):
    
    try:
        row = await conn.fetchrow(
            """
            SELECT username, pfp, email, bio, created_at
            FROM Users
            WHERE user_id = $1
            """,
            user_id
        )

        if not row:
            raise ValueError("Não encontramos os dados do usuário")
 
        user = UserOut(
            username=row["username"],
            pfp=row["pfp"],
            email=row["email"],
            bio=row["bio"],
            created_at=fix_date(row["created_at"]),
        )

        return DB_Result(success=True, message="Dados do usuário encontrados!", obj=user)
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_user_follows(conn, user_id: str):
    
    try:
        follower_rows = await conn.fetch(
            """
            SELECT u.username, u.pfp
            FROM Follows f
            JOIN Users u ON u.user_id = f.user_a
            WHERE f.user_b = $1
            """,
            user_id,
        )
        following_rows = await conn.fetch(
            """
            SELECT u.username, u.pfp
            FROM Follows f
            JOIN Users u ON u.user_id = f.user_b
            WHERE f.user_a = $1
            """,
            user_id,
        )

        followers = [User(username=r["username"], pfp=r["pfp"]) for r in follower_rows]
        followings = [User(username=r["username"], pfp=r["pfp"]) for r in following_rows]
 
        user_follows = UserFollows(
            follower_count=len(followers),
            followers=followers,
            following_count=len(followings),
            followings=followings
        )
        
        return DB_Result(success=True, message="Relações do usuário encontradas", obj=user_follows)
        
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_user_list_id(conn, user_id: str, list_name: str, only_public: bool):
    
    try:
        if only_public:
            query = "SELECT list_id FROM Lists WHERE list_creator = $1 AND list_name = $2 AND is_private = false"

        else:
            query = "SELECT list_id FROM Lists WHERE list_creator = $1 AND list_name = $2"

        list_id = await conn.fetchval(query, user_id, list_name)

        return DB_Result(success=True, message="Lista encontrada", obj=list_id)
        
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_user_lists(conn, user_id: str):
    
    try:
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
            ListFull(
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

        return DB_Result(success=True, message="Listas salvas pelo usuário encontrados!", obj=user_lists)
        
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_user_tags(conn, user_id: str = None):

    try:
        rows = await conn.fetch(
            """
            SELECT t.tag_name
            FROM UserTags ut
            JOIN Tags t ON t.tag_id = ut.tag
            WHERE ut.user_a = $1
            """,
            user_id,
        )
 
        tags = [r["tag_name"] for r in rows]
        user_tags = UserTags(tag_count=len(tags), tags=tags)

        return DB_Result(success=True, message="Listas salvas pelo usuário encontrados!", obj=user_tags)
        
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_update_list(conn, new_list: ListIn, old_list_name: str, user_id: str):

    try:
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

        updated_list = ListFull(
            name=full_row["list_name"],
            description=full_row["list_description"],
            creator=full_row["list_creator"],
            is_private=full_row["is_private"],
            created_at=fix_date(full_row["created_at"]),
            list_saves=full_row["list_saves"],
        )
        return DB_Result(success=True, message="Lista alterada com sucesso", obj=updated_list)
    
    except Exception as e:
        return DB_Result(success=False, error=e)

async def DB_create_review(conn, review: ReviewIn, user_id: str):
    review_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Reviews(review_id, reviewer, game, rating_num, rating_text, is_private, time_played, liked, completed)
            VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)''', review_id, user_id, review.game, review.rating_num, 
            review.rating_text, review.is_private, review.time_played, review.liked, review.completed)

    except Exception as e:
        return DB_Result(success=False, error=e)
    
    else:
        return DB_Result(success=True, message="Review criada com sucesso!", obj=review)
    

async def DB_delete_review(conn, review_game: int, user_id: str):
    try:
        await conn.execute('''
            DELETE FROM Reviews 
            WHERE game = $1 AND reviewer = $2
            ''', review_game, user_id)
    
        return DB_Result(success = True, message = "Review deletada com sucesso!")

    except Exception as e:
        return DB_Result(success = False, error = e)
    

async def DB_update_review(conn, review: ReviewIn, old_review_game: int, user_id: str):
    
    try:
        time_now = datetime.now()

        await conn.execute('''
            UPDATE Reviews
            SET game = $1, rating_num = $2, rating_text = $3,
            is_private = $4, time_played = $5, liked = $6, completed = $7, last_update = $8 
            WHERE game = $9 AND reviewer = $10''', review.game, review.rating_num, review.rating_text,
            review.is_private, review.time_played, review.liked, review.completed, time_now,
            old_review_game, user_id)
    
        updated_list = ReviewOut(
            game = review.game,
            rating_num = review.rating_num,
            rating_text = review.rating_text,
            is_private = review.is_private,
            time_played = review.time_played,
            liked = review.liked,
            completed = review.completed,
            last_update = fix_date(time_now)
        )

        return DB_Result(success = True, message="Review alterada com sucesso!", obj = updated_list)
    
    except Exception as e:
        return DB_Result(success=False, error = e)
    
async def DB_read_user_game_review(conn, game: int, user_id: str):
    try:

        review = await conn.fetchrow('''
            SELECT * FROM Reviews WHERE game = $1 AND reviewer = $2 
            ''', game, user_id)

        return DB_Result(success=True, obj=review)
    
    except Exception as e:
        return DB_Result(success=False, error = e)

async def DB_read_review_like(conn, review_id: str, user_id: str):
    try:
        review_like = await conn.fetchrow('''
            SELECT * FROM ReviewLikes WHERE user_a = $1 AND review = $2 
            ''', user_id, review_id)

        return DB_Result(success=True, obj=review_like)
    
    except Exception as e:
        return DB_Result(success=False, error = e)
    
async def DB_read_count_likes(conn, review_id: str):
    try:
        likes = await conn.fetchval('''
            SELECT COUNT(*) FROM ReviewLikes WHERE review = $1 
            ''', review_id)

        return DB_Result(success=True, obj=likes)
    
    except Exception as e:
        return DB_Result(success=False, error = e)

async def DB_read_review(conn, username: str, game: int):
    try:

        review = await conn.fetchrow('''
            SELECT r.*
            FROM Reviews r
            JOIN Users u ON u.user_id = r.reviewer
            WHERE u.username = $1
            AND r.game = $2
        ''', username, game)

        if review is None:
            return DB_Result(success = False, error="Review não existe!")
        
        rows = await conn.fetch(
            """
            SELECT t.tag_name
            FROM ReviewTags rt
            JOIN Tags t ON t.tag_id = rt.tag
            WHERE rt.review = $1
            """,
            review["review_id"]
            )
        
        likes_result = await DB_read_count_likes(conn, review["review_id"])

        if not likes_result.success:
            raise Exception(str(likes_result.error))

        #game_name = await DB_read_game_name(conn, review.game)


        tags = [r["tag_name"] for r in rows]
        review_found = ReviewOutOne(
            username = username,
            rating_num = review["rating_num"],
            rating_text = review["rating_text"],
            time_played = review["time_played"],
            completed = review["completed"],
            tag_count = len(tags),
            tags = tags,
            likes_count = likes_result.obj,
            liked = review["liked"],
            game_name = "arrumarParaNomeJogo",
            created_at = fix_date(review["created_at"]),
            last_update = fix_date(review["last_update"])
        )
        
        return DB_Result(success = True, message="Review encontrada com sucesso!", obj = review_found)
    
    except Exception as e:
        return DB_Result(success=False, error = e)
    
async def DB_create_like_review(conn, like: ReviewLike):
    try:
        
        await conn.execute('''
            INSERT INTO ReviewLikes(user_a, review)
            VALUES($1, $2)''', like.user_a, like.review)

        return DB_Result(success=True, message="Like registrado com sucesso!")

    except Exception as e:
        return DB_Result(success=False, error = e)
    
async def DB_delete_like_review(conn, like: ReviewLike):
    try:
        
        await conn.execute('''
            DELETE FROM ReviewLikes 
            WHERE user_a = $1 AND review = $2
            ''', like.user_a, like.review)

        return DB_Result(success=True, message="Like removido com sucesso!")

    except Exception as e:
        return DB_Result(success=False, error = e)
    
async def DB_read_review_id(conn, username: str, game: int):
    try:

        review_id = await conn.fetchval('''
            SELECT r.review_id
            FROM Reviews r
            JOIN Users u ON u.user_id = r.reviewer
            WHERE u.username = $1
            AND r.game = $2
        ''', username, game)

        return DB_Result(success = True, message="Review encontrada com sucesso!", obj = review_id)
    
    except Exception as e:
        return DB_Result(success=False, error = e)
    

async def DB_read_limit_reviews(conn, username: str, limit: int):
    try:

        reviews_result = await conn.fetch('''
        SELECT r.* FROM Reviews r 
        JOIN Users u On u.user_id = r.reviewer 
        WHERE u.username = $1
        LIMIT $2''', username, limit)

        reviews_out = []
        for r in reviews_result:
            #game_name = await DB_read_game_name(conn, r["game"])
            likes_result = await DB_read_count_likes(conn, r["review_id"])

            if not likes_result.success:
                raise Exception(str(likes_result.error))

            reviews_out.append(
                ReviewOut(
                    rating_num = r["rating_num"],
                    rating_text = r["rating_text"],
                    likes_count = likes_result.obj,
                    liked = r["liked"],
                    game_name = "arrumarParaNomeJogo",
                    created_at = fix_date(r["created_at"])
                )
            )
        
        return DB_Result(success = True, message="Review(s) encontrada(s) com sucesso!", obj = reviews_out)

    except Exception as e:
        return DB_Result(success=False, error = e)