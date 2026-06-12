from uuid import uuid4

from models.schemas import *
from utils.db import DB_Result
from utils.helper import fix_date
from datetime import datetime


async def DB_create_user(conn, user: UserIn):

    user_id = str(uuid4())

    try:
        await conn.execute('''
            INSERT INTO Users(user_id, username, email, password)
            VALUES($1, $2, $3, $4)
        ''', user_id, user.username, user.email, user.password)
        
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


async def DB_create_list_game(conn, list_id, game_id):
    try:
        await conn.execute('''
            INSERT INTO ListContent(list, game) VALUES($1, $2)
        ''', list_id, game_id)

        return DB_Result(success=True, message="Game adicionado à lista com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_create_game(conn, game: Game):
    try:
        await conn.execute('''
            INSERT INTO Games(game_id, game_name, game_picture, game_year)
            VALUES($1, $2, $3, $4)
            ON CONFLICT (game_id)
            DO NOTHING;
        ''', game.game_id, game.name, game.picture, game.year)

        return DB_Result(success=True, message="Game adicionado ao db com sucesso!", obj = game.game_id)
    
    except Exception as e:
        return DB_Result(success=False, error=e)

async def DB_delete_follow(conn, user_follower: str, user_followed: str):
    try:
        await conn.execute('''DELETE FROM Follows WHERE user_a = $1 AND user_b = $2', 
         ''', user_follower, user_followed)
    
        return DB_Result(success=True, message="Novo desseguidor cadastrado com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)
    

async def DB_delete_list(conn, list_id: str, user_id: str):
    try:
        await conn.execute('''DELETE FROM Lists WHERE list = $1 AND user_a = $2', 
         ''', list_id, user_id)
        
        return DB_Result(success=True, message="Lista foi dessalvada com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_delete_list_save(conn, list_id: str, user_id: str):
    try:
        await conn.execute('''DELETE FROM SavedLists WHERE list = $1 AND user_a = $2''',
            list_id, user_id)
        
        return DB_Result(success=True, message="Lista deletada com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_delete_list_game(conn, list_id: str, game_id: int):
    try:
        await conn.execute('''DELETE FROM ListContent WHERE list = $1 AND game = $2''',
            list_id, game_id)
        
        return DB_Result(success=True, message="Game foi deletado da lista com sucesso!")
    
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
            ORDER BY f.created_at DESC
            """,
            user_id,
        )
        
        following_rows = await conn.fetch(
            """
            SELECT u.username, u.pfp
            FROM Follows f
            JOIN Users u ON u.user_id = f.user_b
            WHERE f.user_a = $1
            ORDER BY f.created_at DESC
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

        return DB_Result(success=True, message="Listas salvas pelo usuário encontrados!", obj=user_lists)
        
    except Exception as e:
        return DB_Result(success=False, error=e)    

async def DB_read_list_full(conn, list_id: str):
    try:
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
        return DB_Result(success=True, message="Lista encontrada com sucesso", obj=user_list)
    
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
        return DB_Result(success=True, message="Lista alterada com sucesso", obj=updated_list)
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_update_user(conn, user: UserEdit, user_id: str):

    try:
        await conn.execute('''
            UPDATE Users 
            SET username = $1, email = $2, bio = $3 , pfp = $4
            WHERE user_id = $5
        ''', user.username, user.email, user.bio, user.pfp, user_id)
        
    except Exception as e:
        return DB_Result(success=False, error=e)
    
    else:
        return DB_Result(success=True, message="Usuário atualizado com sucesso!")

    
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

async def DB_read_review_id(conn, username: str, game: int):
    try:

        review_id = await conn.fetchval('''
            SELECT r.review_id
            FROM Reviews r
            JOIN Users u ON u.user_id = r.reviewer
            WHERE u.username = $1
            AND r.game = $2
        ''', username, game)

        if review_id is None:
            return DB_Result(success = False, error="Review não existe!")
        
        return DB_Result(success = True, message="Review encontrada com sucesso!", obj = review_id)
    
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


async def DB_delete_user(conn, user_id: str):
    try:
        await conn.execute('''DELETE FROM Users WHERE user_id = $1
        ''', user_id)

        return DB_Result(success=True, message="Usuário deletado com sucesso!")

    except Exception as e:
        return DB_Result(success=False, error=e)

async def DB_create_block(conn, user_a: str, user_b: str):
    try:
        await conn.execute('''INSERT INTO Blocks(user_a, user_b) VALUES($1, $2)
        ''', user_a, user_b)

        return DB_Result(success=True, message = "Bloqueio criado com sucesso!")

    except Exception as e:
        return DB_Result(success=False, error=e)

async def DB_delete_block(conn, user_a: str, user_b: str):
    try:
        await conn.execute('''DELETE FROM Blocks WHERE user_a = $1 AND user_b = $2
        ''', user_a, user_b)

        return DB_Result(success=True, message = "Bloqueio deletado com sucesso!")
    
    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_game_likes(conn, game_id: int):
    try:
        like_count = await conn.fetchval('''
            SELECT COUNT(r.liked)
            FROM Reviews r 
            WHERE liked = true
            AND game = $1
        ''', game_id)

        return DB_Result(success=True, message="Likes do game encontrados com sucesso!", obj=like_count)

    except Exception as e:
        return DB_Result(success=False, error=e)


async def DB_read_game_avg_rating(conn, game_id: int):
    try:
        avg_rating = await conn.fetchval('''
            SELECT COALESCE(ROUND(AVG(r.rating_num)::numeric, 2), -1)
            FROM Games g
            JOIN Reviews r ON r.game = g.game_id
            WHERE g.game_id = $1
            AND r.is_private = false
        ''', game_id)

        return DB_Result(success=True, message="Média do game encontrada com sucesso!", obj=avg_rating)

    except Exception as e:
        return DB_Result(success=False, error=e)