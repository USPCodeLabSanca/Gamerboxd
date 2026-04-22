from asyncpg import PostgresError
from utils.db import DB_Result


async def create_table_pfp(conn):
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS ProfilePictures (
                pfp_id SERIAL PRIMARY KEY,
                pfp TEXT UNIQUE NOT NULL
            )
        ''')

    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")
    

async def create_table_users(conn):
    try:
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    user_id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(25) UNIQUE NOT NULL,
                    email VARCHAR(256) UNIQUE NOT NULL,
                    password VARCHAR(256) NOT NULL,
                    bio VARCHAR(280) DEFAULT NULL,
                    is_verified BOOL NOT NULL,
                    pfp INTEGER DEFAULT NULL REFERENCES ProfilePictures(pfp_id) ON DELETE SET DEFAULT,
                    created_at TIMESTAMPTZ DEFAULT now()
                )
            ''')

    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")
    

async def create_table_follows(conn):
    try:
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS follows (
                    user_a VARCHAR(36) REFERENCES Users(user_id) ON DELETE CASCADE,
                    user_b VARCHAR(36) REFERENCES Users(user_id) ON DELETE CASCADE,

                    PRIMARY KEY (user_a, user_b)
                )
            ''')

    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")

async def create_table_games(conn):
    try:
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS Games (
                    game_id INTEGER PRIMARY KEY,
                    game_name VARCHAR(30) NOT NULL,
                    game_picture TEXT
                )
            ''')

    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")


async def create_table_lists(conn):
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS Lists (
                list_id SERIAL PRIMARY KEY,
                list_name VARCHAR(50) NOT NULL,
                list_description VARCHAR(300),
                list_creator VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                is_private BOOL NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now(),
                last_update TIMESTAMPTZ DEFAULT now()
            )
        ''')
        
    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")

async def create_table_list_content(conn):
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS list_content (
                list INTEGER NOT NULL REFERENCES Lists(list_id) ON DELETE CASCADE,
                game INTEGER NOT NULL REFERENCES Games(game_id) ON DELETE CASCADE,

                PRIMARY KEY(list, game) 
            )
        ''')
    
    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")

async def create_table_list_saved(conn):
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS list_saved (
                user VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                list INTEGER NOT NULL REFERENCES Lists(list_id) ON DELETE CASCADE,

                PRIMARY KEY(user, list)
            )
        ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")

async def create_table_reviews(conn):
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS Reviews (
                review_id SERIAL PRIMARY KEY,
                reviewer VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                game INTEGER NOT NULL REFERENCES Games(game_id) ON DELETE CASCADE,
                rating_num FLOAT NOT NULL,
                rating_text VARCHAR(300),
                is_private BOOL NOT NULL,
                time_played FLOAT NOT NULL,
                liked BOOL NOT NULL,
                completed BOOL NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now(),
                last_update TIMESTAMPTZ DEFAULT now()
            )
        ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")

async def create_table_review_likes(conn):
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS review_likes (
                user VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                review INTEGER NOT NULL REFERENCES Reviews(review_id) ON DELETE CASCADE,

                PRIMARY KEY(user, review)
            )
        ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)

    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")
