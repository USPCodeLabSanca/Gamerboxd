from asyncpg import PostgresError

TABLES = {
    "Users":
    ''' 
        CREATE TABLE IF NOT EXISTS Users (
            user_id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(25) UNIQUE NOT NULL,
            email VARCHAR(256) UNIQUE NOT NULL,
            password VARCHAR(256) NOT NULL,
            bio VARCHAR(280) DEFAULT NULL,
            is_verified BOOL NOT NULL DEFAULT false,
            pfp TEXT DEFAULT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
            )   
    ''',

    "Follows":
    '''
        CREATE TABLE IF NOT EXISTS Follows (
            user_a VARCHAR(36) REFERENCES Users(user_id) ON DELETE CASCADE,
            user_b VARCHAR(36) REFERENCES Users(user_id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT now(),

            PRIMARY KEY (user_a, user_b)
            )
    ''',

    "Blocks":
    '''
        CREATE TABLE IF NOT EXISTS Blocks (
            user_a VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
            user_b VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
                    
            PRIMARY KEY (user_a, user_b)
            )
    ''',

    "Games":
    '''
        CREATE TABLE IF NOT EXISTS Games (
            game_id INTEGER PRIMARY KEY,
            game_name VARCHAR(50) NOT NULL,
            game_picture TEXT,
            game_year INTEGER
            )
    ''',

    "Tags":
    '''
        CREATE TABLE IF NOT EXISTS Tags (
            tag_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            tag_name VARCHAR(36) UNIQUE NOT NULL 
        )
    ''',

    "UserTags":
    '''
        CREATE TABLE IF NOT EXISTS UserTags (
            user_a VARCHAR(36) REFERENCES Users(user_id) ON DELETE CASCADE,
            tag INTEGER REFERENCES Tags(tag_id) ON DELETE CASCADE,
                    
            PRIMARY KEY(user_a, tag)
        )
    ''',

    "GameTags":
    '''
        CREATE TABLE IF NOT EXISTS GameTags (
            tag INTEGER REFERENCES Tags(tag_id) ON DELETE CASCADE,
            game INTEGER REFERENCES Games(game_id) ON DELETE CASCADE,

            PRIMARY KEY (tag, game)
        )
    ''',

    "Lists":
    '''
        CREATE TABLE IF NOT EXISTS Lists (
            list_id VARCHAR(36) PRIMARY KEY,
            list_name VARCHAR(50) NOT NULL,
            list_description VARCHAR(310) DEFAULT NULL,
            list_creator VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
            is_private BOOL NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now(),
                           
            UNIQUE (list_name, list_creator)
        )
    ''',

    "ListContent":
    '''
        CREATE TABLE IF NOT EXISTS ListContent (
            list VARCHAR(36) NOT NULL REFERENCES Lists(list_id) ON DELETE CASCADE,
            game INTEGER NOT NULL REFERENCES Games(game_id) ON DELETE CASCADE,

            PRIMARY KEY(list, game) 
        )
    ''',

    "SavedLists":
    '''
        CREATE TABLE IF NOT EXISTS SavedLists (
            user_a VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
            list VARCHAR(36) NOT NULL REFERENCES Lists(list_id) ON DELETE CASCADE,

            PRIMARY KEY(user_a, list)
        )
    ''',

    "Reviews":
    '''
        CREATE TABLE IF NOT EXISTS Reviews (
            review_id VARCHAR(36) PRIMARY KEY,
            reviewer VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
            game INTEGER NOT NULL,
            rating_num FLOAT NOT NULL,
            rating_text VARCHAR(300) DEFAULT NULL,
            is_private BOOL DEFAULT false,
            time_played FLOAT DEFAULT NULL,
            liked BOOL DEFAULT NULL,
            completed BOOL NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now(),
            last_update TIMESTAMPTZ DEFAULT now(),
                        
            UNIQUE (reviewer, game)
        )
    ''',

    "ReviewTags":
    '''
        CREATE TABLE IF NOT EXISTS ReviewTags (
            review VARCHAR(36) REFERENCES Reviews(review_id) ON DELETE CASCADE,
            tag INTEGER REFERENCES Tags(tag_id) ON DELETE CASCADE,
                           
            PRIMARY KEY (review, tag)
        )
    ''',

    "ReviewLikes":
    '''
        CREATE TABLE IF NOT EXISTS ReviewLikes (
            user_a VARCHAR(36) NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
            review VARCHAR(36) NOT NULL REFERENCES Reviews(review_id) ON DELETE CASCADE,

            PRIMARY KEY(user_a, review)
        )
    ''',
}

async def create_tables(conn):
    try:
        async with conn.transaction():
            for key, value in TABLES.items():
                await conn.execute(value)

    except PostgresError as e:
        raise RuntimeError(e)
