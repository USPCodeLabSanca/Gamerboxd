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
