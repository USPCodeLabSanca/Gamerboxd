import asyncpg
from dataclasses import dataclass
import os
from dotenv import load_dotenv

from utils.db import DB_Result

@dataclass
class Auth():
    vm_user: str
    vm_pass: str
    db_user:str
    db_pass:str
    db_name: str
    host: str
    port: int

def set_auth():
    
    load_dotenv()

    vm_user = os.getenv("SERVER_USERNAME")
    vm_pass=os.getenv("SERVER_PASS")

    db_user = os.getenv("DB_USERNAME")
    db_pass = os.getenv("DB_PASS")

    port = os.getenv("DB_PORT")

    is_testing = int(os.getenv("TESTING"))

    if is_testing:
        db_name = os.getenv("DB_NAME_TEST")
        host = 'localhost'

    else:
        db_name = os.getenv("DB_NAME")
        host = os.getenv("DB_HOST")

    if any(val is None for val in (vm_user, vm_pass, db_user, db_pass, db_name, host, port)):
        raise ValueError("Campo faltando no .env!")
    
    return Auth(vm_user, vm_pass, db_user, db_pass, db_name, host, port)


def set_dsn(auth: Auth):
    dsn = f'postgresql://{auth.db_user}:{auth.db_pass}@{auth.host}:{auth.port}/{auth.db_name}'
    # print(dsn)
    return dsn


async def create_database():

    auth = set_auth()

    try:
        conn = await asyncpg.connect(
            user=auth.vm_user, 
            password=auth.vm_pass, 
            host=auth.host,
            port=auth.port
        )

        # Cria o usuário que vai fazer as operações no servidor, se ele não existir
        role_exists = await conn.fetchval(
            "SELECT 1 FROM pg_roles WHERE rolname = $1", auth.db_user
        )

        if not role_exists: 
            query = f"""
                CREATE ROLE {auth.db_user} WITH
                    LOGIN
                    SUPERUSER
                    CREATEDB
                    CREATEROLE
                    INHERIT
                    NOREPLICATION
                    NOBYPASSRLS
                    CONNECTION LIMIT -1
                    PASSWORD '{auth.db_pass}';
                """
            
            await conn.execute(query)

        # Cria o banco de dados para inserirmos as tabelas
        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", auth.db_name
        )

        if not db_exists:
            query = f"""
                CREATE DATABASE {auth.db_name}
                    WITH
                    OWNER = {auth.db_user}
                    ENCODING = 'UTF8'
                    LOCALE_PROVIDER = 'libc'
                    CONNECTION LIMIT = 30
                    IS_TEMPLATE = False;
            """
            await conn.execute(query)

    except asyncpg.PostgresError as e:
        await conn.close()
        return DB_Result(success=False, error=e)
    
    else:
        await conn.close()
        return DB_Result(success=True, message="Criação de banco funcionou!")        


async def create_pool():
    auth = set_auth()
    dsn = set_dsn(auth)

    try:
        pool = await asyncpg.create_pool(
            dsn = dsn, 
            min_size = 5,
            max_size = 15,
            max_inactive_connection_lifetime = 300,
        )

    except asyncpg.PostgresError as e:
        return DB_Result(success=False, error=e)
    
    else:
        return DB_Result(success=True, obj=pool, message="Criação do pool de conexões funcionou")