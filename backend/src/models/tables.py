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

        '''CREATE INDEX IF NOT EXISTS idx_followed_follower_created ON Follows (followed, follower DESC, created_at DESC)''',

        '''CREATE INDEX IF NOT EXISTS idx_follower_followed_created ON Follows (follower, followed DESC, created_at DESC);'''

    ],

    "Blocks":[
        ''' 
            CREATE TABLE IF NOT EXISTS Blocks (
                blocker VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
                blocked VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                        
                PRIMARY KEY (blocker, blocked)
            )
        ''',

        '''CREATE INDEX IF NOT EXISTS idx_blocker_blocked_created ON Blocks (blocker, blocked DESC, created_at DESC)'''
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
        ''',

        '''CREATE INDEX IF NOT EXISTS idx_creator_id_updated ON Lists (creator, id DESC, updated_at DESC)'''
    ],

    "ListContent":[
        '''
            CREATE TABLE IF NOT EXISTS ListContent (
                list VARCHAR(36) NOT NULL REFERENCES Lists(id) ON DELETE CASCADE,
                game INTEGER NOT NULL REFERENCES Games(id) ON DELETE CASCADE,
                created_at TIMESTAMPTZ DEFAULT NOW(),

                PRIMARY KEY(list, game) 
            )
        ''',

        '''CREATE INDEX IF NOT EXISTS idx_list_game_created ON ListContent (list, game DESC, created_at DESC)'''
    ],

    "SavedLists": [
        '''
        CREATE TABLE IF NOT EXISTS SavedLists (
            usr VARCHAR(36) NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
            list VARCHAR(36) NOT NULL REFERENCES Lists(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ DEFAULT NOW(),

            PRIMARY KEY(usr, list)
        )
        ''',

        '''CREATE INDEX IF NOT EXISTS idx_usr_list_created ON SavedLists (usr, list DESC, created_at DESC)''',

        '''CREATE INDEX IF NOT EXISTS idx_list_usr_created ON SavedLists (list, usr DESC, created_at DESC)'''
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
                for statement in value:
                    await conn.execute(statement)

    except PostgresError as e:
        raise RuntimeError(e)
