import asyncpg
import os
from dotenv import load_dotenv


def set_dsn():

    load_dotenv()

    user = os.getenv("db_username")
    password = os.getenv("db_password")
    port = os.getenv("db_port")

    is_testing = int(os.getenv("testing"))

    if is_testing:
        name = os.getenv("db_name_test")
        host = "localhost"

    else:
        name = os.getenv("db_name")
        host = os.getenv("db_host")

    if any(val is None for val in (user, password, port, host, name)):
        raise ValueError("Campo faltando no .env")

    dsn = f'postgresql://{user}:{password}@{host}:{port}/{name}'
    print(dsn)
    return dsn


async def create_pool():

    dsn = set_dsn()
    return await asyncpg.create_pool(
        dsn = dsn, 
        min_size = 5,
        max_size = 15,
        max_inactive_connection_lifetime = 300,
    )




