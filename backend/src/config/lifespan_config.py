import asyncpg
import aiohttp
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
import os

from models import create_tables

class LifespanConfig():

    def set_auth(self):
    
        load_dotenv()

        self.vm_user = os.getenv("SERVER_USERNAME")
        self.vm_pass = os.getenv("SERVER_PASS")

        self.db_user = os.getenv("DB_USERNAME")
        self.db_pass = os.getenv("DB_PASS")

        self.port = os.getenv("DB_PORT")

        self.is_testing = int(os.getenv("TESTING"))
        
        self.wipe_bd = int(os.getenv("WIPE_DB"))

        if self.is_testing:
            self.db_name = os.getenv("DB_NAME_TEST")
            self.host = 'localhost'

        else:
            self.db_name = os.getenv("DB_NAME")
            self.host = os.getenv("DB_HOST")
            
        self.jwt_key = os.getenv("SECRET_KEY_JWT")
        self.rawg_key = os.getenv("RAWG_KEY")

        if any(val is None for val in (self.vm_user, self.vm_pass, self.db_user, self.db_pass, self.db_name, self.host, self.port, self.jwt_key, self.rawg_key)):
            raise ValueError("Campo faltando no .env!")
        
    def dsn(self):
        return f'postgresql://{self.db_user}:{self.db_pass}@{self.host}:{self.port}/{self.db_name}'

    async def conn(self):
        conn = None
  
        try:
            conn = await asyncpg.connect(
                user=self.vm_user, 
                password=self.vm_pass, 
                host=self.host,
                port=self.port
            )

            return conn

        except asyncpg.PostgresError as e:
            # Se der erro, retorna a falha
            raise RuntimeError(str(e))


    async def create_database(self):
        conn = None
        conn = await self.conn()
        
        try:
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
            # Se der erro, retorna a falha
            raise RuntimeError(str(e))

        finally:
            if conn is not None:
                await conn.close()
    

    async def create_internal_pool(self):
        try:
            pool = await asyncpg.create_pool(
                dsn = self.dsn(), 
                min_size = 5,
                max_size = 15,
                max_inactive_connection_lifetime = 300,
            )
            return pool
        
        except asyncpg.PostgresError as e:
            raise RuntimeError(str(e))
             
    async def create_external_pool(self):
        try:
            client_session = aiohttp.ClientSession()
            return client_session

        except Exception as e:
            raise RuntimeError(str(e))

    @asynccontextmanager
    async def __call__(self, app: FastAPI):

        self.set_auth()

        await self.create_database()
        app.state.internal_pool = await self.create_internal_pool()
        app.state.external_pool = await self.create_external_pool()
        app.state.jwt_key = self.jwt_key
        app.state.rawg_key = self.rawg_key

        async with app.state.internal_pool.acquire() as conn:
            await create_tables(conn)

        yield

        await app.state.internal_pool.close()
        await app.state.external_pool.close()

        if self.is_testing and self.wipe_bd:
            conn = None
            try:
                conn = await self.conn()

                await conn.execute(f"DROP DATABASE IF EXISTS {self.db_name} WITH (FORCE)")               

            finally:
                if conn is not None:
                    await conn.close()


