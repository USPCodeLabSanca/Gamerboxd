from asyncpg import PostgresError

TABLES = {
    "Users":[
        ''' 
            CREATE TABLE IF NOT EXISTS Users (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(25) UNIQUE NOT NULL,
                email VARCHAR(256) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                bio VARCHAR(290) DEFAULT NULL,
                is_verified BOOL NOT NULL DEFAULT false,
                pfp TEXT DEFAULT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )   
        '''
    ],

    "Follows":[
        ''' 
            CREATE TABLE IF NOT EXISTS Follows (
                follower VARCHAR(36) REFERENCES Users(id) ON DELETE CASCADE,
                followed VARCHAR(36) REFERENCES Users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ DEFAULT NOW(),

                PRIMARY KEY (follower, followed)
            )
        ''',

        '''CREATE INDEX idx_follows_created_at_follower_desc ON Follows (created_at DESC, follower DESC)''',

        '''CREATE INDEX idx_follows_created_at_followed_desc ON Follows (created_at DESC, followed DESC)''',

        '''CREATE INDEX idx_follows_created_at_follower_asc ON Follows (created_at ASC, follower ASC)''',

        '''CREATE INDEX idx_follows_created_at_followed_asc ON Follows (created_at ASC, followed ASC)''',
    ],

    "Blocks":[
        ''' 
            CREATE TABLE IF NOT EXISTS Blocks (
                blocker VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
                blocked VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                        
                PRIMARY KEY (blocker, blocked)
            )
        '''
    ],

    "Games":[
        ''' 
            CREATE TABLE IF NOT EXISTS Games (
                id INTEGER PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                picture TEXT,
                year INTEGER
            )
        '''
    ],
    

    "Tags":[
        ''' 
            CREATE TABLE IF NOT EXISTS Tags (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name VARCHAR(20) NOT NULL,
                type VARCHAR(20)
            )
        '''
    ],

    "UserTags":[
        ''' 
            CREATE TABLE IF NOT EXISTS UserTags (
                usr VARCHAR(36) REFERENCES Users(id) ON DELETE CASCADE,
                tag INTEGER REFERENCES Tags(id) ON DELETE CASCADE,
                        
                PRIMARY KEY(usr, tag)
            )
        '''
    ],

    "Lists":[
        '''
            CREATE TABLE IF NOT EXISTS Lists (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                description VARCHAR(310) DEFAULT NULL,
                creator VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
                is_private BOOL NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                            
                UNIQUE (name, creator)
            )
        '''
    ],

    "ListContent":[
        '''
            CREATE TABLE IF NOT EXISTS ListContent (
                list VARCHAR(36) NOT NULL REFERENCES Lists(id) ON DELETE CASCADE,
                game INTEGER NOT NULL REFERENCES Games(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ DEFAULT NOW(),

                PRIMARY KEY(list, game) 
            )
        '''
    ],

    "SavedLists": [
        '''
        CREATE TABLE IF NOT EXISTS SavedLists (
            usr VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            list VARCHAR(36) NOT NULL REFERENCES Lists(id) ON DELETE CASCADE,

            PRIMARY KEY(usr, list)
        )
        '''
    ],

    "Reviews":[
        '''
            CREATE TABLE IF NOT EXISTS Reviews (
                id VARCHAR(36) PRIMARY KEY,
                reviewer VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
                game INTEGER NOT NULL REFERENCES Games(id) ON DELETE NO ACTION,
                rating_num FLOAT NOT NULL,
                rating_text VARCHAR(301) DEFAULT NULL,
                is_private BOOL DEFAULT false,
                time_played FLOAT DEFAULT NULL,
                liked BOOL DEFAULT NULL,
                completed BOOL NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                            
                UNIQUE (reviewer, game)
            )
        '''
    ],

    "ReviewTags":[
        '''
            CREATE TABLE IF NOT EXISTS ReviewTags (
                review VARCHAR(36) REFERENCES Reviews(id) ON DELETE CASCADE,
                tag INTEGER REFERENCES Tags(id) ON DELETE CASCADE,
                            
                PRIMARY KEY (review, tag)
            )
        '''
    ],

    "ReviewLikes":[
        '''
            CREATE TABLE IF NOT EXISTS ReviewLikes (
                usr VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
                review VARCHAR(36) NOT NULL REFERENCES Reviews(id) ON DELETE CASCADE,

                PRIMARY KEY(usr, review)
            )
        '''
    ],
}

async def create_tables(conn):
    try:
        async with conn.transaction():
            for key, value in TABLES.items():
                await conn.execute(v for v in value)

    except PostgresError as e:
        raise RuntimeError(e)
