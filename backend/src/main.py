from contextlib import asynccontextmanager
import fastapi
import asyncio

from config.db import create_pool
from models.tables import *


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    app.state.pool = await create_pool()

    async with app.state.pool.acquire() as conn:
        await create_table_pfp(conn)
        await create_table_users(conn)
        await create_table_games(conn)
        await create_table_follows(conn)

        # Outras criações de tabelas vão aqui

        # Obs: Muito cuidado com a ordem de criação! Se a tabela A tem uma
        # coluna X que depende de uma coluna Y na tabela B,chame a função
        # create_table_B antes de create_table_A

        # Fim das criações de tabelas

    yield

    await app.state.pool.close()

app = fastapi.FastAPI(lifespan = lifespan)

