from contextlib import asynccontextmanager
import fastapi
import asyncio

from config.db import create_pool, create_database
from models.tables import *


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):

    table_creation = await create_database()
    if not table_creation.success:
        raise table_creation.error

    pool_creation = await create_pool()
    if pool_creation.success:
        app.state.pool = pool_creation.obj
    
    else:
        raise pool_creation.error

    async with app.state.pool.acquire() as conn:
        await create_table_pfp(conn)
        await create_table_users(conn)
        await create_table_games(conn)
        await create_table_tags(conn)
        await create_table_reviews(conn)
        await create_table_lists(conn)
        
        await create_table_user_tags(conn)
        await create_table_follows(conn)
        await create_table_blocks(conn)

        await create_table_list_content(conn)
        await create_table_list_saved(conn)
        
        await create_table_game_tags(conn)

        await create_table_review_tags(conn)
        await create_table_review_likes(conn)

    yield

    await app.state.pool.close()

app = fastapi.FastAPI(lifespan = lifespan)

