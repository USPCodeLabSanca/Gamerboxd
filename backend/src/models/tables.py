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
   
async def create_table_tags(conn):
    try:
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS Tags(
                    tag_id INTEGER GENERATED ALWAYS AS IDENTITY,
                    tag_name VARCHAR(36) UNIQUE NOT NULL 
                )
            ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)
    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")
        
async def create_table_user_tags(conn):
    try:
        await conn.execute('''
                CREATE TABLE IF NOT EXISTS UserTags(
                    user VARCHAR(36) REFERENCES Users(user_id) ON DELETE CASCADE
                    tag INTEGER REFERENCES Tags(tag_id) ON DELETE CASCADE
                           
                    PRIMARY KEY(user, tag)
                )
            ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)
    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")
    
async def create_table_game_tags(conn):
    try:
        await conn.execute('''
                CREATE TABLE IF NOT EXIST GameTags(
                    tag INTEGER REFERENCES Tags(tag_id) ON DELETE CASCADE
                    game INTEGER REFERENCES Games(game_id) ON DELETE CASCADE

                    PRIMARY KEY (tag, game)
                )
            ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)
    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")
    
async def create_table_review_tags(conn):
    try:
        await conn.execute('''
                CREATE TABLE IF NOT EXIST ReviewTags(
                    review VARCHAR(36) REFERENCES Reviews(review_id) ON DELETE CASCADE
                    tag INTEGER REFERENCES Tags(tag_id) ON DELETE CASCADE
                           
                    PRIMARY KEY (review, tag)
                )
            ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)
    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")
    
async def create_table_blocks(conn):
    try:
        await conn.execute('''
                CREATE IF NOT EXIST Blocks(
                    user_a REFERENCES Users(user_id) ON CASCADE DELETE
                    user_b REFERENCES Users(user_id) ON CASCADE DELETE
                    
                    PRIMARY KEY (user_a, user_b)
                )
            ''')
    except PostgresError as e:
        return DB_Result(success = False, message = e)
    else:
        return DB_Result(success = True, message = "Criação da tabela funcionou!")