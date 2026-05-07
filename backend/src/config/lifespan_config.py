import asyncpg
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import os

from config.auth_config import get_secret_key
from models.tables import *
from utils.db import DB_Result


class LifespanConfig():

    def set_auth(self):
    
        load_dotenv()

        self.vm_user = os.getenv("SERVER_USERNAME")
        self.vm_pass = os.getenv("SERVER_PASS")

        self.db_user = os.getenv("DB_USERNAME")
        self.db_pass = os.getenv("DB_PASS")

        self.port = os.getenv("DB_PORT")

        is_testing = int(os.getenv("TESTING"))

        if is_testing:
            self.db_name = os.getenv("DB_NAME_TEST")
            self.host = 'localhost'

        else:
            self.db_name = os.getenv("DB_NAME")
            self.host = os.getenv("DB_HOST")

        if any(val is None for val in (self.vm_user, self.vm_pass, self.db_user, self.db_pass, self.db_name, self.host, self.port)):
            raise ValueError("Campo faltando no .env!")
        
    def dsn(self):
        return f'postgresql://{self.db_user}:{self.db_pass}@{self.host}:{self.port}/{self.db_name}'

    async def create_database(self):


        try:
            conn = await asyncpg.connect(
                user=self.vm_user, 
                password=self.vm_pass, 
                host=self.host,
                port=self.port
            )

            # Cria o usuário que vai fazer as operações no servidor, se ele já não existir
            role_exists = await conn.fetchval(
                "SELECT 1 FROM pg_roles WHERE rolname = $1", self.db_user
            )

            if not role_exists: 
                query = f"""
                    CREATE ROLE {self.db_user} WITH
                        LOGIN
                        SUPERUSER
                        CREATEDB
                        CREATEROLE
                        INHERIT
                        NOREPLICATION
                        NOBYPASSRLS
                        CONNECTION LIMIT -1
                        PASSWORD '{self.db_pass}';
                    """
                
                await conn.execute(query)

            # Cria o banco de dados para inserirmos as tabelas
            db_exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", self.db_name
            )

            if not db_exists:
                query = f"""
                    CREATE DATABASE {self.db_name}
                        WITH
                        OWNER = {self.db_user}
                        ENCODING = 'UTF8'
                        LOCALE_PROVIDER = 'libc'
                        CONNECTION LIMIT = 30
                        IS_TEMPLATE = False;
                """
                await conn.execute(query)

        except asyncpg.PostgresError as e:
            await conn.close()
            return DB_Result(success=False, message=f"{e}")
        
        else:
            await conn.close()
            return DB_Result(success=True, message="Criação de banco funcionou!")        


    async def create_pool(self):
        try:
            pool = await asyncpg.create_pool(
                dsn = self.dsn(), 
                min_size = 5,
                max_size = 15,
                max_inactive_connection_lifetime = 300,
            )

        except asyncpg.PostgresError as e:
            return DB_Result(success=False, message=f"{e}")
        
        else:
            return DB_Result(success=True, obj=pool, message="Criação do pool de conexões funcionou")

    @asynccontextmanager
    async def __call__(self, app: FastAPI):

        self.set_auth()

        table_creation = await self.create_database()
        if not table_creation.success:
            raise table_creation.error

        pool_creation = await self.create_pool()
        if pool_creation.success:
            app.state.pool = pool_creation.obj
        
        else:
            raise pool_creation.error

        app.state.jwt_key = get_secret_key()

        async with app.state.pool.acquire() as conn:
            await create_table_users(conn)
            await create_table_games(conn)
            await create_table_tags(conn)
            await create_table_reviews(conn)
            await create_table_lists(conn)
            
            await create_table_user_tags(conn)
            await create_table_follows(conn)
            await create_table_blocks(conn)

            await create_table_list_content(conn)
            await create_table_saved_lists(conn)
            
            await create_table_game_tags(conn)

            await create_table_review_likes(conn)
            await create_table_review_tags(conn)

        yield

        await app.state.pool.close()
